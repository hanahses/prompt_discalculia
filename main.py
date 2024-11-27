from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
import pygame
import sys

# Configuração da API
load_dotenv()
api_token = os.getenv("GOOGLE_API_TOKEN")
genai.configure(api_key=api_token)
model = genai.GenerativeModel("gemini-1.5-flash")

# Definição das categorias
categorias = [
    "Magnitude dos Números",
    "Representações Numéricas",
    "Sequências e Contagem",
    "Operações Básicas",
    "Problemas de Palavra",
    "Reconhecimento de Formas"
]

qt_perguntas_por_categoria = 5  # número de perguntas por categoria

# JSON Schema adaptado para perguntas de discalculia
json_schema = """
    Questao = {
        "questao": str,
        "resposta": str,
        "alternativas": list[str]
    }
"""

# Função para obter perguntas da API por categoria
def gerar_perguntas(categoria):
    response = model.generate_content(
        f"Gere {qt_perguntas_por_categoria} perguntas de matemática no estilo de quiz para auxiliar crianças com discalculia. "
        f"A categoria é: {categoria}. Use o seguinte esquema JSON: {json_schema}"
    )
    response_text = response.candidates[0].content.parts[0].text
    response_text = response_text.replace("```json\n", '').replace("\n```", '')
    return json.loads(response_text)

# Configurações do pygame
pygame.init()
screen = pygame.display.set_mode((1024, 768))  # Aumentando o tamanho da tela
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

# Função para exibir o texto na tela com quebra de linha
def draw_text(text, pos, color=BLACK, max_width=800):
    lines = []
    words = text.split(' ')
    current_line = []

    for word in words:
        current_line.append(word)
        line_surface = font.render(' '.join(current_line), True, color)
        if line_surface.get_width() > max_width:
            current_line.pop()  # Remove a última palavra
            lines.append(' '.join(current_line))
            current_line = [word]  # Começa uma nova linha com a última palavra

    lines.append(' '.join(current_line))  # Adiciona a última linha

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (pos[0], pos[1] + i * 40))  # Espaçamento entre linhas

# Função para o quiz
def quiz_game(perguntas):
    index = 0
    score = 0

    while index < len(perguntas):
        screen.fill(WHITE)
        pergunta = perguntas[index]
        draw_text(pergunta['questao'], (20, 20))

        y_offset = 150
        alternativas = pergunta['alternativas']
        resposta_correta = pergunta['resposta']
        buttons = []

        # Desenha as alternativas
        for i, alternativa in enumerate(alternativas):
            rect = pygame.Rect(20, y_offset, 760, 40)
            pygame.draw.rect(screen, BLUE, rect)
            draw_text(alternativa, (30, y_offset + 10), WHITE)
            buttons.append((rect, alternativa))
            y_offset += 60

        # Desenha os botões de navegação
        next_button = pygame.Rect(650, 500, 120, 50)
        back_button = pygame.Rect(20, 500, 120, 50)
        exit_button = pygame.Rect(200, 500, 120, 50)

        pygame.draw.rect(screen, GRAY, next_button)
        draw_text("Avançar", (670, 515), WHITE)
        pygame.draw.rect(screen, GRAY, back_button)
        draw_text("Menu Principal", (30, 515), WHITE)
        pygame.draw.rect(screen, RED, exit_button)
        draw_text("Sair", (210, 515), WHITE)

        pygame.display.flip()

        feedback_shown = False
        avancar_permitido = False

        # Loop de eventos
        while not avancar_permitido:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos

                    # Verifica os botões de navegação
                    if back_button.collidepoint(mouse_pos):
                        return True  # Retorna ao menu principal
                    if exit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

                    # Verifica as alternativas
                    if not feedback_shown:
                        for rect, alternativa in buttons:
                            if rect.collidepoint(mouse_pos):
                                if alternativa == resposta_correta:
                                    # Pinta o botão correto de verde
                                    pygame.draw.rect(screen, GREEN, rect)
                                    draw_text(alternativa, (30, rect.y + 10), WHITE)
                                    score += 1
                                else:
                                    # Pinta o botão incorreto de vermelho
                                    pygame.draw.rect(screen, RED, rect)
                                    draw_text(alternativa, (30, rect.y + 10), WHITE)
                                    # Pinta o botão da resposta correta de verde
                                    for correct_rect, correct_alternative in buttons:
                                        if correct_alternative == resposta_correta:
                                            pygame.draw.rect(screen, GREEN, correct_rect)
                                            draw_text(correct_alternative, (30, correct_rect.y + 10), WHITE)
                                            break

                                pygame.display.flip()
                                feedback_shown = True  # Feedback foi exibido
                                break

                    # Verifica o botão "Avançar"
                    if feedback_shown and next_button.collidepoint(mouse_pos):
                        avancar_permitido = True  # Permite avançar para a próxima questão

        # Avança para a próxima questão
        index += 1

    # Fim do jogo
    screen.fill(WHITE)
    draw_text(f"Fim do jogo! Pontuação final: {score} de {len(perguntas)}", (20, 200))
    pygame.display.flip()
    pygame.time.delay(3000)
    return True


# Função para mostrar o menu de categorias
def menu_categorias():
    while True:
        screen.fill(WHITE)
        draw_text("Escolha uma categoria:", (20, 20))

        # Desenho das categorias
        y_offset = 60
        buttons = []
        for i, categoria in enumerate(categorias):
            rect = pygame.Rect(20, y_offset, 760, 40)
            pygame.draw.rect(screen, BLUE, rect)
            draw_text(categoria, (30, y_offset + 10), WHITE)
            buttons.append((rect, categoria))
            y_offset += 60

        pygame.display.flip()

        # Loop de eventos para o menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for rect, categoria in buttons:
                    if rect.collidepoint(mouse_pos):
                        # Alterar cor da categoria selecionada
                        pygame.draw.rect(screen, GREEN, rect)
                        draw_text(categoria, (30, rect.y + 10), WHITE)
                        pygame.display.flip()
                        pygame.time.delay(300)  # Pequeno atraso para feedback visual
                        return categoria  # Retorna a categoria escolhida
# Executa o menu e o quiz
while True:
    categoria_selecionada = menu_categorias()
    perguntas = gerar_perguntas(categoria_selecionada)
    if not quiz_game(perguntas):
        continue  # Se a resposta for False (retorno ao menu), continua no menu

pygame.quit()
