
    # def login():
#     cws = input("Insira o Seu CWS: ")
#     senha = input("Insira a Sua Senha: ")
#     return cws, senha
    
    # cws, senha = login()
    # print(f"Tentando login com o CWS: {cws}")
    
    # try:
    #     campo_cws = WebDriverWait(driver, 180).until(
    #         EC.visibility_of_element_located((By.ID, 'signInName'))
    #     )
    #     campo_cws.clear()
    #     campo_cws.send_keys(cws)
        
    #     botao_continuar = driver.find_element(By.ID, 'next')
    #     botao_continuar.click()

    #     print("Verificando se a senha é necessária...")
        
    #     try:
    #         campo_senha = WebDriverWait(driver, 5).until(
    #             EC.visibility_of_element_located((By.ID, 'i0118'))
    #         )

    #         print("Senha necessária. Inserindo senha...")
    #         campo_senha.clear()
    #         campo_senha.send_keys(senha)
    #         campo_senha.send_keys(Keys.ENTER)

    #         print("Verificando o login após a senha...")
    #         WebDriverWait(driver, 15).until(
    #             EC.visibility_of_element_located((By.XPATH, '//*[@id="involve-select-0"]/div[1]/input'))
    #         )
            
    #     except TimeoutException:
    #         print("Campo de senha não encontrado. Verificando login automático...")
    #         WebDriverWait(driver, 15).until(
    #             EC.visibility_of_element_located((By.XPATH, '//*[@id="involve-select-0"]/div[1]/input'))
    #         )
    #         print("Login automático (sem senha) detectado.")
    #     print(" Login realizado com sucesso!")

    # except TimeoutException:

    #     print("\n" + "="*40)
    #     print("ERRO! o Login falhou.")
    #     print("   Verifique seu CWS/Senha.")
    #     print("   Encerrando o programa.")
    #     print("="*40 + "\n")
        
    #     driver.quit()
    #     return        
