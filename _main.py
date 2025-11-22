"""
Script principal (Orquestrador).
Este arquivo centraliza a execução de todo o processo de automação:
gerencia o driver, roda as automações do RFV e DSP, processa os dados e salva o Excel.
"""
    
import pandas as pd
from dsp_automacao_selenium import web
from deletar_arquivos import deletar_arquivos
from processamento_dados import processar_dados
from rfv_automacao_selenium import automacao_rfv
from baixar_edge_atual import gerenciar_edgedriver

def atualizar_dados():
    """
    Função que executa o fluxo sequencial de atualização.
    1. Verifica Driver -> 2. RFV -> 3. Processamento -> 4. DSP -> 5. Salva Excel.
    """
    # O gerenciar_edgedriver garante que o msedgedriver.exe esteja atualizado/instalado antes de iniciar a automação
    gerenciar_edgedriver()
    
    # Inicia a automação para processar os clientes no site RFV
    automacao_rfv()
    
    # Chama a função processar_dados do processamento_dados.py
    caminho_saida, nao_atualizados_ultima_comunicacao = processar_dados()
    
    # Coleta os dados de última comunicação via automação web DSP
    dh_ultimo_ping_dict = web(nao_atualizados_ultima_comunicacao)
    
    # Carrega a planilha
    ativos_atualizados = pd.read_excel(caminho_saida, dtype={'NºSÉRIE': str})
    
    # Garante que a coluna de datas esteja no formato datetime
    ativos_atualizados['Data Última Comunicação'] = pd.to_datetime(
        ativos_atualizados['Data Última Comunicação'], errors='coerce'
    )
    
    # Atualiza as datas na planilha com base nos dados coletados
    for sn, data_str in dh_ultimo_ping_dict.items():
        sn = str(sn).strip()
        # Converte a string de data para datetime
        try:
            data_dict = pd.to_datetime(data_str, errors='coerce', dayfirst=False)
            if pd.isna(data_dict):
                print(f"Data inválida para {sn}: '{data_str}'\n")
                continue
        except Exception as e:
            print(f"Falha ao converter data para {sn}: {e}\n")
            continue

        # Filtra as linhas onde o número de série contém o SN
        filtro_sn = ativos_atualizados['NºSÉRIE'].str.contains(sn, na=False)
        
        
        # Bloco para atualizar a Data Última Comunicação se a nova data for mais recente
        if filtro_sn.any():
            try:
                data_excel = ativos_atualizados.loc[filtro_sn, 'Data Última Comunicação'].iloc[0]
                # Se a célula está vazia ou a nova data é mais recente, atualiza
                if pd.isna(data_excel) or data_dict > data_excel:
                    ativos_atualizados.loc[filtro_sn, 'Data Última Comunicação'] = data_dict
                    print(f"{sn} - Data atualizada para {data_dict}")
                # Se as datas são iguais, informa que já está atualizada
                elif data_dict == data_excel:
                    print(f"{sn} - Já está atualizada ({data_dict})")
                # Se a data na planilha é mais recente, não faz nada
                else:
                    print(f"{sn} - Data na planilha ({data_excel}) é mais recente")
            except Exception as e: 
                print(f"Erro ao acessar ou atualizar {sn}: {e}")
        else:
            print(f"{sn} - Não encontrado na planilha.")   
    
    # Chama a função para deletar os arquivos .csv processados, com o objetivo de evitar acúmulo desnecessário na pasta destino_rfv
    deletar_arquivos()
    
    # Salva a planilha atualizada
    ativos_atualizados.to_excel(caminho_saida, index=False)
    print(f"\n Planilha atualizada salva em: {caminho_saida}")
    
if __name__ == "__main__":
    atualizar_dados() 