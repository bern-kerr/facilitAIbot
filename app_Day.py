nome_robo = 'BB-8'
nome_humano = 'Day'
genero = 'mulher'
link_imagem='https://i.pinimg.com/564x/ca/ff/94/caff942a376ad0466f5c97ba31b82439.jpg'

import tempfile

import streamlit as st
from langchain.memory import ConversationBufferMemory

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from loaders import * # chama as funções dentro do arquivo loaders.py

TIPOS_ARQUIVOS_VALIDOS = [
    'Usar o bot sem arquivos ou links', 'Site', 'YouTube', 'pdf', 'Excel', 'csv', 'txt'
]

CONFIG_MODELOS = {'OpenAI': 
                        {'modelos': ['gpt-4o-mini', 'gpt-4o', 'o1-preview', 'o1-mini'],
                         'chat': ChatOpenAI},
    
                    'Groq': 
                        {'modelos': ['llama-3.1-70b-versatile', 'gemma2-9b-it', 'mixtral-8x7b-32768'],
                         'chat': ChatGroq} # atribui classe chat dependendo da escolha do modelo
                  }

MEMORIA = ConversationBufferMemory()

def carrega_arquivos(tipo_arquivo, arquivo):
    if tipo_arquivo == 'Site':
        documento = carrega_site(arquivo)
    if tipo_arquivo == 'YouTube':
        documento = carrega_youtube(arquivo)
    if tipo_arquivo == 'pdf':
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_pdf(nome_temp)
    if tipo_arquivo == 'Excel':
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_excel(nome_temp)
    if tipo_arquivo == 'csv':
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_csv(nome_temp)
    if tipo_arquivo == 'txt':
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_txt(nome_temp)
    return documento

def carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo, nome_robo, genero, nome_humano):
    documento = carrega_arquivos(tipo_arquivo, arquivo)

    system_message = '''Você é um assistente amigável chamado {}, feito para a pessoa {} chamada {}.
    Você possui acesso às seguintes informações vindas 
    de um documento {}: 

    ####
        {}
        ####

    Utilize as informações fornecidas para basear as suas respostas.

    Sempre que houver $ na sua saída, substitua por S.

    Se a informação do documento for algo como "Just a moment...Enable JavaScript and cookies to continue" 
    sugira ao usuário carregar novamente o assistente!
    
    '''.format(nome_robo, genero, nome_humano, tipo_arquivo, documento)

    print(system_message)

    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])
    chat = CONFIG_MODELOS[provedor]['chat'](model=modelo, api_key=api_key)
    chain = template | chat

    st.session_state['chain'] = chain

def carrega_chat(provedor, modelo, api_key, nome_robo):
    nome_robo = nome_robo
    system_message = f'''Você é um assistente amigável chamado {nome_robo}, feito para a pessoa {genero} chamada {nome_humano}.
    Responda aos inputs do usuário usando o modelo de linguagem escolhido.'''

    print(system_message)

    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])
    chat = CONFIG_MODELOS[provedor]['chat'](model=modelo, api_key=api_key)
    chain = template | chat

    st.session_state['chain'] = chain

def pagina_chat():
    #st.header(f'Oi {nome_humano}! Eu sou o {nome_robo}')
    
    chain = st.session_state.get('chain')
    if chain is None:
        st.error(f'Configure as abas à esquerda para inicializar o {nome_robo}')
        st.stop()

    memoria = st.session_state.get('memoria', MEMORIA)
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    input_usuario = st.chat_input(f'Fale com o {nome_robo}')
    if input_usuario:
        chat = st.chat_message('human')
        chat.markdown(input_usuario) 

        chat = st.chat_message('ai')
        resposta = chat.write_stream(chain.stream({ 
            'input': input_usuario, 
            'chat_history': memoria.buffer_as_messages
            }))
        
        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria
def sidebar():
    st.image(link_imagem, width=100)
    tabs = st.tabs(['Upload de Arquivos', 'Seleção de Modelos'])
    with tabs[0]:
        tipo_arquivo = st.selectbox('Selecione como você quer usar o bot', TIPOS_ARQUIVOS_VALIDOS)
        if tipo_arquivo == 'Usar o bot sem arquivos ou links':
            arquivo = st.markdown(f'Clique em inicializar {nome_robo}')
        if tipo_arquivo == 'Site':
            arquivo = st.text_input('Digite a url do site')
        if tipo_arquivo == 'YouTube':
            arquivo = st.text_input('Cole o link do video, tirado do botão compartilhar no app ou site do youtube - só funciona em vídeos com CCs')
        if tipo_arquivo == 'pdf':
            arquivo = st.file_uploader('Faça o upload do arquivo pdf', type=['.pdf'])
        if tipo_arquivo == 'Excel':
            arquivo = st.file_uploader('Faça o upload do arquivo xlsx', type=['.xlsx'])
        if tipo_arquivo == 'csv':
            arquivo = st.file_uploader('Faça o upload do arquivo csv', type=['.csv'])
        if tipo_arquivo == 'txt':
            arquivo = st.file_uploader('Faça o upload do arquivo txt', type=['.txt'])
    with tabs[1]:
        provedor = st.selectbox('Selecione o provedor dos modelos de linguagem', CONFIG_MODELOS.keys())
        modelo = st.selectbox('Selecione o modelo', CONFIG_MODELOS[provedor]['modelos'])
        api_key = st.text_input(
            f'Adicione a api key para o provedor {provedor}',
            value=st.session_state.get(f'api_key_{provedor}'))
        st.session_state[f'api_key_{provedor}'] = api_key # salvando api key na session state
    
    if st.button(f'Inicializar {nome_robo}', use_container_width=True):
        
        if tipo_arquivo == 'Usar o bot sem arquivos ou links':
            carrega_chat(provedor, modelo, api_key,nome_robo)
        else:
            carrega_modelo(provedor, modelo, api_key, tipo_arquivo, arquivo, nome_robo, genero, nome_humano)
    if st.button('Apagar Histórico de Conversa', use_container_width=True):
        st.session_state['memoria'] = MEMORIA
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.markdown("<h1 style='font-size: 12px'>Desenvolvido por Facilit.AI</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='font-size: 12px'>Clique na logo para entrar em contato (LinkedIn):</h1>", unsafe_allow_html=True)
    #st.image('https://media.licdn.com/dms/image/v2/D4D0BAQELTl5xA91RHg/company-logo_100_100/company-logo_100_100/0/1727325533304?e=1738195200&v=beta&t=KjuBnUerdDgR1tBShcdpP_PSXiKyT9ju3fUW4n5yGQM', width=50)
    st.markdown("""
    <a href="https://www.linkedin.com/company/105124305/" target="_blank">
        <img src="https://media.licdn.com/dms/image/v2/D4D0BAQELTl5xA91RHg/company-logo_100_100/company-logo_100_100/0/1727325533304?e=1738195200&v=beta&t=KjuBnUerdDgR1tBShcdpP_PSXiKyT9ju3fUW4n5yGQM" 
             style="width: 50px; 
                    height: auto; 
                    cursor: pointer;
                    border-radius: 10px;"
        />
    </a>
""", unsafe_allow_html=True)

def main():
    with st.sidebar: # só assim pra side bar aparecer na lateral
        sidebar()
    pagina_chat()


if __name__ == '__main__':
    main()