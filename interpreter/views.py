from django.shortcuts import render
from .graficalc_engine import executar_comandos
import pandas as pd
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from .graficalc_engine import safe_read_json


def interpreter_view(request):
    
    context = {
        'codigo_submetido': '',
        'resultados': []
    }

    
    variaveis_sessao = request.session.get('graficalc_variaveis', {})

    
    for key, value in variaveis_sessao.items():
        variaveis_sessao[key] = safe_read_json(value)

    if request.method == 'POST':
        
        codigo = request.POST.get('codigo', '')
        context['codigo_submetido'] = codigo

        
        resultados, variaveis_atualizadas = executar_comandos(codigo, variaveis_sessao)
        
        context['resultados'] = resultados
        
        
        variaveis_para_json = {}
        for key, df in variaveis_atualizadas.items():
            variaveis_para_json[key] = df.to_json()

        request.session['graficalc_variaveis'] = variaveis_para_json

    
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

        
        if 'arquivo_dados' in request.FILES:
            arquivo_enviado = request.FILES['arquivo_dados']
            fs = FileSystemStorage()
            
            nome_arquivo = fs.save(arquivo_enviado.name, arquivo_enviado)
            
            caminho_arquivo_temporario = os.path.join(settings.MEDIA_ROOT, nome_arquivo)

        
        resultados, variaveis_atualizadas = executar_comandos(codigo, variaveis_sessao, caminho_arquivo_temporario)
        
        
        if caminho_arquivo_temporario and os.path.exists(caminho_arquivo_temporario):
            os.remove(caminho_arquivo_temporario)

        context['resultados'] = resultados
        
        variaveis_para_json = {}
        for key, df in variaveis_atualizadas.items():
            variaveis_para_json[key] = df.to_json()
        request.session['graficalc_variaveis'] = variaveis_para_json

    return render(request, 'interpreter/interface.html', context)