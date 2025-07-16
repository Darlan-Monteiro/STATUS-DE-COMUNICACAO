from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
from datetime import datetime
import time
import os

def config_navegador():
    load_dotenv()
    caminho_user_chorme = os.getenv('caminho_user_chorme')
    site_dsp = os.getenv('site_dsp')

    s = Service(r'./msedgedriver.exe')
    dsp_automation = webdriver.EdgeOptions()
    dsp_automation.add_argument(caminho_user_chorme)
    driver = webdriver.Edge(service=s, options=dsp_automation)
    driver.get(site_dsp)
    return driver

def web(sn_lista): 
    driver = config_navegador()

    # Esperar campo de pesquisa inicial
    pesquisa = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'input-field'))
    )
    time.sleep(2)
    pesquisa.send_keys('12345678' + Keys.ENTER)
        
    data = {}
    
    for sn in sn_lista:
        try:
            # Limpar barra de pesquisa anterior
            x_barra_pesquisa = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'clear'))
            )
            time.sleep(1)
            x_barra_pesquisa.click()

            # Realizar nova busca
            busca = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'input-field'))
            )
            time.sleep(3)
            busca.send_keys(sn + Keys.ENTER)

            # Buscar elemento relacionado ao SN
            lista_sn_elementos = WebDriverWait(driver, 120).until(
                EC.presence_of_all_elements_located((By.ID, 'td-0-0'))
            )
            for sn_elemento in lista_sn_elementos:
                if sn in sn_elemento.text.upper():
                    time.sleep(3)
                    sn_elemento.click()
                    break
            else:
                print(f"- Elemento não encontrado: {sn}")
                data[sn] = "SN não encontrado"
                continue

            # Esperar engrenagem de informações do dispositivo estar clicável
            engrenagem_device_information = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="asset-drawer-container"]/div/div[1]/div/div[2]/dsp-next-gen-ui-dft-asset-device-details/div/cc-card/div/cc-card-content/div/div[1]/div[2]/img'))
            )

            # Scroll até o elemento e tentar clicar
            driver.execute_script("arguments[0].scrollIntoView(true);", engrenagem_device_information)
            time.sleep(3)
            try:
                engrenagem_device_information.click()
            except Exception as e:
                print(f"Erro ao clicar na engrenagem (tentando via JS): {e}")
                driver.execute_script("arguments[0].click();", engrenagem_device_information)

            time.sleep(3)

            # Captura da data "Last Check-in"
            last_check_in = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="device-status"]/div[2]/div[1]/div/div/div[3]/div[1]/span[2]'))
            ).text

            data[sn] = last_check_in

            # Fechar aba de status do dispositivo
            x_device_status = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="device-status"]/div[1]/div/div/cc-icon'))
            )
            time.sleep(3)
            x_device_status.click()

            # Fechar segunda aba
            x_segunda_aba = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="multiSizeDrawer"]/div[2]/dsp-next-gen-ui-dft-asset-drawer/div/div[1]/div[2]/div[2]/cc-icon'))
            )
            time.sleep(3)
            x_segunda_aba.click()

            print(data)
        
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Erro ao processar SN {sn}: {e}")
            data[sn] = "Erro na coleta"

    driver.quit()
    return data