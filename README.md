# GrafiCalc 📊 A Linguagem de Programação para Análise de Dados na Web

GrafiCalc é uma aplicação web completa que implementa uma linguagem de programação de alto nível, em português, focada em análise e visualização de dados de forma rápida e interativa. A plataforma permite que utilizadores façam o upload de seus próprios ficheiros de dados (.csv ou .xlsx) e utilizem comandos simples para inspecionar os dados, realizar cálculos estatísticos e gerar gráficos diretamente no navegador.

Este projeto foi construído com fins didáticos para demonstrar a criação de uma linguagem do zero (análise léxica e sintática com PLY) e sua integração com um framework web como o Django.

---

## 📋 Índice

* [Principais Funcionalidades](#-principais-funcionalidades)
* [Tecnologias Utilizadas](#-tecnologias-utilizadas)
* [Começando: Instalação e Execução](#-começando-instalação-e-execução)
* [Documentação da Linguagem GrafiCalc](#-documentação-da-linguagem-graficalc)
    * [CARREGAR ARQUIVO](#1-carregar-arquivo)
    * [MOSTRAR DADOS](#2-mostrar-dados)
    * [CALCULAR](#3-calcular)
    * [PLOTAR GRÁFICO](#4-plotar-gráfico)
* [Exemplo Completo de Utilização](#-exemplo-completo-de-utilização)
* [Estrutura do Projeto](#-estrutura-do-projeto)
---

## ✨ Principais Funcionalidades

* **Linguagem de Programação em Português:** Comandos simples e intuitivos que abstraem a complexidade das bibliotecas de análise de dados.
* **Interface Web Interativa:** Um ambiente de desenvolvimento online (IDE) simples onde os comandos podem ser escritos e os resultados (tabelas e gráficos) são exibidos instantaneamente.
* **Upload de Ficheiros:** Suporte para que o utilizador envie seus próprios conjuntos de dados nos formatos `.csv` e `.xlsx`.
* **Geração de Gráficos:** Criação de gráficos de barras e de linhas para visualização de dados, com opção de download em formato `.png`.
* **Cálculos Estatísticos:** Funções para calcular rapidamente `MEDIA`, `MEDIANA` e `MODA` de colunas específicas.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3
* **Framework Web:** Django 4+
* **Motor da Linguagem:** PLY (Python Lex-Yacc)
* **Análise de Dados:** Pandas
* **Geração de Gráficos:** Matplotlib
* **Cálculos Estatísticos:** SciPy

---

## 🚀 Começando: Instalação e Execução

Para executar este projeto localmente, siga os passos abaixo.

### Pré-requisitos

* Python 3.8 ou superior
* Pip (gerenciador de pacotes do Python)

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/MiVinicius/GrafiCalc](https://github.com/MiVinicius/GrafiCalc.git)
    cd graficalc_project
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Cria o ambiente
    python -m venv venv

    # Ativa no Windows
    .\venv\Scripts\activate

    # Ativa no macOS/Linux
    source venv/bin/activate
    ```

5.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Aplique as migrações do Django:**
    *(Necessário para o sistema de sessões funcionar)*
    ```bash
    python manage.py migrate
    ```

7.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

8.  Abra o seu navegador e vá até **`http://127.0.0.1:8000/`**. A interface da GrafiCalc estará pronta para ser usada!

---

## 📖 Documentação da Linguagem GrafiCalc

### 1. CARREGAR ARQUIVO
Carrega os dados do ficheiro enviado pela interface para uma variável. **Deve ser sempre o primeiro comando.**

**Sintaxe:** `CARREGAR ARQUIVO COMO <nome_da_variavel>`
**Exemplo:** `CARREGAR ARQUIVO COMO dados_de_vendas`

### 2. MOSTRAR DADOS
Exibe as primeiras 5 linhas de uma variável de dados já carregada.

**Sintaxe:** `MOSTRAR DADOS DE <nome_da_variavel>`
**Exemplo:** `MOSTRAR DADOS DE dados_de_vendas`

### 3. CALCULAR
Realiza cálculos estatísticos (`MEDIA`, `MEDIANA`, `MODA`) numa coluna.

**Sintaxe:** `CALCULAR <tipo_de_calculo> DA COLUNA "<nome_da_coluna>" DE <nome_da_variavel>`
**Exemplo:** `CALCULAR MEDIA DA COLUNA "Total" DE dados_de_vendas`

### 4. PLOTAR GRÁFICO
Gera um gráfico de `BARRAS` ou `LINHAS`. A cláusula `SALVAR COMO` é opcional.

**Sintaxe:**
PLOTAR GRAFICO DE <tipo> COM EIXO_X "<col_x>" E EIXO_Y "<col_y>" DE <variavel> [SALVAR COMO "<arquivo.png>"]

**Exemplos:**
**Gráfico simples para visualização**

PLOTAR GRAFICO DE BARRAS COM EIXO_X "Produto" E EIXO_Y "Quantidade" DE dados_de_vendas

**Gráfico para um possível download**

PLOTAR GRAFICO DE LINHAS COM EIXO_X "Mes" E EIXO_Y "Faturamento" DE dados_de_vendas SALVAR COMO "faturamento_mensal.png"

---

## 💡 Exemplo Completo de Utilização

1.  **Faça o upload** de um ficheiro `.csv` com colunas `Mes`, `Receita` e `Despesas`.
2.  **Escreva o seguinte código** na interface:

    ```
    # Carrega o arquivo para a variável 'financeiro'
    CARREGAR ARQUIVO COMO financeiro

    # Verifica se os dados foram carregados corretamente
    MOSTRAR DADOS DE financeiro

    # Calcula a receita média mensal
    CALCULAR MEDIA DA COLUNA "Faturamento" DE financeiro

    # Cria um gráfico para visualizar o Faturamento ao longo dos meses
    PLOTAR GRAFICO DE LINHAS COM EIXO_X "Mes" E EIXO_Y "Faturamento" DE financeiro SALVAR COMO "relatorio_f.png"
    ```
3.  **Clique em "Executar"** para ver todos os resultados, incluindo a tabela e o gráfico.

---

## 📁 Estrutura do Projeto

```text
graficalc/
├── venv/
├── graficalc_project/
│   ├── init.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── interpreter/
│   ├── migrations/
│   ├── static/
│   │    └── interpreter/
│   │         └── css/
│   │              └── style.css
│   ├── templates/
│   │    └── interpreter/
│   │         └── interface.html
│   ├── init.py
│   ├── admin.py
│   ├── apps.py
│   ├── graficalc_engine.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── requirements.txt
├── manage.py
└── README.md
```