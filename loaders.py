import os # para a gestão de variável do useragent no Windows
from time import sleep
import re
import streamlit as st
from langchain_community.document_loaders import (WebBaseLoader,
                                                  YoutubeLoader, 
                                                  CSVLoader, 
                                                  PyPDFLoader, 
                                                  TextLoader)
from fake_useragent import UserAgent # para driblar bloqueios DDOS

def carrega_site(url):
    documento = ''
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url.lstrip('/')  # Remove leading slashes if any
    
    for i in range(5): # 5 tentativas de carregar site
        try:
            os.environ['USER_AGENT'] = UserAgent().random # para driblar bloqueios DDOS
            loader = WebBaseLoader(url, raise_for_status=True)
            lista_documentos = loader.load()
            documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
            break
        except:
            print(f'Erro ao carregar o site {i+1}')
            sleep(3) # espera de 3 segundos para tentar carregar o site
    if documento == '':
        st.error('Não foi possível carregar o site')
        st.stop()
    return documento

def carrega_youtube(entrada):
    # Padrões para diferentes formatos de entrada
    padrao_completo = r"v=([-\w]+)"
    padrao_curto = r"youtu\.be\/([-\w]+)"
    padrao_id = r"^[-\w]{11}$"  # Padrão para ID puro (11 caracteres)
    
    # Se a entrada for uma URL, remover parâmetros após '?'
    if '/' in entrada:
        entrada = entrada.split('?')[0]
    
    # Tentar encontrar match em todos os padrões
    match_completo = re.search(padrao_completo, entrada)
    match_curto = re.search(padrao_curto, entrada)
    match_id = re.search(padrao_id, entrada)
    
    # Pegar o ID do vídeo do padrão que der match
    if match_completo:
        video_id = match_completo.group(1)
    elif match_curto:
        video_id = match_curto.group(1)
    elif match_id:
        video_id = entrada
    else:
        return "Entrada inválida. Por favor, forneça um ID de vídeo válido ou URL do YouTube."
    
    try:
        # Carregar o vídeo usando o ID encontrado
        loader = YoutubeLoader(video_id, add_video_info=False, language=['pt'])
        lista_documentos = loader.load()
        documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
        return documento
    except Exception as e:
        return f"Erro ao carregar o vídeo: {str(e)}"

def carrega_csv(caminho):
    loader = CSVLoader(caminho)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_pdf(caminho):
    loader = PyPDFLoader(caminho)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

def carrega_txt(caminho):
    loader = TextLoader(caminho)
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento
