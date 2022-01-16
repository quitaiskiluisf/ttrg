
import zeep
from environmentconfig import EnvironmentConfig


class TBCWSFactory(object):
    ''' Builds ready-to-use zeep instances for connecting to the ERP system
        through TBC '''

    @classmethod
    def _get_transport_with_basic_auth(cls, username, password):
        ''' Returns a transport object (from zeep.transports), configured to use the supplied username and password
            through Basic Authentication. '''
        from requests import Session
        from requests.auth import HTTPBasicAuth
        from zeep.transports import Transport

        session = Session()
        session.auth = HTTPBasicAuth(username, password)
        return Transport(session=session)


    @classmethod
    def _get_ws_ref(cls, wsdl, service, port, username=None, password=None):
        ''' Returns a generic service reference.

            The service URL and the parameters are already set. '''

        client = None
        if (username != None or password != None):
            client = zeep.Client(wsdl, transport=cls._get_transport_with_basic_auth(username, password))
        else:
            client = zeep.Client(wsdl)

        return client.bind(service, port)


    @classmethod
    def get_ws_report(cls):
        ''' Returns a webservice instance for interacting with the wsReport object.

            More info: https://tdn.totvs.com/display/public/LRM/TBC+-+Web+Services+Reports '''

        url = EnvironmentConfig.get('URL')
        user = EnvironmentConfig.get('USERNAME')
        password = EnvironmentConfig.get('PASSWORD')

        return cls._get_ws_ref(url + '/wsReport/MEX?wsdl', 'wsReport', 'RM_IwsReport',
                               user, password)
