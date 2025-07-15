import pandas as pd
from processamento_dados import processar_dados
from dsp_automacao_selenium import web
from rfv_automacao_selenium import automacao_rfv

def atualizar_dados():
    
    automacao_rfv()  # chama a automação rfv
    
    # executa a função para processamento dos dados
    caminho_saida, nao_atualizados_ultima_comunicacao = processar_dados()
    
    # chama a automação web com a lista de sns que precisam de atualização
    dh_ultimo_ping_dict = web(nao_atualizados_ultima_comunicacao)
    
    # carrega a planilha salva
    ativos_atualizados = pd.read_excel(caminho_saida, dtype={'NºSÉRIE': str})
    
    # converte a coluna 'Data Última Comunicação' para datetime, com tratamento de erros
    ativos_atualizados['Data Última Comunicação'] = pd.to_datetime(ativos_atualizados['Data Última Comunicação'], errors='coerce')
    
    for sn, data_str in dh_ultimo_ping_dict.items():
        # transforma em string e tira os espaços
        sn = str(sn).strip()
        
        # tenta converter a data do dicionário para datetime
        try:
            data_dict = pd.to_datetime(data_str, errors='coerce')
            if pd.isna(data_dict): # isna verifica se é inválido
                print(f"Data inválida para {sn}: '{data_str}'. Atualização ignorada.")
                continue

        except Exception as e:
            print(f"Erro ao converter data para {sn}. Atualização ignorada.")
            continue
        
        # verifica se o sn está contido em algum valor na coluna 'NºSÉRIE'
        nserie = ativos_atualizados['NºSÉRIE'].str.contains(sn) #contains procurar o valor na coluna n de serie
        if nserie.any(): #se o sn estiver na planilha, então vai retornar true e seguir o if
            data_excel = ativos_atualizados.loc[nserie, 'Data Última Comunicação'].iloc[0] #iloc pega o primeiro valor que aparecer
             
            # compara as datas e atualiza se a do dicionário for mais recente
            if pd.isna(data_excel) or data_dict > data_excel:
                ativos_atualizados.loc[nserie, 'Data Última Comunicação'] = data_dict
                print(f"{sn}: Data atualizada para {data_dict}")
            elif data_dict == data_excel:
                print(f"{sn}: Data na planilha já está atualizada ({data_dict}).")
            else:
                print(f"{sn}: Data na planilha ({data_excel}) é mais recente ou igual à do dicionário ({data_dict}).")
        else:
            print(f"{sn}: Número de série não encontrado na planilha. Atualização ignorada.")
    
    # salva a planilha novamente com as atualizações
    ativos_atualizados.to_excel(caminho_saida, index=False)
    print(f"\nTabela final atualizada salva em {caminho_saida}")

atualizar_dados()
