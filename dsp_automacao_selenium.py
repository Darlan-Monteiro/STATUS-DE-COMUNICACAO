"""
Código para automação do site DSP usando Selenium.
O objetivo é percorrer todas as datas que não foram atualizadas após o processamento de dados.
"""

import os
import time
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ---- ETAPA 4 ----:


def config_navegador(): 
    """ 
    Função para configurar o navegador Edge com perfil de usuário específico e acessar o site DSP.
    """
    load_dotenv()
    caminho_user_chorme = os.getenv('caminho_user_chorme')
    site_dsp = os.getenv('site_dsp')
    s = Service(r'./msedgedriver.exe')
    #s = Service(EdgeChromiumDriverManager().install())
    dsp_automation = webdriver.EdgeOptions()
    dsp_automation.add_argument(caminho_user_chorme)
    driver = webdriver.Edge(service=s, options=dsp_automation)
    driver.get(site_dsp)
    return driver

def web(sn_lista): 
    """ 
    Função principal para automação no site DSP.
    Recebe uma lista de SNs e retorna um dicionário com a data da última comunicação.
    """
    
    driver = config_navegador() # Inicia o navegador com a função config_navegador
        
    data = {} # Dicionário para armazenar os resultados de última comunicação
    for sn in sn_lista:
        try:
            # O site DSP pode demorar para carregar, então busquei o loader do site para garantir que a página esteja pronta antes de prosseguir
            loader_locator = (By.TAG_NAME, "dsp-next-gen-ui-loader")

            # Espera o loader desaparecer
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located(loader_locator)
            )
            busca = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'input-field')
                )
            )
            busca.click()
            # Bloco para limpar o campo de busca antes de inserir o novo SN
            busca.send_keys(Keys.CONTROL + "a")
            busca.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # Insere o SN e pressiona Enter
            busca.send_keys(sn + Keys.ENTER)


            # Novamente espera o loader desaparecer
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located(loader_locator)
            )
            # Bloco para localizar o elemento do SN na lista de resultados.
            # Aqui ele pega o SN e faz uma busca dele na página
            lista_sn_elementos = WebDriverWait(driver, 120).until(
                EC.presence_of_all_elements_located((By.ID, 'td-0-0')
                )
            )
            # Buscando SN na lista de elementos encontrados
            for sn_elemento in lista_sn_elementos:
                if sn in sn_elemento.text.upper():
                    time.sleep(0.5)
                    sn_elemento.click()
                    break            
            else:
                print(f"Elemento não encontrado: {sn}")
                data[sn] = "Elemento não encontrado"
                continue
            
            # Espera o loader desaparecer novamente
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located(loader_locator)
                )
            
            # Esperar engrenagem estar clicável
            engrenagem_device_information = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="asset-drawer-container"]/div/div[1]/div/div[2]/dsp-next-gen-ui-dft-asset-device-details/div/cc-card/div/cc-card-content/div/div[1]/div[2]/img')
                )
            )
            # Scroll até o elemento e tentar clicar
            driver.execute_script("arguments[0].scrollIntoView(true);", engrenagem_device_information)
            time.sleep(0.5)
            try:                
                engrenagem_device_information.click()
            except Exception as e:
                print(f"Erro ao clicar na engrenagem (tentando via JS): {e}")
                driver.execute_script("arguments[0].click();", engrenagem_device_information)

            # Espera o loader desaparecer novamente
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located(loader_locator)
            )
            last_check_in = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="device-status"]/div[2]/div[1]/div/div/div[3]/div[1]/span[2]')
                )
            ).text
            # Armazena o resultado no dicionário
            data[sn] = last_check_in

            # Fecha a aba de status do dispositivo
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located(loader_locator)
            )
            x_device_status = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="device-status"]/div[1]/div/div/cc-icon')
                )
            )
            time.sleep(0.5)
            x_device_status.click()

            # Fechar segunda aba
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located(loader_locator)
            )
            x_segunda_aba = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="multiSizeDrawer"]/div[2]/dsp-next-gen-ui-dft-asset-drawer/div/div[1]/div[2]/div[2]/cc-icon')
                )
            )
            time.sleep(0.5)
            x_segunda_aba.click()

            print(data)
        
        except (TimeoutException, NoSuchElementException) as e:
            print(f" Erro ao processar SN {sn}: {e}")
            data[sn] = "Erro na coleta"
            
    # Finaliza o driver após a conclusão do processo
    driver.quit()
    
    return data # Retorna o dicionário com os resultados