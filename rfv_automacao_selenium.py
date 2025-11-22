"""
Código para automação do site RFV usando Selenium.
O objetivo é iterar sobre uma lista de clientes, selecionar cada um no site,
navegar até a seção "Área Vitals/Fleet Status" e exportar os dados em formato CSV.
"""

import os
import time
import polars as pl
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# ---- ETAPA 2 ----:

def config_navegador():
    """ 
    Função para configurar o navegador Edge com perfil de usuário específico e acessar o site RFV 
    """
    load_dotenv()
    caminho_user_rfv = os.getenv('caminho_user_rfv')
    site_rfv = os.getenv('site_rfv')
    s = Service(r'./msedgedriver.exe')
    #s = Service(EdgeChromiumDriverManager().install())
    rfv_automation = webdriver.EdgeOptions()
    rfv_automation.add_argument(caminho_user_rfv)
    driver = webdriver.Edge(service=s, options=rfv_automation)
    driver.get(site_rfv)
    return driver


def automacao_rfv():
    """ 
    Função principal para automação no site RFV.
    O objetivo aqui é iterar sobre a lista de clientes e exportar os dados necessários.
    """
    driver = config_navegador()
    caminho_base_cleinte = os.getenv('base_clientes')
    base_cliente = caminho_base_cleinte
    base_clientes = pl.read_excel(base_cliente)
    coluna_clientes = 'Clientes'
    clientes = base_clientes[coluna_clientes].to_list()

    # for para iterar sobre a lista de clientes e realizar as ações necessárias no site RFV.
    # Este bloco tenta localizar e interagir com o dropdown de seleção de clientes no site RFV
    for cliente in clientes:
        try:
            
            print(f"\n")
            # Encontra o xpath do dropdown para colocar o cliente
            dropdown_abrir = WebDriverWait(driver, 130).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="involve-select-0"]/div[1]/input')
                )
            ) 
            dropdown_abrir.click()
            time.sleep(0.3)
            dropdown_abrir.clear() # Limpa o campo do dropdown para tirar qualquer valor pré-existente
            print(f"Procurando cliente: {cliente}")
            dropdown_abrir.send_keys(cliente) # Digita o nome do cliente no dropdown
            time.sleep(0.3)
            dropdown_abrir.send_keys(Keys.ENTER)
            print(f"Cliente {cliente} processado com sucesso.")
             
        except TimeoutException:
            print(f"Não foi possível encontrar o dropdown para o cliente {cliente}.\n")
            continue  
        except Exception as e:
            print(f"Ocorreu um erro ao processar o cliente {cliente}: {e}")
            continue
        
        
        # Este bloco tenta localizar e interagir com os checkboxes de termos de uso no site RFV.
        # Só será executado se os termos de uso aparecerem na tela
        try:
            if True:
                checkbox__square_superior = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='involve-checkbox-0']")
                    )
                )
                checkbox__square_superior.click()
                
                checkbox__square_inferior = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='involve-checkbox-1']")
                    )
                )
                checkbox__square_inferior.click()
                print("Checkbox de termos de uso clicado com sucesso.")         
                
                i_agree_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/app/div[1]/app-eula/div/div[3]/button[1]')
                    )
                )
                i_agree_button.click()
                print("Termos de uso aceitos com sucesso.")
        except:
            pass
                       
        # Este bloco tenta navegar até a aba do cliente   
        try:
            seta_aba_cliente = WebDriverWait(driver, 130).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/app/div[1]/ng-component/sitemapgroup-dashboard/ng-component/breadcrumb/div/div[1]/span[2]')
                )
            )
            seta_aba_cliente.click()
        except Exception as e:
            print(f"Erro ao abrir aba do cliente {cliente}: {e}")
            continue


        # Este bloco tenta localizar e clicar na seção "Área Vitals/Fleet Status" no site RFV
        try:
            
            selecionar_menu_opçoes = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/app/div[1]/ng-component/sitemapgroup-dashboard/ng-component/breadcrumb/div/div[2]/div[1]/breadcrumb-menu/div')
                )
            )
            selecionar_menu_opçoes.click()
            
            # Aqui eu estou pegando todos os elementos h3 que aparecem no overlay do menu
            lista_h3 = WebDriverWait(driver, 60).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@id, "cdk-overlay")]/div/div/div//h3')
                )
            )
            
            #Loop para encontrar e clicar no elemento correto de Área Vitals ou Fleet Status
            for i, elementos_h3 in enumerate(lista_h3):
                if "Area Vitals" in elementos_h3.text or "Fleet Status" in elementos_h3.text:
                    elementos_h3.click()
                    print(f" Área Vitals/Fleet Status encontrada e clicada com sucesso para o cliente {cliente}.")
                    break
    
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

        except Exception as e:
            print(f" Erro ao clicar em Área Vitals/Fleet Status para o cliente {cliente}: {e}\n")
            continue


        # Este bloco tenta exportar os dados do sistema em formato CSV
        try:
            # Espera o overlay de carregamento desaparecer antes de prosseguir
            WebDriverWait(driver, 15).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "cdk-overlay-backdrop")
                )
            )
        except TimeoutException:
            print(" O overlay demorou para desaparecer, tentando continuar mesmo assim.")


        # Espera o botão de status do sistema estar clicável
        try:
            system_status = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'menu-button')
                )
            )
            system_status.click()
            print(" Status do sistema clicado com sucesso.")
        except ElementClickInterceptedException:
            # Segunda tentativa de clique no status do sistema. O sistema pode demorar a responder
            try:
                system_status.click()
                print(" Clique no status do sistema realizado na segunda tentativa.")
            except Exception as e:
                print(f" Erro ao tentar clicar novamente no status do sistema: {e}")
                continue
        except TimeoutException:
            print(" Não foi possível encontrar o status do sistema.\n")
            continue
        
        # Este bloco é para clicar no botão de exportação
        try:
            export = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//system-status-tile-v2//involve-datasource-export//button')
                )
            )
            export.click()
            print(" Exportando dados...")
        except TimeoutException:
            print(" Não foi possível encontrar o botão de exportação.\n")
            continue
        
        # Este bloco é para selecionar o formato CSV na exportação
        try:
            csv_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'CSV')]")
                )
            )
            csv_button.click()
            print("Formato CSV selecionado com sucesso.")
        except TimeoutException:
            print(" Não foi possível encontrar o formato CSV.\n")
            continue
        
    # Finaliza o driver após a conclusão do processo
    driver.quit()