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
    
    for cliente in clientes: # loop principal sobre cada cliente na lista de clientes
        try:
            dropdown_abrir = WebDriverWait(driver, 130).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="involve-select-0"]/div[1]/input'))) # localiza o dropdown de clientes
            dropdown_abrir.click()
            dropdown_abrir.clear()
            time.sleep(2)
            print(f"📁 Procurando cliente: {cliente}")
            dropdown_abrir.send_keys(cliente)
            time.sleep(2)  
            dropdown_abrir.send_keys(Keys.ENTER)
            print(f"⚙️✅ Cliente {cliente} processado com sucesso.")
        except TimeoutException:
            print(f"⚙️❌ Não foi possível encontrar o dropdown para o cliente {cliente}.\n")
            continue  
        except Exception as e:
            print(f"⚙️❗Ocorreu um erro ao processar o cliente {cliente}: {e}")
            continue

        seta_aba_cliente = WebDriverWait(driver, 130).until(EC.element_to_be_clickable((By.XPATH, '/html/body/app/div[1]/ng-component/sitemapgroup-dashboard/ng-component/breadcrumb/div/div[1]/span[2]')))
        time.sleep(2)
        seta_aba_cliente.click()
                
        selecionar_menu_opçoes = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/app/div[1]/ng-component/sitemapgroup-dashboard/ng-component/breadcrumb/div/div[2]/div[1]/breadcrumb-menu/div')))
        time.sleep(1.5)
        selecionar_menu_opçoes.click()
        time.sleep(1)
        lista_h3 = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@id, "cdk-overlay")]/div/div/div//h3')))
        time.sleep(1)
        
        for i, elementos_h3 in enumerate(lista_h3):
            if "Area Vitals" in elementos_h3.text:
                time.sleep(2)
                elementos_h3.click()
                print(f"✅ Área Vitals encontrada e clicada com sucesso para o cliente {cliente}.")
                break
        else:
            print(f"❌ Não foi possível encontrar a área Vitals para o cliente {cliente}.\n")
            continue
                       
        try: # clica no botão de status do sistema
            system_status = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME,'menu-button')))
            time.sleep(2)
            system_status.click()
            print("✅ Status do sistema clicado com sucesso.")
        except TimeoutException:
            print("❌ Não foi possível encontrar o status do sistema.\n")
            continue
        
        try: # clica no botão de exportação de dados
            export = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//system-status-tile-v2//involve-datasource-export//button')))   
            time.sleep(2)
            export.click()
            print("⌛ Exportando dados...") 
        except TimeoutException:
            print("⌛❌ Não foi possível encontrar o botão de exportação.\n")
            continue
        
        try: # seleciona o formato XLSX para exportação
            #xlsx = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'overflow-auto')))
            csv_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'CSV')]")))
            time.sleep(3)
            csv_button.click()
            print("✅ Formato CSV selecionado com sucesso.")
        except TimeoutException:
            print("❌ Não foi possível encontrar o formato CSV.\n")
            continue
        time.sleep(1)