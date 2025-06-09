from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

def FindCalls():
    # Inicia o navegador
    driver = webdriver.Chrome(options=options)
    driver.get("https://s22.chatguru.app")

    # Aguarda a página carregar (ajuste conforme necessário)
    time.sleep(3)

    usuario = driver.find_element(By.ID, "email")  # Substitua pelo ID/caminho real
    usuario.send_keys("cleiton.santos@nutribemrefeicoes.com")

    # Localiza e preenche o campo de senha
    senha = driver.find_element(By.ID, "password")  # Substitua pelo ID/caminho real
    senha.send_keys("S4ntos#12")

    # Clica no botão de login
    botao_login = driver.find_element(By.CLASS_NAME, "FormButton")  # Substitua pelo seletor correto
    botao_login.click()

    # Aguarda a página após o login carregar
    time.sleep(3)

    todos_h5 = driver.find_elements(By.CLASS_NAME, "h5")

    # Percorre e imprime o texto de cada um
    for idx, h5 in enumerate(todos_h5, 1):
        print(f"H5 #{idx}: {h5.text}")

    # Encontra a tabela pelo ID (ou outro seletor)
    tabela = driver.find_element(By.CLASS_NAME, "table")

    # Extrai todas as linhas do corpo da tabela
    linhas = tabela.find_elements(By.TAG_NAME, "tr")

    # Percorre cada linha e extrai as células
    """ for linha in linhas:
        colunas = linha.find_elements(By.TAG_NAME, "td")
        dados = [coluna.text for coluna in colunas]
        if dados:  # Ignora linhas vazias (ex: cabeçalho)
            print(dados[-5:]) """

    dados = []
    for linha in linhas[2:15]:
        colunas = linha.find_elements(By.TAG_NAME, "td")
        linha_dados = []
        for coluna in colunas:
            texto = coluna.text
            if '\n' in texto:
                linha_dados.append(texto.split('\n')[1])
            else:
                linha_dados.append(texto)
        if linha_dados:
            dados.append(linha_dados[-5:])
    driver.quit()
    print (dados)
    return dados