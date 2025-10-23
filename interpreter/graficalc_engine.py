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


variaveis = {}
resultados_execucao = []
caminho_arquivo_upload_temporario = None


# LEXER 

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

t_ignore = ' \t\r'

def t_error(t):
    error_msg = f"Caractere ilegal encontrado: '{t.value[0]}'"
    resultados_execucao.append({'type': 'error', 'content': error_msg})
    t.lexer.skip(1)

lexer = lex.lex()


# PARSER

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
        df_head = df.head()
        tabela_html = df_head.to_html(classes='data-table', border=0, index=False, justify='left')
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
        coluna = df[nome_coluna].dropna() 
        resultado = 0
        if tipo_calculo.upper() == 'MEDIA':
            resultado = coluna.mean()
        elif tipo_calculo.upper() == 'MEDIANA':
            resultado = coluna.median()
        elif tipo_calculo.upper() == 'MODA':
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
    
    if len(p) == 16: 
        tipo_grafico = p[4]
        coluna_x = p[7]
        coluna_y = p[10]
        nome_variavel = p[12]
        nome_ficheiro_saida = p[15]
    else: 
        tipo_grafico = p[4]
        coluna_x = p[7]
        coluna_y = p[10]
        nome_variavel = p[12]
        nome_ficheiro_saida = "grafico_gerado.png" 

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
        plt.figure(figsize=(12, 5)) 
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


# Comando principal
def executar_comandos(codigo_graficalc, variaveis_sessao, caminho_arquivo=None):
    global resultados_execucao, variaveis, caminho_arquivo_upload_temporario

    resultados_execucao = []
    variaveis = variaveis_sessao
    caminho_arquivo_upload_temporario = caminho_arquivo 

    parser.parse(codigo_graficalc, lexer=lexer)

    caminho_arquivo_upload_temporario = None 
    return resultados_execucao, variaveis

# Apenas para evitar problemas
def safe_read_json(value):
    if isinstance(value, str):
        if os.path.exists(value):
            return pd.read_json(value)
        stripped = value.lstrip()
        if stripped.startswith('{') or stripped.startswith('['):
            return pd.read_json(io.StringIO(value))
    return pd.read_json(value)

