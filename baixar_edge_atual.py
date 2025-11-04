import requests
import os
import winreg # para ler o registro do Windows e descobrir a versão do Edge
from bs4 import BeautifulSoup
import zipfile
from io import BytesIO

def get_local_edge_version():
    """
    Verifica no registro do Windows a versão do Microsoft Edge instalada.
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Edge\BLBeacon")
        version, _ = winreg.QueryValueEx(key, "version")
        print(f"Versão do Microsoft Edge encontrada: {version}")
        return version
    except FileNotFoundError:
        print("Não foi possível encontrar a versão do Microsoft Edge no registro.")
        return None

def gerenciar_edgedriver():
    """
    Verifica se o msedgedriver.exe existe e, se não, baixa a versão correta,
    extrai e coloca na pasta do projeto.
    """
    if os.path.exists("msedgedriver.exe"):
        print("O arquivo msedgedriver.exe já existe. Pulando a parte do download.")
        return True

    print(" msedgedriver.exe não encontrado. Iniciando processo de download...")
    
    local_version = get_local_edge_version()
    if not local_version:
        return False

    url = "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/"
    
    print(f"Acessando a página de drivers: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Falha ao acessar a página de drivers: {e}")
        return False

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontra todos os links na página
    links = soup.find_all('a', href=True)
    download_link = None
    
    # O número da versão principal (ex: '125' de '125.0.2535.85')
    major_version = local_version.split('.')[0]

    # Procura um link que contenha a versão principal e seja para win64
    for link in links:
        if major_version in link['href'] and "win64" in link['href'] and link['href'].endswith('.zip'):
            download_link = link['href']
            print(f" Link de download encontrado para a versão ~{major_version}: {download_link}")
            break

    if not download_link:
        print(f" Não foi encontrado um driver compatível para a versão {major_version} na página.")
        return False
        
    print(f" Baixando o driver de {download_link}...")
    try:
        driver_response = requests.get(download_link, stream=True)
        driver_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f" Falha ao baixar o arquivo do driver: {e}")
        return False
        
    print(" Descompactando o arquivo...")
    try:
        zip_file = zipfile.ZipFile(BytesIO(driver_response.content))
        zip_file.extract('msedgedriver.exe', '.')
        print(" msedgedriver.exe extraído com sucesso na pasta do projeto!")
        return True
    except Exception as e:
        print(f" Erro ao descompactar o arquivo: {e}")
        return False
    