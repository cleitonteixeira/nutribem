from pynfe.processamento.comunicacao import ComunicacaoSefaz
from sefaz.models import Business
import xml.etree.ElementTree as etree

def check_nfe(business):

    certificado = business.certificate.path 
    senha = business.password
    uf = business.uf
    homologacao = False

    con = ComunicacaoSefaz(uf, certificado, senha, homologacao)
    # informar cnpj que deseja consultar (String) e nsu (inteiro) (por default se não informar nsu ele assumirá o valor 0, retornando as dos últimos 15 dias)
    xml = con.consulta_distribuicao(cnpj=business.cnpj, nsu=business.nsu)
    print(xml)
    print("########")
    print (xml.text)
    root = etree.fromstring(xml.text)
    doc_zip_elements = root.findall("docZip")
    doc_zip_contents = [element.text for element in doc_zip_elements]
    print("########")
    print(doc_zip_contents)
    return doc_zip_contents