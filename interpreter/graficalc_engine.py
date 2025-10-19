import ply.lex as lex
import ply.yacc as yacc
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import os
import io
import base64

# --- Memória da Linguagem ---
# Este dicionário irá armazenar os dataframes carregados pelo utilizador.
# A chave será o nome da variável (ex: 'vendas') e o valor será o dataframe do pandas.
variaveis = {}

# --- Armazenamento de Resultados ---
# Uma lista para guardar os resultados de cada comando executado.
# Isso permite-nos processar múltiplos comandos e retornar todos os resultados.
resultados_execucao = []

# -----------------------------------------------------------------------------
# LEXER 
# -----------------------------------------------------------------------------
reserved = {
    'CARREGAR': 'CARREGAR', 'DADOS': 'DADOS', 'DE': 'DE', 'COMO': 'COMO',
    'MOSTRAR': 'MOSTRAR', 'CALCULAR': 'CALCULAR', 'MEDIA': 'MEDIA',
    'MEDIANA': 'MEDIANA', 'MODA': 'MODA', 'DA': 'DA', 'COLUNA': 'COLUNA',
    'PLOTAR': 'PLOTAR', 'GRAFICO': 'GRAFICO', 'BARRAS': 'BARRAS',
    'LINHAS': 'LINHAS', 'COM': 'COM', 'EIXO_X': 'EIXO_X', 'EIXO_Y': 'EIXO_Y',
    'E': 'E', 'SALVAR': 'SALVAR', 'ARQUIVO': 'ARQUIVO',
}
tokens = ['ID', 'STRING'] + list(reserved.values())

def t_STRING(t):
    r'\"[^\"]*\"'
    t.value = t.value[1:-1]
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.upper(), 'ID')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    error_msg = f"Caractere ilegal encontrado: '{t.value[0]}'"
    resultados_execucao.append({'type': 'error', 'content': error_msg})
    t.lexer.skip(1)

lexer = lex.lex()

# -----------------------------------------------------------------------------
# PARSER com LÓGICA DE EXECUÇÃO
# -----------------------------------------------------------------------------

def p_programa(p):
    '''
    programa : comando
             | programa comando
    '''
    pass

def p_comando_mostrar(p):
    'comando : MOSTRAR DADOS DE ID'
    nome_variavel = p[4]

    if nome_variavel not in variaveis:
        msg = f"Erro: A variável de dados '{nome_variavel}' não existe."
        resultados_execucao.append({'type': 'error', 'content': msg})
        return

    try:
        df = variaveis[nome_variavel]
        # Pega nas primeiras 5 linhas com o método head() do pandas
        df_head = df.head()
        
        # Converte o dataframe para uma tabela HTML.
        tabela_html = df_head.to_html(classes='data-table', border=0, index=False, justify='left')
        
        # Adiciona o resultado como um novo tipo: 'table'
        resultados_execucao.append({
            'type': 'table', 
            'content': tabela_html,
            'variable_name': nome_variavel
        })

    except Exception as e:
        msg = f"Ocorreu um erro ao tentar mostrar os dados: {e}"
        resultados_execucao.append({'type': 'error', 'content': msg})

def p_comando_carregar(p):
    'comando : CARREGAR DADOS DE STRING COMO ID'
    nome_ficheiro = p[4]
    nome_variavel = p[6]
    try:
        if nome_ficheiro.endswith('.csv'):
            df = pd.read_csv(nome_ficheiro)
        elif nome_ficheiro.endswith('.xlsx'):
            df = pd.read_excel(nome_ficheiro)
        else:
            raise ValueError("Formato de ficheiro não suportado. Use .csv ou .xlsx")

        variaveis[nome_variavel] = df
        msg = f"Dados do ficheiro '{nome_ficheiro}' carregados com sucesso na variável '{nome_variavel}'."
        resultados_execucao.append({'type': 'message', 'content': msg})

    except FileNotFoundError:
        msg = f"Erro: O ficheiro '{nome_ficheiro}' não foi encontrado."
        resultados_execucao.append({'type': 'error', 'content': msg})
    except Exception as e:
        msg = f"Ocorreu um erro ao carregar o ficheiro: {e}"
        resultados_execucao.append({'type': 'error', 'content': msg})

