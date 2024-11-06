import google.generativeai as genai
import json
import pygame
import sys

# Configuração da API

genai.configure(api_key="AIzaSyC6Y0qOQJrLWPrQBim7oKE7nnJ0l-k00b4")
model = genai.GenerativeModel("gemini-1.5-flash")

qt_perguntas = 5  # número de perguntas para o quiz
arquivo_saida = "response_text.json"

# JSON Schema adaptado para perguntas de discalculia
json_schema = """
    Questao = {
        "questao": str,
        "resposta": str,
        "alternativas": list[str]
    }
    """
exemplos = """
    {
        "questao": "Qual número é maior: 3 ou 7?",
        "resposta": "7",
        "alternativas": ["3", "5", "7", "9"]
    },
    {
        "questao": "Quantos objetos há nesta lista: maçã, maçã, maçã?",
        "resposta": "3",
        "alternativas": ["1", "2", "3", "4"]
    }
"""

# Função para obter perguntas da API
def gerar_perguntas():
    response = model.generate_content(
        "Gere " + str(qt_perguntas) + " perguntas de matemática em formato de quiz para auxiliar crianças com discalculia. "
        + "Os tópicos devem incluir: magnitude dos números, associação entre números e suas representações textuais, "
        + "sequências e contagem. Use o seguinte esquema JSON: " + json_schema
        + " Retorne apenas list[Questao] conforme o esquema fornecido."
        + " Exemplos de perguntas: " + exemplos
    )
    response_text = response.candidates[0].content.parts[0].text
    response_text = response_text.replace("```json\n", '').replace("\n```", '')
    return json.loads(response_text)

# Configurações do pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))  # Aumentando o tamanho da tela
pygame.display.set_caption("Quiz de Matemática para Discalculia")
font = pygame.font.Font(None, 32)
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
RED = (255, 69, 0)
GREEN = (0, 128, 0)
GRAY = (169, 169, 169)

# Função para exibir o texto na tela
def draw_text(text, pos, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

# Função para o quiz
def quiz_game(perguntas):
    index = 0
    score = 0
    feedback = ""
    show_feedback = False

    while index < len(perguntas):
        screen.fill(WHITE)
        
        pergunta = perguntas[index]
        draw_text(pergunta['questao'], (20, 20))

        # Exibe o feedback (correto/incorreto)
        if show_feedback:
            draw_text(feedback, (20, 80), GREEN if "Correto" in feedback else RED)

        # Desenha as alternativas
        y_offset = 150
        alternativas = pergunta['alternativas']
        resposta_correta = pergunta['resposta']

        buttons = []
        for i, alternativa in enumerate(alternativas):
            rect = pygame.Rect(20, y_offset, 760, 40)
            pygame.draw.rect(screen, BLUE, rect)
            draw_text(alternativa, (30, y_offset + 10), WHITE)
            buttons.append((rect, alternativa))
            y_offset += 60

        # Desenha o botão "Avançar" após a resposta
        next_button = pygame.Rect(650, 500, 120, 50)
        pygame.draw.rect(screen, GRAY if not show_feedback else GREEN, next_button)
        draw_text("Avançar", (670, 515), WHITE)

        pygame.display.flip()

        # Loop de eventos para cada pergunta
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if not show_feedback:
                    # Clique nas alternativas
                    for rect, alternativa in buttons:
                        if rect.collidepoint(mouse_pos):
                            if alternativa == resposta_correta:
                                feedback = "Correto!"
                                score += 1
                            else:
                                feedback = f"Incorreto! A resposta correta é: {resposta_correta}"
                            show_feedback = True  # Mostrar o feedback até que "Avançar" seja clicado
                            break
                elif show_feedback and next_button.collidepoint(mouse_pos):
                    # Clique no botão "Avançar" para passar à próxima pergunta
                    index += 1
                    show_feedback = False
                    feedback = ""

        clock.tick(30)

    # Exibir a pontuação final
    screen.fill(WHITE)
    draw_text(f"Fim do jogo! Pontuação final: {score} de {len(perguntas)}", (20, 200))
    pygame.display.flip()
    pygame.time.delay(3000)

# Executa o quiz
perguntas = gerar_perguntas()
quiz_game(perguntas)

pygame.quit()
