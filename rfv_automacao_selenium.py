import os
import polars as pl
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

def config_navegador():
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

def login():
    cws = input("Insira o Seu CWS: ")
    senha = input("Insira a Sua Senha: ")
    return cws, senha



def automacao_rfv():
    cws, senha = login()
    driver = config_navegador()
    caminho_base_cleinte = os.getenv('base_clientes')
    base_cliente = caminho_base_cleinte
    base_clientes = pl.read_excel(base_cliente)
    coluna_clientes = 'Clientes'
    clientes = base_clientes[coluna_clientes].to_list()
    print(f"Tentando login com o CWS: {cws}")
    
    try:
        campo_cws = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.ID, 'signInName'))
        )
        campo_cws.clear()
        campo_cws.send_keys(cws)
        
        botao_continuar = driver.find_element(By.ID, 'next')
        botao_continuar.click()

        print("Verificando se a senha é necessária...")
        
        try:
            campo_senha = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'i0118'))
            )

            print("Senha necessária. Inserindo senha...")
            campo_senha.clear()
            campo_senha.send_keys(senha)
            campo_senha.send_keys(Keys.ENTER)

            print("Verificando o login após a senha...")
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="involve-select-0"]/div[1]/input'))
            )
            
        except TimeoutException:
            print("Campo de senha não encontrado. Verificando login automático...")
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="involve-select-0"]/div[1]/input'))
            )
            print("Login automático (sem senha) detectado.")
        print(" Login realizado com sucesso!")

    except TimeoutException:

        print("\n" + "="*40)
        print("ERRO! o Login falhou.")
        print("   Verifique seu CWS/Senha.")
        print("   Encerrando o programa.")
        print("="*40 + "\n")
        
        driver.quit()
        return        

        
    
    for cliente in clientes:
        try:
            dropdown_abrir = WebDriverWait(driver, 130).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="involve-select-0"]/div[1]/input'))
            )
            dropdown_abrir.click()
            dropdown_abrir.clear()
            time.sleep(2)
            print(f"Procurando cliente: {cliente}")
            dropdown_abrir.send_keys(cliente)
            time.sleep(2)
            dropdown_abrir.send_keys(Keys.ENTER)
            print(f"Cliente {cliente} processado com sucesso.")
        except TimeoutException:
            print(f"Não foi possível encontrar o dropdown para o cliente {cliente}.\n")
            continue  
        except Exception as e:
            print(f"Ocorreu um erro ao processar o cliente {cliente}: {e}")
            continue

        try:
            seta_aba_cliente = WebDriverWait(driver, 130).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/app/div[1]/ng-component/sitemapgroup-dashboard/ng-component/breadcrumb/div/div[1]/span[2]'))
            )
            time.sleep(1)
            seta_aba_cliente.click()
        except Exception as e:
            print(f" Erro ao abrir aba do cliente {cliente}: {e}")
            continue

        try:
            selecionar_menu_opçoes = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/app/div[1]/ng-component/sitemapgroup-dashboard/ng-component/breadcrumb/div/div[2]/div[1]/breadcrumb-menu/div'))
            )
            time.sleep(0.5)
            selecionar_menu_opçoes.click()
            time.sleep(1)
            lista_h3 = WebDriverWait(driver, 60).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@id, "cdk-overlay")]/div/div/div//h3'))
            )
            time.sleep(1)

            for i, elementos_h3 in enumerate(lista_h3):
                if "Area Vitals" in elementos_h3.text or "Fleet Status" in elementos_h3.text:
                    time.sleep(0.5)
                    elementos_h3.click()
                    print(f" Área Vitals/Fleet Status encontrada e clicada com sucesso para o cliente {cliente}.")
                    break

            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(1)

        except Exception as e:
            print(f" Erro ao clicar em Área Vitals/Fleet Status para o cliente {cliente}: {e}\n")
            continue

        try:
            WebDriverWait(driver, 15).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "cdk-overlay-backdrop"))
            )
        except TimeoutException:
            print(" O overlay demorou para desaparecer, tentando continuar mesmo assim.")

        try:
            system_status = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'menu-button'))
            )
            time.sleep(1)
            system_status.click()
            print(" Status do sistema clicado com sucesso.")
        except ElementClickInterceptedException:
            print(" Clique interceptado — aguardando 3 segundos e tentando novamente...")
            time.sleep(3)
            try:
                system_status.click()
                print(" Clique no status do sistema realizado na segunda tentativa.")
            except Exception as e:
                print(f" Erro ao tentar clicar novamente no status do sistema: {e}")
                continue
        except TimeoutException:
            print(" Não foi possível encontrar o status do sistema.\n")
            continue

        try:
            export = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//system-status-tile-v2//involve-datasource-export//button'))
            )
            time.sleep(1)
            export.click()
            print(" Exportando dados...")
        except TimeoutException:
            print(" Não foi possível encontrar o botão de exportação.\n")
            continue

        try:
            csv_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'CSV')]"))
            )
            time.sleep(1)
            csv_button.click()
            print(" Formato CSV selecionado com sucesso.")
        except TimeoutException:
            print(" Não foi possível encontrar o formato CSV.\n")
            continue

        time.sleep(1)
