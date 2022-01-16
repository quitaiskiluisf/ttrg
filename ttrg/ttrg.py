#! /usr/bin/env python3

import base64
import fileinput

from cmdconfig import CmdConfig
from tbcwsfactory import TBCWSFactory


if __name__ == '__main__':
    args = CmdConfig.get()

    codcoligada = args['codcoligada']
    idreport = args['idreport']

    tbcr = TBCWSFactory().get_ws_report

    # Fetches the parameters and filters available, but only if the user asked them to be
    # displayed.
    filter_template_raw, params_template_raw = None, None

    if (args['show_raw_filters'] or args['show_raw_params']):
        filter_template_raw, params_template_raw = tbcr().GetReportInfo(codcoligada, idreport)

    if (args['show_raw_filters'] or args['show_raw_params']):
        if args['show_raw_filters']:
            print('Filters XML:')
            print(filter_template_raw)

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