def p_comando_calcular(p):
    'comando : CALCULAR tipo_calculo DA COLUNA STRING DE ID'
    tipo_calculo = p[2]
    nome_coluna = p[5]
    nome_variavel = p[7]

    if nome_variavel not in variaveis:
        msg = f"Erro: A variável de dados '{nome_variavel}' não existe."
        resultados_execucao.append({'type': 'error', 'content': msg})
        return

    df = variaveis[nome_variavel]
    if nome_coluna not in df.columns:
        msg = f"Erro: A coluna '{nome_coluna}' não existe na variável '{nome_variavel}'."
        resultados_execucao.append({'type': 'error', 'content': msg})
        return

    try:
        coluna = df[nome_coluna].dropna() # Remove valores nulos para cálculos
        resultado = 0
        if tipo_calculo.upper() == 'MEDIA':
            resultado = coluna.mean()
        elif tipo_calculo.upper() == 'MEDIANA':
            resultado = coluna.median()
        elif tipo_calculo.upper() == 'MODA':
            # A moda pode retornar múltiplos valores, pegamos o primeiro.
            resultado = stats.mode(coluna, keepdims=False)[0]

        msg = f"A {tipo_calculo} da coluna '{nome_coluna}' é: {resultado:.2f}"
        resultados_execucao.append({'type': 'message', 'content': msg})

    except Exception as e:
        msg = f"Erro ao calcular a {tipo_calculo}: {e}"
        resultados_execucao.append({'type': 'error', 'content': msg})


def p_tipo_calculo_media(p):
    'tipo_calculo : MEDIA'
    p[0] = p[1]

def p_tipo_calculo_mediana(p):
    'tipo_calculo : MEDIANA'
    p[0] = p[1]

def p_tipo_calculo_moda(p):
    'tipo_calculo : MODA'
    p[0] = p[1]

def p_comando_plotar(p):
    '''
    comando : PLOTAR GRAFICO DE tipo_grafico COM EIXO_X STRING E EIXO_Y STRING DE ID SALVAR COMO STRING
            | PLOTAR GRAFICO DE tipo_grafico COM EIXO_X STRING E EIXO_Y STRING DE ID
    '''
    
    # Verificamos o tamanho de 'p' para saber qual regra foi usada.
    # Se len(p) for 16, a regra longa (com SALVAR COMO) foi usada.
    # Se len(p) for 13, a regra curta (sem SALVAR COMO) foi usada.
    
    if len(p) == 16: # Regra com 'SALVAR COMO'
        tipo_grafico = p[4]
        coluna_x = p[7]
        coluna_y = p[10]
        nome_variavel = p[12]
        nome_ficheiro_saida = p[15]
    else: # Regra sem 'SALVAR COMO' (len(p) == 13)
        tipo_grafico = p[4]
        coluna_x = p[7]
        coluna_y = p[10]
        nome_variavel = p[12]
        nome_ficheiro_saida = "grafico_gerado.png" # Usamos um nome padrão

    if nome_variavel not in variaveis:
        msg = f"Erro: A variável de dados '{nome_variavel}' não existe."
        resultados_execucao.append({'type': 'error', 'content': msg})
        return

    df = variaveis[nome_variavel]
    if coluna_x not in df.columns or coluna_y not in df.columns:
        msg = f"Erro: Uma ou ambas as colunas '{coluna_x}', '{coluna_y}' não existem em '{nome_variavel}'."
        resultados_execucao.append({'type': 'error', 'content': msg})
        return

    try:
        plt.figure() 
        if tipo_grafico.upper() == 'BARRAS':
            plt.bar(df[coluna_x], df[coluna_y])
        elif tipo_grafico.upper() == 'LINHAS':
            plt.plot(df[coluna_x], df[coluna_y])

        plt.xlabel(coluna_x)
        plt.ylabel(coluna_y)
        plt.title(f'Gráfico de {tipo_grafico.capitalize()} de {coluna_y} por {coluna_x}')
        plt.grid(True)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        resultados_execucao.append({'type': 'image', 'content': image_base64, 'filename': nome_ficheiro_saida})

    except Exception as e:
        msg = f"Ocorreu um erro ao gerar o gráfico: {e}"
        resultados_execucao.append({'type': 'error', 'content': msg})


