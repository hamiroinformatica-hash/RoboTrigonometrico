import streamlit as st
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import time

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Tutor Trigonométrico", layout="wide")

# Inicialização da API Groq (Substitua pela sua chave)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    client = None

# Inicializar Estados de Sessão (State Management)
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'intro'
if 'nome' not in st.session_state:
    st.session_state.nome = ""
if 'angulo' not in st.session_state:
    st.session_state.angulo = 0.0
if 'pontos' not in st.session_state:
    st.session_state.pontos = 0

# --- FUNÇÕES DE SUPORTE ---
def mudar_pagina(alvo):
    st.session_state.pagina = alvo
    st.rerun()

def gerar_circulo(angulo_atual):
    # Criar o círculo
    theta = np.linspace(0, 2*np.pi, 100)
    x_circ = np.cos(theta)
    y_circ = np.sin(theta)

    fig = go.Figure()

    # Eixos (Cosseno Vermelho, Seno Azul)
    fig.add_shape(type="line", x0=-1.2, y0=0, x1=1.2, y1=0, line=dict(color="Red", width=2))
    fig.add_shape(type="line", x0=0, y0=-1.2, x1=0, y1=1.2, line=dict(color="DarkBlue", width=2))

    # Círculo
    fig.add_trace(go.Scatter(x=x_circ, y=y_circ, mode='lines', line=dict(color='black'), name='Círculo'))

    # Segmento OP (Verde)
    rad = np.radians(angulo_atual)
    px, py = np.cos(rad), np.sin(rad)
    fig.add_trace(go.Scatter(x=[0, px], y=[0, py], mode='lines+markers', line=dict(color='green', width=4), name='Raio (OP)'))

    # Projeções (Segmentos 1 e 2)
    fig.add_trace(go.Scatter(x=[px, px], y=[0, py], mode='lines', line=dict(color='black', dash='dash'), name='Cos'))
    fig.add_trace(go.Scatter(x=[0, px], y=[py, py], mode='lines', line=dict(color='darkgreen', dash='dash'), name='Sen'))

    # Quadrantes
    fig.add_annotation(x=0.5, y=0.5, text="IQ", showarrow=False)
    fig.add_annotation(x=-0.5, y=0.5, text="IIQ", showarrow=False)
    fig.add_annotation(x=-0.5, y=-0.5, text="IIIQ", showarrow=False)
    fig.add_annotation(x=0.5, y=-0.5, text="IVQ", showarrow=False)

    fig.update_layout(width=600, height=600, showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig

# --- LÓGICA DE NAVEGAÇÃO ---

# ECRÃ 1: INTRODUÇÃO
if st.session_state.pagina == 'intro':
    st.title("Tutor Trigonométrico")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.image("https://img.freepik.com/free-vector/cute-robot-waving-hand-cartoon-character_138676-2744.jpg", width=500) # Exemplo de Robô
    
    with col2:
        nome_input = st.text_input("Como te chamas?")
        if st.button("Entrar"):
            if nome_input:
                st.session_state.nome = nome_input
                st.success(f"É um prazer conhecer-te {nome_input}!")
                # Aqui o som seria via HTML (Streamlit não suporta áudio direto do servidor para o cliente facilmente)
                time.sleep(2)
                mudar_pagina('trigo')

# ECRÃ 2: O CÍRCULO
elif st.session_state.pagina == 'trigo':
    # Barra lateral grossa para simular o sensor
    st.sidebar.markdown("<div style='height: 500px; width: 40px; background: orange;'></div>", unsafe_allow_html=True)
    
    st.header(f"Explorador de Ângulos - Olá, {st.session_state.nome}")
    
    col_ctrl, col_graph = st.columns([1, 2])
    
    with col_ctrl:
        st.write("### Controlos")
        if st.button("Iniciar +"):
            for a in range(0, 361, 5):
                st.session_state.angulo = float(a)
                # Simular parada nos notáveis
                if a in [0, 30, 45, 60, 90, 180]:
                    time.sleep(0.5)
                # Infelizmente Streamlit não anima frames fluidos sem st.empty()
                # Esta é a forma mais estável:
                st.rerun()

        if st.button("Reiniciar"):
            st.session_state.angulo = 0.0
            st.rerun()
            
        st.write(f"**Ângulo Atual:** {st.session_state.angulo}º")
        st.write(f"**Seno:** {np.sin(np.radians(st.session_state.angulo)):.2f}")
        st.write(f"**Cosseno:** {np.cos(np.radians(st.session_state.angulo)):.2f}")

    with col_graph:
        st.plotly_chart(gerar_circulo(st.session_state.angulo))

    if st.button("Vamos Jogar"):
        mudar_pagina('jogo')

# ECRÃ 3: GAMIFICAÇÃO
elif st.session_state.pagina == 'jogo':
    st.title("Desafio Moçambicano 🇲🇿")
    st.write(f"Pontuação Acumulada: **{st.session_state.pontos}**")
    
    # Exemplo de Questão gerada (Em produção, aqui chama a GROQ)
    st.info("Pergunta 1: Se um pescador na Beira observa o topo de um farol sob um ângulo de 30º...")
    
    opcoes = ["1/2", "√3/2", "1", "√2/2"]
    escolha = st.radio("Qual é o valor do seno deste ângulo?", opcoes)
    
    if st.button("Submeter"):
        if escolha == "1/2":
            st.success("Acertaste! Excelente trabalho.")
            st.session_state.pontos += 10
        else:
            st.error("Errado! Presta atenção à resolução abaixo.")
    
    if st.button("Voltar ao Início"):
        mudar_pagina('intro')
