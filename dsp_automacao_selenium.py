"""
Código para automação do site DSP usando Selenium (Versão Chrome).
O objetivo é percorrer todas as datas que não foram atualizadas após o processamento de dados.
"""

import os
import time
from pathlib import Path
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def config_navegador(): 
    """ 
    Função para configurar o Google Chrome com Perfil Persistente (DSP).
    """
    load_dotenv()
    site_dsp = os.getenv('site_dsp')
    
    chrome_options = webdriver.ChromeOptions()
    
    # Cria um perfil no chrome para salvar sessão e cookies. gera uma pasta na raiz do projeto
    caminho_base_perfis = Path.home() / ".robo_perfis" / "dsp"
    chrome_options.add_argument(f"user-data-dir={caminho_base_perfis}")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-search-engine-choice-screen")

    # Instala ou atualiza driver
    try:
        driver_path = ChromeDriverManager().install()
    except:
        print("Falha na instalação automática. Tentando versão forçada...")
        driver_path = ChromeDriverManager(driver_version="142.0.7444.176").install()

    servico = Service(driver_path)
    driver = webdriver.Chrome(service=servico, options=chrome_options)
    driver.get(site_dsp)
    return driver

def web(sn_lista): 
    """ 
    Função principal para automação no site DSP.
    Recebe uma lista de SNs e retorna um dicionário com a data da última comunicação.
    """
    driver = config_navegador()
        
    data = {} 
    
    for sn in sn_lista:
        try:
            print(f"Iniciando busca para: {sn}")
            
            # pegar o loader da pag
            loader_locator = (By.TAG_NAME, "dsp-next-gen-ui-loader")

            # Espera inicial e limpeza de tela
            WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(loader_locator))
            
            # Campo de busca
            busca = WebDriverWait(driver, 300).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'input-field'))
            )
            
            # Garante que o campo está visível e clica
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1) 
            try:
                busca.click()
            except:
                driver.execute_script("arguments[0].click();", busca)
            
            # Limpa e insere o SN
            busca.send_keys(Keys.CONTROL + "a")
            busca.send_keys(Keys.DELETE)
            time.sleep(0.5)
            busca.send_keys(sn + Keys.ENTER)
         
            # Espera carregar resultados da tabela
            WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(loader_locator))
            
            # Localiza elementos na lista
            lista_sn_elementos = WebDriverWait(driver, 120).until(
                EC.presence_of_all_elements_located((By.ID, 'td-0-0'))
            )
            
            # Bloco para encontrar o SN na lista
            encontrou = False
            for sn_elemento in lista_sn_elementos:
                if sn in sn_elemento.text.upper():
                    time.sleep(0.5)
                    WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(loader_locator))
                    sn_elemento.click()
                    print(f"SN {sn} encontrado e clicado.")
                    encontrou = True
                    break            
            
            if not encontrou:
                print(f"Elemento não encontrado: {sn}")
                data[sn] = "Elemento não encontrado"
                continue
            
            # Clica na engrenagem
            engrenagem_device_information = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'settingsIconStyle')
                )
            )
            
            WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(loader_locator))   
            time.sleep(1)           
            engrenagem_device_information.click()
        
            # Pega a data
            WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(loader_locator))
            time.sleep(1)
            last_check_in = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="device-status"]/div[2]/div[1]/div/div/div[3]/div[1]/span[2]'))
            ).text
            
            data[sn] = last_check_in
            print(f"Data coletada: {last_check_in}")

            # Fecha as abas
            WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(loader_locator))
            
            # Bloco para fechar a aba de Device Status
            try:
                x_device_status = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="device-status"]/div[1]/div/div/cc-icon'))
                )
                WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(loader_locator))
                time.sleep(0.5)
                x_device_status.click()
            except:
                pass

            time.sleep(1)
            
            # Bloco para voltar à tela principal
            try:
                seta_voltar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'cc-drawer__leadingIcon'))
                )
                WebDriverWait(driver, 30).until(EC.invisibility_of_element_located(loader_locator))
                time.sleep(0.5)
                seta_voltar.click()
            except:
                pass

            print(data)
        
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Erro ao processar SN {sn}: {e}")
            data[sn] = "Erro na coleta"
            
    driver.quit()
    return data