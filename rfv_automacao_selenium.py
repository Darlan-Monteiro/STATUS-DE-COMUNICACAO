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
    dsp_automation = webdriver.EdgeOptions()
    dsp_automation.add_argument(caminho_user_rfv)
    driver = webdriver.Chrome(service=s, options=dsp_automation)
    driver.get(site_rfv)
    time.sleep(20)  
    return driver


def automacao_rfv():
    driver = config_navegador()
    
    # Carregar a base de clientes
    base_clientes = pl.read_excel(r'C:\Users\700543\Sotreq\Darlan Monteiro - Desenvolvimento\status_project\STATUS-DE-COMUNICACAO\clientes.xlsx')
    coluna_clientes = 'Clientes'
    clientes = base_clientes[coluna_clientes].to_list()
    
    for cliente in clientes:
        try:
            dropdown_abrir = WebDriverWait(driver, 120).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="involve-select-0"]/div[1]/input'))
            )
            
            time.sleep(2)  
            dropdown_abrir.click()
            time.sleep(1)
            dropdown_abrir.clear()
            time.sleep(1)

            print(f"Procurando cliente: {cliente}")
            dropdown_abrir.send_keys(cliente)
            time.sleep(2)  
            dropdown_abrir.send_keys(Keys.ENTER)
            time.sleep(3) 
            
            print(f"Cliente {cliente} processado com sucesso.")
            
        except TimeoutException:
            print(f"Não foi possível encontrar o dropdown para o cliente {cliente}.")
        
        except Exception as e:
            print(f"Ocorreu um erro ao processar o cliente {cliente}: {e}")

        
        try:
            click_nome_cliente = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.XPATH, '//*[contains(@class, "involve-tree-node")]/h4'))
            )
            time.sleep(2)
            click_nome_cliente.click()
            print(f"Nome do cliente {cliente} encontrado e clicado com sucesso.")
        except TimeoutException:
            print(f"Não foi possível encontrar o nome do cliente para {cliente}.")
            continue
        
               
        
        
         
        try:
            area_vitals_h4 = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((
            By.XPATH,
            '//system-status-tile-v2//involve-tile-header-button'
        ))
    )
            area_vitals_h4.click()
            print("Área Vitals encontrada e clicada com sucesso.")
        except TimeoutException:
            print("Não foi possível encontrar a área Vitals.")
          
               
        system_status = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((
            By.CLASS_NAME,
            'ng-star-inserted')))       
  
        print('Clicando no status do sistema...')
        time.sleep(2)
        system_status.click()
        print("Status do sistema clicado com sucesso.")
        
        export = WebDriverWait(driver, 60).until(
    EC.element_to_be_clickable((By.XPATH, '//system-status-tile-v2//involve-datasource-export//button'))
)   
        export.click()
        print("Exportando dados...")
        
        xlsx = WebDriverWait(driver, 60).until(
    EC.element_to_be_clickable((By.CLASS_NAME, 'overflow-auto'))
)
        if "XLSX" in xlsx.text:
            xlsx.click()
            print("Formato XLSX selecionado com sucesso.")

         
automacao_rfv()
    