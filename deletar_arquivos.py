""" 
Criei este script para deletar os arquivos .csv que foram processados e estão na pasta destino_rfv,
evitando o acúmulo desnecessário de arquivos.
"""

import os
import glob
from dotenv import load_dotenv

# ---- ETAPA 5 ----:

# Função para deletar os arquivos .csv processados
def deletar_arquivos():
    """ 
    Função para deletar os arquivos .csv processados da pasta de destino.
    Verifica se a pasta existe e remove todos os arquivos com extensão .csv.
    """
    print("\n Iniciando limpeza dos arquivos CSV processados")
    load_dotenv()
    pasta_destino_rfv = os.getenv('pasta_destino_rfv')
    
    if not pasta_destino_rfv:
        print(" Variável 'pasta_destino_rfv' não encontrada no .env. Pulando limpeza.")
        return
    
    # Usa glob para encontrar todos os arquivos .csv na pasta destino_rfv
    var_glob = os.path.join(pasta_destino_rfv, '*.csv')
    arquivos_para_deletar = glob.glob(var_glob)
    if not arquivos_para_deletar:
        print("Nenhum arquivo .csv encontrado para limpar.")
        return
    
    print(f"Encontrados {len(arquivos_para_deletar)} arquivos .csv para deletar...")
    
    # Loop para deletar cada arquivo encontrado
    for arquivo in arquivos_para_deletar:
        try:
            os.remove(arquivo)
            print(f"Deletado: {arquivo}")
        except Exception as e:
            print(f"Erro ao deletar {arquivo}: {e}")
    print("Limpeza concluída\n")