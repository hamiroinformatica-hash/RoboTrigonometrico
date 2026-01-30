import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
from groq import Groq
from gtts import gTTS
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Tutor Trigonométrico", layout="wide")

# Inicialização da IA Groq
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    client = None

# --- ESTADOS DA SESSÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = 'intro'
if 'angulo' not in st.session_state: st.session_state.angulo = 0
if 'movendo' not in st.session_state: st.session_state.movendo = False
if 'pontuacao' not in st.session_state: st.session_state.pontuacao = 0
if 'questoes_respondidas' not in st.session_state: st.session_state.questoes_respondidas = 0

ANGULOS_NOTAVEIS = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]

# --- FUNÇÕES DE AUDIO ---
def falar(texto):
    tts = gTTS(text=texto, lang='pt')
    tts.save("voce.mp3")
    with open("voce.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
        st.markdown(md, unsafe_allow_html=True)

# --- LÓGICA DO GRÁFICO (ECRÃ 2) ---
def desenhar_circulo(angulo):
    rad = np.radians(angulo)
    px, py = np.cos(rad), np.sin(rad)
    
    fig = go.Figure()

    # Círculo Trigonométrico (Negrito)
    t = np.linspace(0, 2*np.pi, 200)
    fig.add_trace(go.Scatter(x=np.cos(t), y=np.sin(t), mode='lines', line=dict(color='black', width=4)))

    # Sistema Cartesiano (Cosseno: Vermelho, Seno: Azul Escuro)
    fig.add_shape(type="line", x0=-1.5, y0=0, x1=1.5, y1=0, line=dict(color="red", width=3))
    fig.add_shape(type="line", x0=0, y0=-1.5, x1=0, y1=1.5, line=dict(color="darkblue", width=3))

    # Ângulos Notáveis (Rótulos)
    for a in ANGULOS_NOTAVEIS:
        r_a = np.radians(a)
        fig.add_trace(go.Scatter(x=[np.cos(r_a)], y=[np.sin(r_a)], mode='markers+text', 
                                 text=[f"<b>{a}º</b>"], textposition="top right",
                                 marker=dict(color='black', size=8)))

    # Segmentos Móveis
    # Segmento 3: OP (Verde)
    fig.add_trace(go.Scatter(x=[0, px], y=[0, py], mode='lines', line=dict(color='green', width=4), name="OP"))
    # Segmento 1: Paralelo ao Seno (Indica Cosseno - Preto)
    fig.add_trace(go.Scatter(x=[px, px], y=[0, py], mode='lines', line=dict(color='black', dash='dash'), name="Seg1"))
    # Segmento 2: Paralelo ao Cosseno (Indica Seno - Verde Escuro)
    fig.add_trace(go.Scatter(x=[0, px], y=[py, py], mode='lines', line=dict(color='darkgreen', dash='dash'), name="Seg2"))

    # Robô Vermelho no ponto P
    fig.add_trace(go.Scatter(x=[px], y=[py], mode='markers', marker=dict(color='red', size=15, symbol='diamond'), name="P"))

    # Quadrantes e Valores nos Eixos (Negrito)
    valores = [-1, -0.866, -0.707, -0.5, 0, 0.5, 0.707, 0.866, 1]
    labels = ["-1", "-√3/2", "-√2/2", "-1/2", "0", "1/2", "√2/2", "√3/2", "1"]
    
    fig.update_layout(
        showlegend=False, width=700, height=700,
        xaxis=dict(range=[-1.5, 1.5], tickvals=valores, ticktext=[f"<b>{l}</b>" for l in labels]),
        yaxis=dict(range=[-1.5, 1.5], tickvals=valores, ticktext=[f"<b>{l}</b>" for l in labels]),
        template="plotly_white",
        title=f"Ângulo α: {int(angulo)}º | Cos: {px:.2f} | Sen: {py:.2f}"
    )
    return fig

# --- ESTILO DOS ECRÃS ---
# CSS para o Robô de fundo no Ecrã 2
BG_ROBO_CSS = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #d3d3d3; /* Cinza claro */
    background-image: radial-gradient(circle at 20% 20%, red 10px, transparent 11px), /* Olhos */
                      radial-gradient(circle at 30% 20%, red 10px, transparent 11px);
}
/* Barra lateral grossa (Sensor) */
[data-testid="stSidebar"] {
    min-width: 150px;
    max-width: 150px;
    border-right: 20px solid #ff8c00; 
}
</style>
"""

# --- NAVEGAÇÃO ---

# ECRÃ 1: INTRODUÇÃO
if st.session_state.pagina == 'intro':
    st.title("Tutor Trigonométrico")
    col1, col2, col3 = st.columns([0.15, 0.7, 0.15])
    with col2:
        # Robô 70% do ecrã
        st.image("https://img.freepik.com/free-vector/cute-robot-waving-hand-cartoon-character_138676-2744.jpg", use_container_width=True)
    
    nome = st.text_input("Escreve o teu nome:", key="nome_user")
    if st.button("Entrar") or (nome and st.session_state.get('last_nome') != nome):
        falar(f"É um prazer conhecer-te {nome}, e discutir contigo assuntos da trigonometria")
        time.sleep(2)
        st.session_state.pagina = 'trigo'
        st.rerun()

# ECRÃ 2: LABORATÓRIO
elif st.session_state.pagina == 'trigo':
    st.markdown(BG_ROBO_CSS, unsafe_allow_html=True)
    
    col_main, col_side = st.columns([3, 1])
    
    with col_main:
        placeholder = st.empty()
        placeholder.plotly_chart(desenhar_circulo(st.session_state.angulo))
        
        # Botões de Controle
        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button("Iniciar +"):
            st.session_state.movendo = True
        if c2.button("Parar/Avançar"):
            st.session_state.movendo = not st.session_state.movendo
        if c3.button("Reiniciar"):
            st.session_state.angulo = 0
            st.session_state.movendo = False
            st.rerun()

        # Loop de Animação
        if st.session_state.movendo:
            while st.session_state.movendo:
                st.session_state.angulo = (st.session_state.angulo + 1) % 361
                placeholder.plotly_chart(desenhar_circulo(st.session_state.angulo))
                
                if st.session_state.angulo in ANGULOS_NOTAVEIS:
                    time.sleep(2) # Pausa nos notáveis
                else:
                    time.sleep(0.02) # Velocidade 0.02
                
                if st.session_state.angulo == 360:
                    st.session_state.movendo = False
                    break

    with col_side:
        if st.button("VAMOS JOGAR"):
            st.session_state.pagina = 'jogo'
            st.rerun()
        if st.button("Página Inicial"):
            st.session_state.pagina = 'intro'
            st.rerun()

# ECRÃ 3: GAMIFICAÇÃO
elif st.session_state.pagina == 'jogo':
    st.title("Ecrã de Gamificação")
    st.sidebar.write(f"### Pontuação: {st.session_state.pontuacao}")
    
    if st.session_state.questoes_respondidas < 20:
        st.write(f"Questão {st.session_state.questoes_respondidas + 1} de 20")
        
        # Simulação de pergunta da IA
        pergunta = "Qual o valor do Cosseno de 60º?"
        opcoes = ["1/2", "√3/2", "√2/2", "1"]
        resposta = st.radio("Escolha a opção correta:", opcoes)
        
        if st.button("Confirmar Resposta"):
            if resposta == "1/2":
                st.balloons()
                st.success("Excelente! Estás de parabéns.")
                st.session_state.pontuacao += 10
            else:
                st.error("Incorreto. Acompanha a resolução que a IA apresentará:")
                st.video("https://www.youtube.com/watch?v=exemplo") # Espaço para imagem/vídeo
            
            st.session_state.questoes_respondidas += 1
            time.sleep(2)
            st.rerun()
    else:
        st.success("🎉 PARABÉNS! Completaste as 20 questões!")
        if st.button("Reiniciar Quiz"):
            st.session_state.questoes_respondidas = 0
            st.session_state.pontuacao = 0
            st.rerun()

    if st.button("Recuar para o Círculo"):
        st.session_state.pagina = 'trigo'
        st.rerun()
