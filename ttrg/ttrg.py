#! /usr/bin/env python3

import base64
import fileinput
import xml.dom.minidom

from cmdconfig import CmdConfig
from tbcwsfactory import TBCWSFactory
from xmlutils import xml_first_child_or_error


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


if __name__ == '__main__':
    args = CmdConfig.get()

    codcoligada = args['codcoligada']
    idreport = args['idreport']

    tbcr = TBCWSFactory().get_ws_report

    # Fetches the parameters and filters available, but only if the user asked them to be
    # displayed.
    filter_template_raw, params_template_raw = None, None
    filter_template, params_template = None, None
    filter_available, params_available = None, None

    if (args['show_filters'] or args['show_raw_filters']
        or args['show_params'] or args['show_raw_params']):
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

    args['filters'] = f'''<?xml version="1.0" encoding="utf-16"?>
<ArrayOfRptFilterReportPar xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.totvs.com.br/RM/">
  <RptFilterReportPar>
    <BandName>rptReport1</BandName>
    <FiltersByTable />
    <MainFilter>true</MainFilter>
    <Value>{args['filters']}</Value>
  </RptFilterReportPar>
</ArrayOfRptFilterReportPar>'''

    args['params'] = ''.join(fileinput.input(files=args['params']))

    print('Generating report...')
    guid_rel = tbcr().GenerateReport(codcoligada,
                                     idreport,
                                     args.get('filters'),
                                     args.get('parameters'),
                                     args.get('output'))
    print('   ... report ready. ID = {}'.format(guid_rel))

    print('Getting file size...')
    tamanho = tbcr().GetGeneratedReportSize(guid_rel)
    print('   ... file size = {} bytes'.format(tamanho))

    print('Downloading file...')
    arquivo_base64 = tbcr().GetFileChunk(guid_rel, 0, tamanho)
    print('   ... file downloaded')

    print('Saving file to disk...')
    with open(args.get('output'), mode='wb') as f:
        f.write(base64.b64decode(arquivo_base64))
    print('   ... done')
