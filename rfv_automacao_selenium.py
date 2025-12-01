"""
Código para automação do site RFV usando Selenium (Versão Chrome).
O objetivo é iterar sobre uma lista de clientes, selecionar cada um no site,
navegar até a seção "Área Vitals/Fleet Status" e exportar os dados em formato CSV.
"""

import os
import time
import polars as pl
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


def config_navegador():

    """ 
    Função para configurar o Google Chrome com Perfil Persistente.
    Salva cookies e sessão na pasta 'chrome_perfil_rfv'.
    """
    load_dotenv()
    site_rfv = os.getenv('site_rfv')
    chrome_options = webdriver.ChromeOptions()
    caminho_base_perfis = Path.home() / ".status_perfis" / "rfv"
    chrome_options.add_argument(f"user-data-dir={caminho_base_perfis}")
    
    # Argumentos padrão
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    
    # Instala ou atualiza driver
    try:
        driver_path = ChromeDriverManager().install()
    except:
        driver_path = ChromeDriverManager(driver_version="142.0.7444.176").install()
        
    servico = Service(driver_path)
    driver = webdriver.Chrome(service=servico, options=chrome_options)
    
    try:
        driver.get(site_rfv)
    except Exception as e:
        print(f"Erro ao acessar site: {e}")
        
    return driver


def automacao_rfv():
    """ 
    Função principal para automação no site RFV.
    """
    driver = config_navegador()
    caminho_base_cleinte = os.getenv('base_clientes')
    base_cliente = caminho_base_cleinte
    base_clientes = pl.read_excel(base_cliente)
    coluna_clientes = 'Clientes'
    clientes = base_clientes[coluna_clientes].to_list()

    # for para iterar sobre a lista de clientes
    for cliente in clientes:
        try:
            print(f"\n")
            # Encontra o xpath do dropdown para colocar o cliente
            dropdown_abrir = WebDriverWait(driver, 300).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="involve-select-0"]/div[1]/input')
                )
            ) 
            dropdown_abrir.click()
            time.sleep(0.3)
            dropdown_abrir.clear() 
            print(f"Procurando cliente: {cliente}")
            dropdown_abrir.send_keys(cliente) 
            time.sleep(0.3)
            dropdown_abrir.send_keys(Keys.ENTER)
            print(f"Cliente {cliente} processado com sucesso.")
             
        except TimeoutException:
            print(f"Não foi possível encontrar o dropdown para o cliente {cliente}.\n")
            continue  
        except Exception as e:
            print(f"Ocorreu um erro ao processar o cliente {cliente}: {e}")
            continue
        
        # Checkboxes de termos de uso
        try:
            if True:
                checkbox__square_superior = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='involve-checkbox-0']")
                    )
                )
                checkbox__square_superior.click()
                
                checkbox__square_inferior = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='involve-checkbox-1']")
                    )
                )
                checkbox__square_inferior.click()
                
                i_agree_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/app/div[1]/app-eula/div/div[3]/button[1]')
                    )
                )
                i_agree_button.click()
                print("Termos de uso aceitos.")
        except:
            pass
                       
        # Navegar até a aba do cliente   
        try:
            seta_aba_cliente = WebDriverWait(driver, 130).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/app/div[1]/ng-component/sitemapgroup-dashboard/ng-component/breadcrumb/div/div[1]/span[2]')
                )
            )
            seta_aba_cliente.click()
        except Exception as e:
            print(f"Erro ao abrir aba do cliente {cliente}: {e}")
            continue

        # Clicar na seção "Área Vitals/Fleet Status"
        try:
            selecionar_menu_opçoes = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/app/div[1]/ng-component/sitemapgroup-dashboard/ng-component/breadcrumb/div/div[2]/div[1]/breadcrumb-menu/div')
                )
            )
            selecionar_menu_opçoes.click()
            
            lista_h3 = WebDriverWait(driver, 60).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@id, "cdk-overlay")]/div/div/div//h3')
                )
            )
            
            for i, elementos_h3 in enumerate(lista_h3):
                if "Area Vitals" in elementos_h3.text or "Fleet Status" in elementos_h3.text:
                    elementos_h3.click()
                    print(f" Área Vitals/Fleet Status encontrada.")
                    break
    
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

        except Exception as e:
            print(f" Erro ao clicar em Área Vitals: {e}\n")
            continue

        # Exportar CSV
        try:
            WebDriverWait(driver, 15).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "cdk-overlay-backdrop"))
            )
        except:
            pass

        try:
            system_status = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'menu-button')
                )
            )
            system_status.click()
            print(" Status do sistema clicado.")
        except Exception as e:
            try:
                system_status.click()
            except:
                print(f"Não foi possível clicar no status do sistema.")
                continue
        
        try:
            export = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//system-status-tile-v2//involve-datasource-export//button')
                )
            )
            export.click()
            print("Exportando dados...")
        except:
            print("Botão exportar não encontrado.")
            continue
        
        try:
            csv_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'CSV')]")
                )
            )
            csv_button.click()
            print("Formato CSV selecionado.")
        except:
            print("Opção CSV não encontrada.")
            continue
        
    driver.quit()