# 📡 Status de Comunicação (RPA)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)

## 📋 Sobre o Projeto

Este projeto é uma solução de **RPA (Robotic Process Automation)** desenvolvida para automatizar a atualização de dados de telemetria de ativos. O sistema elimina a verificação manual em múltiplos portais, garantindo a integridade da informação de "Última Comunicação" na base de dados mestra.

A automação consulta duas fontes de dados (Portais RFV e DSP), consolida as informações e atualiza uma planilha Excel local, priorizando sempre a data mais recente.

### ✨ Principais Funcionalidades

* **Gestão Automática de Drivers:** Verifica a versão do navegador Edge instalada e baixa o `msedgedriver` compatível automaticamente.
* **Coleta em Massa (RFV):** Acessa o portal RFV, itera sobre uma lista de clientes e exporta relatórios CSV.
* **Processamento ETL:** Unifica arquivos CSV, limpa dados e cruza informações com a base de ativos usando Pandas.
* **Coleta Pontual (DSP):** Realiza buscas específicas ("Item a Item") para ativos que não foram encontrados na coleta em massa.
* **Limpeza Automática:** Remove arquivos temporários após a execução para manter o ambiente organizado.

---

## 🛠️ Tecnologias Utilizadas

* **[Python](https://www.python.org/)** - Linguagem principal.
* **[Selenium](https://www.selenium.dev/)** - Automação Web.
* **[Pandas](https://pandas.pydata.org/)** & **[Polars](https://www.pola.rs/)** - Manipulação e análise de dados.
* **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)** - Web Scraping (para baixar drivers).
* **[Python-Dotenv](https://pypi.org/project/python-dotenv/)** - Gestão de variáveis de ambiente.

---

## 🚀 Como Executar

### Pré-requisitos

* Python 3.x instalado.
* Navegador **Microsoft Edge** instalado.
* Git instalado.

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU-USUARIO/status-de-comunicacao.git](https://github.com/SEU-USUARIO/status-de-comunicacao.git)
    cd status-de-comunicacao
    ```

2.  **Crie um ambiente virtual (Opcional, mas recomendado):**
    ```bash
    python -m venv venv
    # No Windows:
    venv\Scripts\activate
    # No Linux/Mac:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto e preencha com os seus caminhos locais:

    ```env
    # Caminhos de Perfil do Navegador (Para manter login salvo)
    caminho_user_rfv="C:\Users\SEU_USER\AppData\Local\Microsoft\Edge\User Data\Perfil_RFV"
    caminho_user_chorme="C:\Users\SEU_USER\AppData\Local\Microsoft\Edge\User Data\Perfil_DSP"

    # URLs dos Portais
    site_rfv="[https://url-do-portal-rfv.com](https://url-do-portal-rfv.com)"
    site_dsp="[https://url-do-portal-dsp.com](https://url-do-portal-dsp.com)"

    # Caminhos de Arquivos
    caminho_bdrfv="C:\Users\SEU_USER\Downloads\System Status*.csv"
    pasta_destino_rfv="./temp_rfv"
    caminho_ativosatt="Z:\Caminho\Para\Sua\Planilha_Final.xlsx"
    base_clientes="./input/clientes.xlsx"
    ```

5.  **Execute a automação:**
    ```bash
    python _main.py
    ```

---

## 📂 Estrutura do Projeto

```text
STATUS-DE-COMUNICACAO/
│
├── _main.py                    # Orquestrador: Inicia todo o fluxo
├── baixar_edge_atual.py        # Infra: Atualiza o driver do Edge
├── rfv_automacao_selenium.py   # Bot: Coleta dados do RFV
├── dsp_automacao_selenium.py   # Bot: Coleta dados do DSP
├── processamento_dados.py      # ETL: Trata dados e atualiza Excel




📄 Licença
Este projeto está sob a licença MIT - veja o arquivo LICENSE para detalhes.

Desenvolvido por Darlan Monteiro
├── deletar_arquivos.py         # Utils: Limpa arquivos CSV temporários
├── .gitignore                  # Arquivos ignorados pelo Git
└── README.md                   # Documentação do projeto
