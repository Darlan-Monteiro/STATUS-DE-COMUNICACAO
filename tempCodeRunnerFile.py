            # Localizar o texto "Area Vitals"
            area_vitals = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[text()="Area Vitals"]'))
            )

            # Subir para o container e encontrar o involve-icon anterior (a seta)
            seta_area_vitals = area_vitals.find_element(By.XPATH, './preceding-sibling::involve-icon')

            # Scroll até o elemento e clicar com JavaScript (por ser SVG)
            driver.execute_script("arguments[0].scrollIntoView(true);", seta_area_vitals)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", seta_area_vitals)

            print("Seta ao lado de 'Area Vitals' clicada com sucesso.")

        except Exception as e:
            print(f"Erro ao clicar na seta de 'Area Vitals': {e}")