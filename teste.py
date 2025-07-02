import os
import shutil

# caminho da pasta de origem
pasta_origem = os.path.expanduser('~/Downloads')

# caminho da pasta de destino
pasta_destino = r'C:\Users\700543\Sotreq\Darlan Monteiro - Desenvolvimento\status_project\STATUS-DE-COMUNICACAO\bd_rfv'  # alterarr caminho

# garante que a pasta de destino exista
os.makedirs(pasta_destino, exist_ok=True)

# percorre os arquivos na pasta de origem
for arquivo in os.listdir(pasta_origem):
    if arquivo.endswith('.xlsx') and 'system status' in arquivo.lower():
        origem = os.path.join(pasta_origem, arquivo)
        destino = os.path.join(pasta_destino, arquivo)

        # move o arquivo
        shutil.move(origem, destino)
        print(f'Movido: {arquivo}')
