#! /usr/bin/env python3

import base64
import xml.dom.minidom

from cmdconfig import CmdConfig
from tbcwsfactory import TBCWSFactory
from xmlutils import xml_first_child_or_error, xml_set_node_value


def extract_params_available(params_template):
    ''' Generates a dictionary with all of the parameters the report exposes, their description and current value. '''
    params = dict()
    array_of_rpt_parameter_report_par = xml_first_child_or_error(params_template, 'ArrayOfRptParameterReportPar')
    for p in array_of_rpt_parameter_report_par.getElementsByTagName('RptParameterReportPar'):
        param_name = xml_first_child_or_error(p, 'ParamName').firstChild.nodeValue
        param_description = xml_first_child_or_error(p, 'Description').firstChild.nodeValue
        param_type = xml_first_child_or_error(xml_first_child_or_error(p, 'Type'), 'Data').firstChild.nodeValue
        param_value = None
        if (xml_first_child_or_error(p, 'Value').firstChild != None):
            param_value = xml_first_child_or_error(p, 'Value').firstChild.nodeValue
        param_visible = xml_first_child_or_error(p, 'Visible').firstChild.nodeValue
        params[param_name] = (param_value, param_type, param_visible, param_description, )

    return params


def print_params_available(params_available):
    ''' Pretty-print the params which the report exposes. '''
    for k, v in params_available.items():
        value = v[0]
        if (value == None):
            value = 'None'
        else:
            value = f'"{value}"'

        descr = ''
        if (v[3] != k):
            descr = f' (Long description = "{v[3]}")'

        visible = ''
        if (v[2].upper() == "FALSE"):
            visible = "(HIDDEN PARAMETER) "

        print (f'{visible}{k} ({v[1]}) = {value}{descr}')


def parse_params_supplied(raw_params):
    ''' Turns the supplied parameters into a dictionary. '''
    params = dict()

    if raw_params != None:
        for x in raw_params:
            s = x.split('=', maxsplit=1)
            if len(s) == 2:
                params[s[0]] = s[1]
            else:
                params[s[0]] = None

    return params


def fill_filter(filter_template, supplied_filter):
    ''' Fills the supplied filter in the corresponding XML tag. '''
    array_of_rpt_filter_report_par = xml_first_child_or_error(filter_template, 'ArrayOfRptFilterReportPar')
    rpt_filter_report_par = xml_first_child_or_error(array_of_rpt_filter_report_par, 'RptFilterReportPar')
    value = xml_first_child_or_error(rpt_filter_report_par, 'Value')
    xml_set_node_value(value, supplied_filter)


def fill_parameters(params_template, supplied_parameters):
    ''' Fills the supplied parameters in the corresponding XML tag. '''
    params = dict()
    # Makes a copy of all of the parameters which were supplied. This will be used to detect if the user supplied
    # an unknown parameter
    all_supplied_parameters = set(supplied_parameters.keys())

    array_of_rpt_parameter_report_par = xml_first_child_or_error(params_template, 'ArrayOfRptParameterReportPar')
    for p in array_of_rpt_parameter_report_par.getElementsByTagName('RptParameterReportPar'):
        param_name = xml_first_child_or_error(p, 'ParamName').firstChild.nodeValue
        param_value = xml_first_child_or_error(p, 'Value')

        if param_name in supplied_parameters:
            xml_set_node_value(param_value, supplied_parameters[param_name])
            if param_name in all_supplied_parameters:
                all_supplied_parameters.remove(param_name)

    if len(all_supplied_parameters) > 0:
        msg = 'The following parameters were supplied, but were not found on the list of parameters ' + \
              'accepted by the report: {}'
        raise Exception(msg.format(', '.join(all_supplied_parameters)))

    return params


if __name__ == '__main__':
    args = CmdConfig.get()

    codcoligada = args['codcoligada']
    idreport = args['idreport']

    tbcr = TBCWSFactory().get_ws_report

    # Fetches the parameters and filters available, but only if the user asked them to be
    # displayed or if the user supplied any of those for generating the report.
    filter_template_raw, params_template_raw = None, None
    filter_template, params_template = None, None
    filter_available, params_available = None, None

    if (args['filters'] != None or args['show_filters'] or args['show_raw_filters']
        or args['params'] != None or args['show_params'] or args['show_raw_params']):
        filter_template_raw, params_template_raw = tbcr().GetReportInfo(codcoligada, idreport)

        # Change both the filters and the parameters to a xml object
        if filter_template_raw != None:
            filter_template = xml.dom.minidom.parseString(filter_template_raw)

        if params_template_raw != None:
            params_template = xml.dom.minidom.parseString(params_template_raw)

        filter_available = ''
        params_available = extract_params_available(params_template)

    if (args['show_filters'] or args['show_raw_filters']
        or args['show_params'] or args['show_raw_params']):
        if args['show_filters']:
            print('Default filter string:')
            raise NotImplemented()

        if args['show_raw_filters']:
            print('Filters XML:')
            print(filter_template_raw)

        if args['show_params']:
            print('The report exposes the following parameters:')
            print_params_available(params_available)

        if (args['show_raw_params']):
            print('Parameters XML:')
            print(params_template_raw)

        # Exit after showing the items
        exit(0)

    # Fill in the filters and parameters objects
    fill_filter(filter_template, args['filters'])
    parsed_params = parse_params_supplied(args['params'])
    fill_parameters(params_template, parsed_params)

    print('Generating report...')
    guid_rel = tbcr().GenerateReport(codcoligada,
                                     idreport,
                                     filter_template.toxml(),
                                     params_template.toxml(),
                                     args.get('output'))
    print(f'   ... report ready. ID = {guid_rel}')

    print('Getting file size...')
    size = tbcr().GetGeneratedReportSize(guid_rel)
    print(f'   ... file size = {size} bytes')

    print('Downloading file...')
    arquivo_base64 = tbcr().GetFileChunk(guid_rel, 0, size)
    print('   ... file downloaded')

    print('Saving file to disk...')
    with open(args.get('output'), mode='wb') as f:
        f.write(base64.b64decode(arquivo_base64))
    print('   ... done')