def p_comando_carregar_arquivo(p):
    'comando : CARREGAR ARQUIVO COMO ID'
    nome_variavel = p[4]

    # A magia acontece aqui: o caminho do ficheiro não virá do comando,
    # mas sim de um argumento que a nossa view irá passar.
    # Usaremos uma variável global temporária para isso.

    if not caminho_arquivo_upload_temporario:
        msg = "Erro: O comando 'CARREGAR ARQUIVO' só pode ser usado com um upload de ficheiro."
        resultados_execucao.append({'type': 'error', 'content': msg})
        return

    try:
        if caminho_arquivo_upload_temporario.endswith('.csv'):
            df = pd.read_csv(caminho_arquivo_upload_temporario)
        elif caminho_arquivo_upload_temporario.endswith('.xlsx'):
            df = pd.read_excel(caminho_arquivo_upload_temporario)
        else:
            raise ValueError("Formato de ficheiro não suportado. Use .csv ou .xlsx")

        variaveis[nome_variavel] = df
        msg = f"Ficheiro enviado com sucesso e carregado na variável '{nome_variavel}'."
        resultados_execucao.append({'type': 'message', 'content': msg})

    except Exception as e:
        msg = f"Ocorreu um erro ao carregar o ficheiro enviado: {e}"
        resultados_execucao.append({'type': 'error', 'content': msg})


def p_tipo_grafico_barras(p):
    'tipo_grafico : BARRAS'
    p[0] = p[1]

def p_tipo_grafico_linhas(p):
    'tipo_grafico : LINHAS'
    p[0] = p[1]

def p_error(p):
    if p:
        msg = f"Erro de sintaxe no token '{p.value}' (tipo: {p.type}) na linha {p.lineno}"
    else:
        msg = "Erro de sintaxe: Fim inesperado do comando."
    resultados_execucao.append({'type': 'error', 'content': msg})

parser = yacc.yacc()

# --- Função Principal de Execução ---
# Esta será a única função que o nosso Django irá chamar.
caminho_arquivo_upload_temporario = None
def executar_comandos(codigo_graficalc, variaveis_sessao, caminho_arquivo=None):
    global resultados_execucao, variaveis, caminho_arquivo_upload_temporario

    resultados_execucao = []
    variaveis = variaveis_sessao
    caminho_arquivo_upload_temporario = caminho_arquivo # Define o caminho para a execução atual

    parser.parse(codigo_graficalc, lexer=lexer)

    caminho_arquivo_upload_temporario = None # Limpa a variável global
    return resultados_execucao, variaveis


def safe_read_json(value):
    """
    Lê JSON vindo de um caminho de ficheiro ou de uma string literal JSON.
    - Se 'value' for caminho de ficheiro existente -> pd.read_json(path)
    - Senão, assume que é JSON literal e usa StringIO(value)
    """
    if isinstance(value, str):
        # caminho existente (arquivo local)
        if os.path.exists(value):
            return pd.read_json(value)
        # provável JSON literal: começa por '{' ou '[' (após espaços)
        stripped = value.lstrip()
        if stripped.startswith('{') or stripped.startswith('['):
            return pd.read_json(io.StringIO(value))
    # fallback: tenta usar read_json diretamente (pode lançar)
    return pd.read_json(value)

