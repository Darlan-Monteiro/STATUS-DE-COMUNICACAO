import pandas as pd
from glob import glob
from dotenv import load_dotenv
import os

load_dotenv()
caminho_bdrfv = os.getenv('caminho_bdrfv')
caminho_bdativos = os.getenv('caminho_bdativos') 
caminho_ativosatt = os.getenv('caminho_ativosatt')  

def ler_base():
    arquivos = sorted(glob(caminho_bdrfv))
    if not arquivos:
        print("Nenhum arquivo encontrado na pasta especificada.")
        return None
    arquivos_concat = pd.concat((pd.read_excel(cont) for cont in arquivos), ignore_index=True)
    print(arquivos_concat)
    return arquivos_concat

def ler_planilha_ativos():
    caminho_ativos = caminho_bdativos
    aba_ativos = 'Ativos'
    try:
        planilha_ativos = pd.read_excel(caminho_ativos, sheet_name=aba_ativos)
        return planilha_ativos
    except ValueError:
        print(f"Arquivo {caminho_ativos} não encontrado.")
        return None
    
def remover_separador(separador):
    if isinstance(separador, str):
        return separador[-8:].strip()
    
