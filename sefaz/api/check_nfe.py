from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests_pkcs12 import Pkcs12Adapter

from ..models import Business

def check_nfe(business):
    PKCS12_CERT_PATH = business.certificate.path
    PKCS12_CERT_PASSWORD = business.password
    WSDL_URL = 'https://hom.nfe.fazenda.gov.br/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx'

    session = Session()
    session.mount('https://', Pkcs12Adapter(pkcs12_filename=PKCS12_CERT_PATH, pkcs12_password=PKCS12_CERT_PASSWORD))

    transport = Transport(session=session)
    client = Client(WSDL_URL, transport=transport)
    
    request_data = {
        'tpAmb': 2,  # Ambiente: 1 = Produção, 2 = Homologação
        'cnpj': business.cnpj,  # CNPJ da empresa
        'ultNSU': business.nsu  # Número Sequencial Único (NSU) do último documento obtido
    }

    # Chame o serviço da SEFAZ com os dados de requisição
    response = client.service.nfeDistDFeInteresse(request_data)
    return response