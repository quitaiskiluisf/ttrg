#! /usr/bin/env python3

import base64
import fileinput

from cmdconfig import CmdConfig
from tbcwsfactory import TBCWSFactory


if __name__ == '__main__':
    args = CmdConfig.get()

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

    tbcr = TBCWSFactory().get_ws_report

    print(args)

    print('Generating report...')
    guid_rel = tbcr().GenerateReport(args.get('codcoligada'),
                                     args.get('idreport'),
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
