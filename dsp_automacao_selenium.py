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
    driver = webdriver.Chrome(service=s, options=dsp_automation)
    driver.get(site_dsp)
    return driver

def web(sn_lista): 
    driver = config_navegador()
    pesquisa = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'input-field')))
    time.sleep(1)
    pesquisa.send_keys('12345678' + Keys.ENTER)
        
    data = {}
    
    for sn in sn_lista:
        try:
            # Limpar barra de pesquisa anterior
            x_barra_pesquisa = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'clear')))
            time.sleep(3)
            x_barra_pesquisa.click()

            # Realizar nova busca
            busca = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'input-field')))
            time.sleep(3)
            busca.send_keys(sn + Keys.ENTER)

            # Buscar por elementos relacionados ao SN
            lista_sn_elementos = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.ID, 'td-0-0')))
            for sn_elementos in lista_sn_elementos:
                if sn in sn_elementos.text.upper():
                    time.sleep(3)
                    sn_elementos.click()
                    break
            else:
                print(f"- Elemento não encontrado: {sn}")
                continue

            # Abrir engrenagem de informações do dispositivo
            engrenagem_device_information = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="asset-drawer-container"]/div/div[1]/div/div[2]/dsp-next-gen-ui-dft-asset-device-details/div/cc-card/div/cc-card-content/div/div[1]/div[2]/img')))
            time.sleep(3)
            engrenagem_device_information.click()
            time.sleep(3)

            # Captura das datas
            last_check_in = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, '//*[@id="device-status"]/div[2]/div[1]/div/div/div[3]/div[1]/span[2]'))).text

            # last_http = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, '//*[@id="device-status"]/div[2]/div[1]/div/div/div[3]/div[2]/span[2]'))).text

            # last_saber = WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, '//*[@id="device-status"]/div[2]/div[1]/div/div/div[3]/div[3]/span[2]'))).text

            # # Formato esperado das datas
            # formato_data = "%d/%m/%Y"

            # def converter_data(data_str):
            #     """Converte string de data para datetime, ignorando valores inválidos."""
            #     if data_str and data_str.strip() not in ["-", ""]:
            #         try:
            #             return datetime.strptime(data_str.split(" ")[0], formato_data)
            #         except ValueError:
            #             print(f"Erro ao converter data: {data_str}")
            #             return None
            #     return None

            # # Conversão das datas
            # data_check_in = converter_data(last_check_in)
            # data_http = converter_data(last_http)
            # data_saber = converter_data(last_saber)

            # Filtrar apenas datas válidas e encontrar a maior
            # datas_validas = [d for d in [data_check_in, data_http, data_saber] if d is not None]
            # maior_data = max(datas_validas) if datas_validas else None

            # Armazenar no dicionário
            data[sn] = last_check_in

            # Fechar abas abertas
            x_device_status = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="device-status"]/div[1]/div/div/cc-icon'))
            )
            time.sleep(3)
            x_device_status.click()

            x_segunda_aba = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="multiSizeDrawer"]/div[2]/dsp-next-gen-ui-dft-asset-drawer/div/div[1]/div[2]/div[2]/cc-icon'))
            )
            time.sleep(3)
            x_segunda_aba.click()

            print(data)
        
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Erro ao processar SN {sn}: {e}")
            data[sn] = "Erro na coleta"

    driver.quit()
    return data