from pathlib import Path

# Pega a pasta do usuário
user_docs = Path.home() / "Sotreq" / "Sol. Tec - Documentos" / "01 - Controle de Ativos"

# Caminho final
caminho_bdativos = user_docs / "2 - Ativos Cat Connect.xlsm"

print(caminho_bdativos)
