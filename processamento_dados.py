""" 
Código para processar os dados dos arquivos CSV exportados do RFV 
e atualizar a planilha de ativos. 
"""

import os
import shutil
import pandas as pd
from glob import glob
from pathlib import Path
from dotenv import load_dotenv

# Bloco que carrega as variáveis de ambiente do arquivo .env
load_dotenv()
parte_relativa = os.getenv('caminho_relativo_ativos')
pasta_usuario = Path.home()
caminho_bdrfv = os.getenv('caminho_bdrfv')
caminho_bdativos = pasta_usuario / parte_relativa
#caminho_bdativos = os.getenv('caminho_bdativos') 
caminho_ativosatt = os.getenv('caminho_ativosatt')  
pasta_destino_rfv = os.getenv('pasta_destino_rfv')

# Pega a pasta do usuário
user_docs = Path.home() / "Sotreq" / "Sol. Tec - Documentos" / "01 - Controle de Ativos"
# Caminho final da planilha de ativos
caminho_bdativos = user_docs / "2 - Ativos Cat Connect.xlsm"


def ler_base():
    """ 
    Função para ler os arquivos baixados do RFV e concatenar em um único DataFrame 
    """
    arquivos = sorted(glob(caminho_bdrfv))
    if not arquivos:
        print("Nenhum arquivo encontrado na pasta especificada")
        return None

    lista_df = [] # Lista para armazenar os df lidos
    # Loop para ler cada arquivo e adicionar à lista
    for arquivo in arquivos:
        try:
            df = pd.read_csv(arquivo, encoding='latin1', sep=',')
            print(f"Lido com sucesso: {arquivo} ({df.shape[0]} linhas, {df.shape[1]} colunas)")
            lista_df.append(df) # Adiciona o df à lista
            
        except Exception as e:
            print(f"Erro ao ler o arquivo {arquivo}: {e}")

    if not lista_df:
        print("Nenhuma base válida foi carregada")
        return None

    # retorna todos os df concatenados
    return pd.concat(lista_df, ignore_index=True) 


def ler_planilha_ativos():
    """ 
    Função para ler a planilha de ativos Cat Connect e pegar só a aba Ativos
    """
    caminho_ativos = caminho_bdativos
    aba_ativos = 'Ativos'
    
    # Lê a planilha e retorna o df
    try:
        planilha_ativos = pd.read_excel(caminho_ativos, sheet_name=aba_ativos)
        return planilha_ativos
    
    except ValueError:
        print(f"Arquivo {caminho_ativos} não encontrado")
        return None
    
    
def remover_separador(separador):
    """ 
    Função para remover os 8 últimos caracteres de uma string
    """
    if isinstance(separador, str):
        return separador[-8:].strip()
    
    
def processar_dados():
    """ 
    Função principal para processar os dados.
    Move arquivos, lê bases, compara e atualiza a planilha
    """
   
    print("\nIniciando o processamento dos dados")
    
    # Bloco que move os arquivos CSV da pasta de downloads para a pasta destino_rfv
    pasta_origem = Path.home() / "Downloads"
    pasta_destino = Path(pasta_destino_rfv)    
    pasta_destino.mkdir(parents=True, exist_ok=True)

    for arquivo in pasta_origem.iterdir():
        if arquivo.is_file() and arquivo.name.lower().endswith('.csv') and 'system status' in arquivo.name.lower():
            destino = pasta_destino / arquivo.name
            try:
                shutil.move(str(arquivo), str(destino))
                print(f"Movido: {arquivo.name}")
            except Exception as e:
                print(f"Erro ao mover {arquivo.name}: {e}")


    # Chamando as funções para ler as bases e verificando se há erros
    bases_concat = ler_base()
    ativos = ler_planilha_ativos()
    coluna_bdconcat = 'Unit Name'
    coluna_bdativos = 'NºSÉRIE'
    
    # verificações de erro
    if bases_concat is None or ativos is None:
        print('Erro! Base de dados vazia')
        exit()
    
    if coluna_bdconcat not in bases_concat.columns or coluna_bdativos not in ativos.columns: 
        print("Colunas não encontradas em um dos arquivos")
        exit()
    
    # Bloco para verificar quais assets não estão presentes na coluna NºSÉRIE    
    asset_name_modificado = bases_concat[coluna_bdconcat].astype(str).apply(remover_separador)
    num_series = ativos[coluna_bdativos].astype(str)
    
    # Bloco para modificar a coluna NºSÉRIE aplicando split('/') e removendo espaços.
    # O objetivo é separar números de série que estão juntos na mesma célula, como 12345/67890
    num_series_modificado = set()
    for num in num_series:
        partes = num.split('/')
        for serie in partes:
            num_series_modificado.add(serie.strip())
            
    # Bloco para comparar as duas listas e identificar quais assets não estão presentes em NºSÉRIE 
    lista_nao_contem = []
    for asset_name in asset_name_modificado:
        for n_serie in num_series_modificado:
            if asset_name in n_serie:
                print(f'{asset_name} está presente em NºSÉRIE')
                break
            
        else:
            print(f'{asset_name} NÃO está presente em NºSÉRIE')
            lista_nao_contem.append(asset_name)
     
    # Bloco para atualizar a coluna Data Última Comunicação na planilha de ativos        
    ativos['Data Última Comunicação'] = ativos['Data Última Comunicação'].replace(['-', '', 'NaT'], pd.NaT)
    ativos['Data Última Comunicação'] = pd.to_datetime(ativos['Data Última Comunicação'], errors='coerce') 
    bases_concat['Sample Time'] = pd.to_datetime(bases_concat['Sample Time'], errors='coerce')
    
    # Bloco para comparar as datas e atualizar a planilha de ativos 
    nao_atualizados_ultima_comunicacao = []
    for i, linha in bases_concat.iterrows():
        # Aplica a função para remover os separadores para pegar os últimos 8 caracteres
        asset_name = remover_separador(linha[coluna_bdconcat])
        sample_time = linha['Sample Time']
        ativos_correspondentes = ativos[ativos[coluna_bdativos].astype(str).str.contains(asset_name, na=False)]
        # loop para verificar e atualizar as datas
        for  j, ativo_linha in ativos_correspondentes.iterrows():
            if sample_time > ativo_linha['Data Última Comunicação']:
                ativos.at[j, 'Data Última Comunicação'] = sample_time
                print(f'{ativo_linha[coluna_bdativos]} atuializado para {sample_time}\n')
            
            else:
                print(f'{ativo_linha[coluna_bdativos]}:{sample_time} NÃO é maior que {ativo_linha["Data Última Comunicação"]}. \n')
                nao_atualizados_ultima_comunicacao.append(asset_name)
                
                
    # Bloco para exibir os resultados via print        
    print(ativos[['NºSÉRIE', 'Data Última Comunicação', 'Data Último Envio de Dados']])
    print("\n\nAssets não atualizados para Data Última Comunicação:")
    print(nao_atualizados_ultima_comunicacao)
    print(len(nao_atualizados_ultima_comunicacao)) # quantidade de ativos que não foram atualizados
    print("\n\nAssets que não contém na lista:")
    print(lista_nao_contem)
    
    # Bloco para salvar a planilha atualizada
    caminho_saida = caminho_ativosatt
    ativos.to_excel(caminho_saida, index=False)
    print(f"\n\n Tabela atualizada salva em Sol. Tec - Documentos\Projeto Status de Comunicação\ com o nome de: {caminho_saida}")
    return caminho_saida, nao_atualizados_ultima_comunicacao