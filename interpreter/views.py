from django.shortcuts import render
from .graficalc_engine import executar_comandos
import pandas as pd
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from .graficalc_engine import safe_read_json


def interpreter_view(request):
    # O 'context' é um dicionário que envia dados para o nosso ficheiro HTML.
    context = {
        'codigo_submetido': '',
        'resultados': []
    }

    # Carrega as variáveis da sessão do utilizador.
    # Se não existirem, começa com um dicionário vazio.
    variaveis_sessao = request.session.get('graficalc_variaveis', {})

    # Converte os dados JSON da sessão de volta para DataFrames do Pandas
    for key, value in variaveis_sessao.items():
        variaveis_sessao[key] = safe_read_json(value)

    if request.method == 'POST':
        # O utilizador clicou no botão "Executar"
        codigo = request.POST.get('codigo', '')
        context['codigo_submetido'] = codigo

        # Chama o nosso motor, passando o código e as variáveis da sessão
        resultados, variaveis_atualizadas = executar_comandos(codigo, variaveis_sessao)
        
        context['resultados'] = resultados
        
        # --- Salvar o estado de volta na sessão ---
        # Converte os DataFrames para um formato que pode ser guardado (JSON)
        variaveis_para_json = {}
        for key, df in variaveis_atualizadas.items():
            variaveis_para_json[key] = df.to_json()

        request.session['graficalc_variaveis'] = variaveis_para_json

    # Renderiza a página HTML, passando os dados do 'context'.
    return render(request, 'interpreter/interface.html', context)


def interpreter_view(request):
    context = {'codigo_submetido': '', 'resultados': []}
    variaveis_sessao = request.session.get('graficalc_variaveis', {})

    for key, value in variaveis_sessao.items():
        variaveis_sessao[key] = safe_read_json(value)

    caminho_arquivo_temporario = None

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '')
        context['codigo_submetido'] = codigo

        # --- LÓGICA DE UPLOAD DE FICHEIRO ---
        if 'arquivo_dados' in request.FILES:
            arquivo_enviado = request.FILES['arquivo_dados']
            fs = FileSystemStorage()
            # Salva o ficheiro na pasta 'media' que configurámos
            nome_arquivo = fs.save(arquivo_enviado.name, arquivo_enviado)
            # Guarda o caminho completo do ficheiro para passá-lo ao motor
            caminho_arquivo_temporario = os.path.join(settings.MEDIA_ROOT, nome_arquivo)

        # Chama o motor, passando o caminho do ficheiro (ou None se não houver upload)
        resultados, variaveis_atualizadas = executar_comandos(codigo, variaveis_sessao, caminho_arquivo_temporario)
        
        # --- LIMPEZA DO FICHEIRO TEMPORÁRIO ---
        if caminho_arquivo_temporario and os.path.exists(caminho_arquivo_temporario):
            os.remove(caminho_arquivo_temporario)

        context['resultados'] = resultados
        
        variaveis_para_json = {}
        for key, df in variaveis_atualizadas.items():
            variaveis_para_json[key] = df.to_json()
        request.session['graficalc_variaveis'] = variaveis_para_json

    return render(request, 'interpreter/interface.html', context)