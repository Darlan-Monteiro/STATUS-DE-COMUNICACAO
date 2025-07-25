import pandas as pd
from glob import glob
from dotenv import load_dotenv
import os
import shutil
from pathlib import Path

load_dotenv()
caminho_bdrfv = os.getenv('caminho_bdrfv')
caminho_bdativos = os.getenv('caminho_bdativos') 
caminho_ativosatt = os.getenv('caminho_ativosatt')  
pasta_destino_rfv = os.getenv('pasta_destino_rfv')  # alterado para pasta_destino_rfv

# def ler_base(): # funcão para ler a base baixada do RFV e unificar todas elas.
#     arquivos = sorted(glob(caminho_bdrfv))
#     if not arquivos:
#         print("Nenhum arquivo encontrado na pasta especificada.")
#         return None
#     arquivos_concat = pd.concat((pd.read_csv(cont, encoding='latin1', sep=';') for cont in arquivos), ignore_index=True)
#     print(arquivos_concat)
#     return arquivos_concat


def ler_base():
    arquivos = sorted(glob(caminho_bdrfv))
    if not arquivos:
        print("Nenhum arquivo encontrado na pasta especificada.")
        return None

    lista_df = []
    for arquivo in arquivos:
        try:
            df = pd.read_csv(arquivo, encoding='latin1', sep=',')
            print(f"✅ Lido com sucesso: {arquivo} ({df.shape[0]} linhas, {df.shape[1]} colunas)")
            lista_df.append(df)
        except Exception as e:
            print(f"❌ Erro ao ler o arquivo {arquivo}: {e}")

    if not lista_df:
        print("❗ Nenhuma base válida foi carregada.")
        return None

    return pd.concat(lista_df, ignore_index=True)



def ler_planilha_ativos(): # Função para ler a planilha "2 - Ativos Cat Connect" e pegar só a aba "Ativos".
    caminho_ativos = caminho_bdativos
    aba_ativos = 'Ativos'
    try:
        planilha_ativos = pd.read_excel(caminho_ativos, sheet_name=aba_ativos)
        return planilha_ativos
    except ValueError:
        print(f"Arquivo {caminho_ativos} não encontrado.")
        return None
    
def remover_separador(separador): # função que tem como objetivo remover os 8 últimos caracteres de uma string.
    if isinstance(separador, str):
        return separador[-8:].strip()
    
def processar_dados(): # função principal deste código
    
    # caminho da pasta de origem
    pasta_origem = Path.home() / "Downloads"
    pasta_destino = Path(pasta_destino_rfv)
    pasta_destino.mkdir(parents=True, exist_ok=True)

    # percorre os arquivos na pasta de origem
    for arquivo in pasta_origem.iterdir():
        if arquivo.is_file() and arquivo.name.lower().endswith('.csv') and 'system status' in arquivo.name.lower():
            destino = pasta_destino / arquivo.name
            try:
                shutil.move(str(arquivo), str(destino))
                print(f"✅ Movido: {arquivo.name}")
            except Exception as e:
                print(f"❌ Erro ao mover {arquivo.name}: {e}")

    
    bases_concat = ler_base()
    ativos = ler_planilha_ativos()
    coluna_bdconcat = 'Unit Name'
    coluna_bdativos = 'NºSÉRIE'
    
    if bases_concat is None or ativos is None:
        print('Erro! Base de dados vazia')
        exit()
    
    if coluna_bdconcat not in bases_concat.columns or coluna_bdativos not in ativos.columns: 
        print("Colunas não encontradas em um dos arquivos.")
        exit()
        
    asset_name_modificado = bases_concat[coluna_bdconcat].astype(str).apply(remover_separador)
    num_series = ativos[coluna_bdativos].astype(str)
    
    num_series_modificado = set()
    
    for num in num_series:
        partes = num.split('/')
        for serie in partes:
            num_series_modificado.add(serie.strip())
    
    lista_nao_contem = []

    for asset_name in asset_name_modificado:
        for n_serie in num_series_modificado:
            if asset_name in n_serie:
                print(f'{asset_name} está presente em NºSÉRIE.')
                break
        else:
            print(f'{asset_name} NÃO está presente em NºSÉRIE.')
            lista_nao_contem.append(asset_name)
            
    ativos['Data Última Comunicação'] = ativos['Data Última Comunicação'].replace(['-', '', 'NaT'], pd.NaT)
    ativos['Data Última Comunicação'] = pd.to_datetime(ativos['Data Última Comunicação'], errors='coerce') 
    bases_concat['Sample Time'] = pd.to_datetime(bases_concat['Sample Time'], errors='coerce')
    
    
    nao_atualizados_ultima_comunicacao = []
    for i, linha in bases_concat.iterrows():
        asset_name = remover_separador(linha[coluna_bdconcat])
        sample_time = linha['Sample Time']
        ativos_correspondentes = ativos[ativos[coluna_bdativos].astype(str).str.contains(asset_name, na=False)]

        for  j, ativo_linha in ativos_correspondentes.iterrows():
            if sample_time > ativo_linha['Data Última Comunicação']:
                ativos.at[j, 'Data Última Comunicação'] = sample_time
                print(f'{ativo_linha[coluna_bdativos]} atuializado para {sample_time}\n')
            
            else:
                print(f'{ativo_linha[coluna_bdativos]}:{sample_time} NÃO é maior que {ativo_linha["Data Última Comunicação"]}. \n')
                nao_atualizados_ultima_comunicacao.append(asset_name)
            
    print(ativos[['NºSÉRIE', 'Data Última Comunicação', 'Data Último Envio de Dados']])
    print("\n\nAssets não atualizados para Data Última Comunicação:")
    print(nao_atualizados_ultima_comunicacao)
    print("\n\nAssets que não contém na lista:")
    print(lista_nao_contem)
    
    caminho_saida = caminho_ativosatt
    ativos.to_excel(caminho_saida, index=False)
    print(f"\n\nTabela atualizada salva em Sol. Tec - Documentos\Projeto Status de Comunicação\ com o nome de: {caminho_saida}")
    return caminho_saida, nao_atualizados_ultima_comunicacao