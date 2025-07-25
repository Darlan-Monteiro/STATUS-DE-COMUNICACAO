from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import polars as pl

def config_navegador():
    load_dotenv()
    caminho_user_rfv = os.getenv('caminho_user_rfv')
    site_rfv = os.getenv('site_rfv')
    s = Service(r'./msedgedriver.exe')
    rfv_automation = webdriver.EdgeOptions()
    rfv_automation.add_argument(caminho_user_rfv)
    driver = webdriver.Edge(service=s, options=rfv_automation)
    driver.get(site_rfv)
    return driver

def automacao_rfv(): # função principal para automatizar o processo de exportação de dados do RFV
    driver = config_navegador()
    caminho_base_cleinte = os.getenv('base_clientes')
    base_cliente = caminho_base_cleinte
    base_clientes = pl.read_excel(base_cliente)
    coluna_clientes = 'Clientes'
    clientes = base_clientes[coluna_clientes].to_list()
    
    for cliente in clientes: # loop para iterar sobre cada cliente na lista de clientes
        try:
            dropdown_abrir = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="involve-select-0"]/div[1]/input'))) # Localiza o dropdown de clientes
            dropdown_abrir.click()
            dropdown_abrir.clear()
            time.sleep(0.5)
            print(f"Procurando cliente: {cliente}")
            dropdown_abrir.send_keys(cliente)
            time.sleep(0.3)  
            dropdown_abrir.send_keys(Keys.ENTER)
            print(f"Cliente {cliente} processado com sucesso.")
        except TimeoutException:
            print(f"Não foi possível encontrar o dropdown para o cliente {cliente}.")       
        except Exception as e:
            print(f"Ocorreu um erro ao processar o cliente {cliente}: {e}")
        
        try: # clica no nome do cliente na árvore de clientes
            click_nome_cliente = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[contains(@class, "involve-tree-node")]/h4')))
            time.sleep(2)
            click_nome_cliente.click()
            print(f"Nome do cliente {cliente} encontrado e clicado com sucesso.")
        except TimeoutException:
            print(f"Não foi possível encontrar o nome do cliente para {cliente}.")
            continue
         
        try: # clica na área de Vitals ou Fleet Status
            area_vitals_h4 = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "cdk-virtual-scroll-content-wrapper")]//h4[normalize-space()="Area Vitals" or normalize-space()="Fleet Status"]')))
            if "Area Vitals" in area_vitals_h4.text or "Fleet Status" in area_vitals_h4.text:
                time.sleep(2)
                area_vitals_h4.click()
                print("Área Vitals encontrada e clicada com sucesso.")
        except TimeoutException:
            print("Não foi possível encontrar a área Vitals.")
            continue
                       
        try: # clica no botão de status do sistema
            system_status = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME,'menu-button')))
            time.sleep(2)
            system_status.click()
            print("Status do sistema clicado com sucesso.")
        except TimeoutException:
            print("Não foi possível encontrar o status do sistema.")
            continue
        
        try: # clica no botão de exportação de dados
            export = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//system-status-tile-v2//involve-datasource-export//button')))   
            time.sleep(2)
            export.click()
            print("Exportando dados...")    
        except TimeoutException:
            print("Não foi possível encontrar o botão de exportação.")
            continue
        
        try: # seleciona o formato XLSX para exportação
            #xlsx = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'overflow-auto')))
            csv_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'CSV')]")))
            time.sleep(2)
            csv_button.click()
            print("Formato CSV selecionado com sucesso.")
        except TimeoutException:
            print("Não foi possível encontrar o formato CSV.")
            continue
        time.sleep(1)