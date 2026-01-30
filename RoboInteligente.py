import os
import time
import threading
import math
import random
from groq import Groq
from gtts import gTTS
import pygame

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.graphics import Color, Line, Ellipse, Rectangle
import speech_recognition as sr

# Configuração da API Groq - Substitua pela sua chave ou configure no ambiente
client = Groq(api_key="SUA_CHAVE_GROQ_AQUI")

# Inicialização do Mixer para áudio
pygame.mixer.init()

def falar(texto):
    try:
        tts = gTTS(text=texto, lang='pt')
        filename = "voce.mp3"
        tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Erro na voz: {e}")

# Design da Interface
KV = '''
ScreenManager:
    IntroScreen:
    TrigoScreen:
    GameScreen:

<IntroScreen>:
    name: 'intro'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: "Tutor Trigonométrico"
            font_size: '32sp'
            size_hint_y: 0.1

        # Placeholder para o Robô (70% do ecrã)
        Image:
            source: 'robo_intro.png' # Certifique-se de ter esta imagem
            size_hint_y: 0.6
            allow_stretch: True

        TextInput:
            id: nome_input
            hint_text: "Escreve o teu nome aqui"
            multiline: False
            size_hint: (0.5, None)
            height: '40dp'
            pos_hint: {'center_x': 0.5}

        Button:
            text: "Entrar"
            size_hint: (0.3, None)
            height: '50dp'
            pos_hint: {'center_x': 0.5}
            on_release: root.saudacao()

<TrigoScreen>:
    name: 'trigo'
    canvas.before:
        # Fundo do Robô personalizado
        Color:
            rgba: 0.8, 0.8, 0.8, 1 # Cinza claro
        Rectangle:
            pos: self.pos
            size: self.size
        # Aqui seriam desenhados os elementos do robô (olhos vermelhos, etc)
        # Simplificado com cores de fundo:
        Color:
            rgba: 1, 1, 1, 1 # Boca branca
        Rectangle:
            pos: self.width*0.4, self.height*0.1
            size: self.width*0.2, self.height*0.05

    FloatLayout:
        # Círculo Trigonométrico
        TrigoWidget:
            id: trigo_widget
            size_hint: (0.8, 0.8)
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}

        # Painel de Botões
        BoxLayout:
            size_hint: (1, 0.1)
            pos_hint: {'y': 0}
            Button:
                text: "Iniciar +"
                on_release: trigo_widget.start_movement(1)
            Button:
                text: "Parar/Avançar"
                on_release: trigo_widget.toggle_movement()
            Button:
                text: "Reiniciar"
                on_release: trigo_widget.reset()
            Button:
                text: "Vamos Jogar"
                on_release: app.root.current = 'game'

<GameScreen>:
    name: 'game'
    BoxLayout:
        orientation: 'horizontal'
        
        # Barra de rolagem grossa à esquerda
        ScrollView:
            size_hint_x: 0.2
            bar_width: 20
            Label:
                text: "Progresso e Dicas\\n" * 50
                size_hint_y: None
                height: self.texture_size[1]
        
        BoxLayout:
            orientation: 'vertical'
            padding: 20
            Label:
                text: "Ecrã de Gamificação - IA Groq"
                font_size: '24sp'
                size_hint_y: 0.1
            
            Label:
                id: score_label
                text: "Pontuação: 0"
                size_hint_y: 0.1
            
            Label:
                id: question_text
                text: "Carregando questão..."
                text_size: self.width, None
                size_hint_y: 0.4
            
            GridLayout:
                id: options_grid
                cols: 2
                spacing: 10
                size_hint_y: 0.3

            BoxLayout:
                size_hint_y: 0.1
                Button:
                    text: "Voltar ao Círculo"
                    on_release: app.root.current = 'trigo'
                Button:
                    text: "Reiniciar Jogo"
                    on_release: root.start_game()

<TrigoWidget@Widget>:
    angle: 0
