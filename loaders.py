import os # para a gestão de variável do useragent no Windows
from time import sleep
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

def carrega_youtube(video_id): # faz as transcrições dos CC's do video
    loader = YoutubeLoader(video_id, add_video_info=False, language=['pt'])
    lista_documentos = loader.load()
    documento = '\n\n'.join([doc.page_content for doc in lista_documentos])
    return documento

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
