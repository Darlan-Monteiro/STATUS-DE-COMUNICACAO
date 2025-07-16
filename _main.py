import pandas as pd
from processamento_dados import processar_dados
from dsp_automacao_selenium import web
from rfv_automacao_selenium import automacao_rfv

def atualizar_dados():
    automacao_rfv()  # Executa automação RFV
    
    # Processa os dados e retorna o caminho do arquivo e a lista de SNs que precisam de atualização
    caminho_saida, nao_atualizados_ultima_comunicacao = processar_dados()
    
    # Coleta os dados de última comunicação via automação web
    dh_ultimo_ping_dict = web(nao_atualizados_ultima_comunicacao)
    
    # Carrega a planilha
    ativos_atualizados = pd.read_excel(caminho_saida, dtype={'NºSÉRIE': str})
    
    # Garante que a coluna de datas esteja no formato datetime
    ativos_atualizados['Data Última Comunicação'] = pd.to_datetime(
        ativos_atualizados['Data Última Comunicação'], errors='coerce'
    )
    
    for sn, data_str in dh_ultimo_ping_dict.items():
        sn = str(sn).strip()

        try:
            data_dict = pd.to_datetime(data_str, errors='coerce', dayfirst=True)
            if pd.isna(data_dict):
                print(f"[AVISO] Data inválida para {sn}: '{data_str}'\n")
                continue
        except Exception as e:
            print(f"[ERRO] Falha ao converter data para {sn}: {e}\n")
            continue

        # Filtra as linhas onde o número de série contém o SN
        filtro_sn = ativos_atualizados['NºSÉRIE'].str.contains(sn, na=False)
        
        if filtro_sn.any():
            try:
                data_excel = ativos_atualizados.loc[filtro_sn, 'Data Última Comunicação'].iloc[0]

                # Se a célula está vazia ou a nova data é mais recente, atualiza
                if pd.isna(data_excel) or data_dict > data_excel:
                    ativos_atualizados.loc[filtro_sn, 'Data Última Comunicação'] = data_dict
                    print(f"[OK] {sn} → Data atualizada para {data_dict}")
                elif data_dict == data_excel:
                    print(f"[INFO] {sn} → Já está atualizada ({data_dict})")
                else:
                    print(f"[INFO] {sn} → Data na planilha ({data_excel}) é mais recente")

            except Exception as e:
                print(f"[ERRO] Ao acessar ou atualizar {sn}: {e}")
        else:
            print(f"[IGNORADO] {sn} → Não encontrado na planilha.")
    
    # Salva a planilha atualizada
    ativos_atualizados.to_excel(caminho_saida, index=False)
    print(f"\n✅ Planilha atualizada salva em: {caminho_saida}")

# Chamada principal
atualizar_dados()
