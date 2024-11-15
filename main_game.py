# main_game.py

import pygame
import sys
import threading
import random
import logging
from ai_interaction import (
    generate_multiple_choice_question,
    generate_open_ended_question,
    evaluate_response,
)

# Configurar el registro
logging.basicConfig(level=logging.INFO)

# Inicialización de Pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 1400, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ambicioso Quality")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (211, 211, 211)
DARK_GRAY = (169, 169, 169)
PRIMARY_COLOR = (33, 150, 243)    # Azul
SECONDARY_COLOR = (255, 193, 7)   # Amarillo
ACCENT_COLOR = (76, 175, 80)      # Verde
ERROR_COLOR = (244, 67, 54)       # Rojo

# Color de fondo
BACKGROUND_COLOR = (255, 255, 255)  # Blanco humo

# Fuentes
try:
    FONT = pygame.font.Font('videogame.ttf', 18)  # Fuente personalizada
    LARGE_FONT = pygame.font.Font('videogame.ttf', 30)  # Fuente personalizada
    SMALL_FONT = pygame.font.Font('videogame.ttf', 14)  # Fuente personalizada
except FileNotFoundError:
    logging.warning("Fuente 'videogame.ttf' no encontrada. Usando fuentes predeterminadas.")
    FONT = pygame.font.SysFont('Arial', 18)
    LARGE_FONT = pygame.font.SysFont('Arial', 30, bold=True)
    SMALL_FONT = pygame.font.SysFont('Arial', 14)

# Variables del juego
players = []
current_player_index = 0
goal_score = 100  # Puntaje objetivo predeterminado

# Temas para las preguntas
TOPICS = [
    'ISO 25000',
    'CMM',
    'SPICE',
    'ISO 9001',
    'McCalls Quality Model',
    'Boehms Model',
    'IEEE Model',
    'Total Quality Management (TQM)',
    'Software Quality In Development (SQUID)',
    'DEQUALITE Model',
    'FURPS Model',
    'Dromeys Quality Model',
    'ISO/IEC 25010',
    'ISO/IEC 25020',
    'ISO/IEC 25030',
    'ISO/IEC 25040',
    'ISO/IEC 15504 - SPICE',
    'ISO/IEC 9126',
    'ISO/IEC 14598'
]

# Clase Jugador
class Player:
    def __init__(self, name, avatar_color):
        self.name = name
        self.score = 0
        self.avatar_color = avatar_color
        self.input_text = ''
        self.input_active = False

# Función para mostrar texto centrado en la pantalla
def draw_centered_text(text, font, color, surface, y, x_offset=None):
    textobj = font.render(text, True, color)
    if x_offset is None:
        text_rect = textobj.get_rect(center=(WIDTH // 2, y))
    else:
        text_rect = textobj.get_rect(center=(x_offset, y))
    surface.blit(textobj, text_rect)

# Función para mostrar texto en una posición específica
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    surface.blit(textobj, (x, y))

# Función principal
def main():
    main_menu()

# Función para el menú principal
def main_menu():
    click = False

    # Cargar imágenes
    logo_hh = pygame.image.load('logo-hh.png')
    logo_hh = pygame.transform.scale(logo_hh, (700, 400))  # Tamaño ajustado del logo principal
    logo_l = pygame.image.load('logo-l.png')
    logo_l = pygame.transform.scale(logo_l, (500, 500))  # Tamaño ajustado del logo inicial

    # Desvanecimiento inicial
    fade_alpha = 255  # Transparencia inicial
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BACKGROUND_COLOR)

    while fade_alpha > 0:  # Animación de desvanecimiento
        SCREEN.fill(BACKGROUND_COLOR)
        logo_x = (WIDTH - logo_l.get_width()) // 2
        logo_y = (HEIGHT - logo_l.get_height()) // 2
        SCREEN.blit(logo_l, (logo_x, logo_y))

        fade_surface.set_alpha(fade_alpha)
        SCREEN.blit(fade_surface, (0, 0))
        fade_alpha -= 5  # Reducir transparencia gradualmente
        pygame.display.update()
        pygame.time.delay(30)  # Controlar la velocidad de la animación

    # Loop del menú principal
    while True:
        SCREEN.fill(BACKGROUND_COLOR)

        # Dibujar el título usando el logo-hh.png
        logo_x = (WIDTH - logo_hh.get_width()) // 2
        logo_y = 50
        SCREEN.blit(logo_hh, (logo_x, logo_y))

        # Obtener la posición del mouse
        mx, my = pygame.mouse.get_pos()

        # Dibujar botón "JUGAR" más abajo
        button_play = pygame.Rect(WIDTH // 2 - 100, 400, 200, 60) 
        pygame.draw.rect(SCREEN, PRIMARY_COLOR, button_play, border_radius=30)
        draw_centered_text('JUGAR', FONT, WHITE, SCREEN, button_play.y + 30)


        # Efecto hover en el botón
        if button_play.collidepoint((mx, my)):
            pygame.draw.rect(SCREEN, ACCENT_COLOR, button_play, border_radius=30)
            draw_centered_text('JUGAR', FONT, WHITE, SCREEN, button_play.y + 30)

        # Manejo de clic en el botón
        if button_play.collidepoint((mx, my)) and click:
            player_selection()

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()


# Función para la selección de jugadores
def player_selection():
    global players, goal_score
    players = []
    num_players = 2
    input_active = False
    input_text = ''

    selecting = True
    click = False

    while selecting:
        SCREEN.fill(BACKGROUND_COLOR)
        draw_centered_text('Selecciona el número de jugadores (2-4):', FONT, PRIMARY_COLOR, SCREEN, 150)

        mx, my = pygame.mouse.get_pos()

        buttons = []
        positions = [WIDTH // 2 - 150, WIDTH // 2, WIDTH // 2 + 150]
        for i, x_pos in enumerate(positions, start=2):
            button = pygame.Rect(x_pos - 50, 200, 100, 60)
            buttons.append((button, i))
            pygame.draw.rect(SCREEN, PRIMARY_COLOR, button, border_radius=20)
            draw_centered_text(str(i), FONT, WHITE, SCREEN, button.y + 30, x_offset=button.x + 50)

            if button.collidepoint((mx, my)):
                pygame.draw.rect(SCREEN, ACCENT_COLOR, button, border_radius=20)
                draw_centered_text(str(i), FONT, WHITE, SCREEN, button.y + 30, x_offset=button.x + 50)
                if click:
                    num_players = i

        draw_centered_text(f'Jugadores seleccionados: {num_players}', FONT, PRIMARY_COLOR, SCREEN, 280)

        draw_centered_text('Ingresa el puntaje objetivo para ganar:', FONT, PRIMARY_COLOR, SCREEN, 340)
        input_box = pygame.Rect(WIDTH // 2 - 100, 370, 200, 40)
        pygame.draw.rect(SCREEN, WHITE, input_box, border_radius=10)
        pygame.draw.rect(SCREEN, PRIMARY_COLOR, input_box, 2, border_radius=10)
        input_text_surface = FONT.render(input_text, True, BLACK)
        input_rect = input_text_surface.get_rect(center=(WIDTH // 2, input_box.y + 20))
        SCREEN.blit(input_text_surface, input_rect)

        continue_button = pygame.Rect(WIDTH // 2 - 100, 430, 200, 50)
        pygame.draw.rect(SCREEN, PRIMARY_COLOR, continue_button, border_radius=25)
        draw_centered_text('CONTINUAR', FONT, WHITE, SCREEN, continue_button.y + 25)

        if continue_button.collidepoint((mx, my)):
            pygame.draw.rect(SCREEN, ACCENT_COLOR, continue_button, border_radius=25)
            draw_centered_text('CONTINUAR', FONT, WHITE, SCREEN, continue_button.y + 25)
            if click:
                if input_text.isdigit() and int(input_text) > 0:
                    goal_score = int(input_text)
                    avatar_colors = [PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, DARK_GRAY]
                    for j in range(num_players):
                        players.append(Player(f"Jugador {j+1}", avatar_colors[j]))
                    selecting = False
                else:
                    draw_centered_text('Por favor, ingresa un puntaje válido.', FONT, ERROR_COLOR, SCREEN, 500)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                if event.button == 1:
                    click = True
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        pass
                    else:
                        if len(input_text) < 4 and event.unicode.isdigit():
                            input_text += event.unicode

        pygame.display.update()

    game_loop()

# Función principal del juego
def game_loop():
    global current_player_index

    # Cargar y escalar la imagen del logo
    logo = pygame.image.load('logo-h.png')
    logo = pygame.transform.scale(logo, (300, 150))  # Ajustar tamaño (ancho x alto)
    logo_width, logo_height = logo.get_size()

    running = True
    click = False
    while running:
        SCREEN.fill(BACKGROUND_COLOR)

        # Encabezado
        pygame.draw.rect(SCREEN, PRIMARY_COLOR, (0, 0, WIDTH, logo_height + 20))
        logo_x = (WIDTH - logo_width) // 2
        logo_y = 10  # Espaciado desde el borde superior
        SCREEN.blit(logo, (logo_x, logo_y))
        draw_text(f'Puntaje Objetivo: {goal_score}', FONT, WHITE, SCREEN, WIDTH - 420, logo_y + logo_height // 2)

        # Mostrar puntajes y progreso
        draw_players_info()

        current_player = players[current_player_index]

        # Espaciado para evitar sobreposición
        text_y_offset = logo_height + 50  # Ajustar más espacio vertical desde el logo

        # Texto del turno actual
        draw_text(f'Turno del {current_player.name}', FONT, PRIMARY_COLOR, SCREEN, WIDTH - 400, text_y_offset)
        text_y_offset += 80  # Aumentar espacio vertical para separar del input

        # Campo de entrada para el resultado del dado
        draw_text('Resultado del dado:', FONT, PRIMARY_COLOR, SCREEN, WIDTH - 400, text_y_offset)
        input_box = pygame.Rect(WIDTH - 340, text_y_offset + 40, 200, 40)  # Bajar más el input
        pygame.draw.rect(SCREEN, WHITE, input_box, border_radius=10)
        pygame.draw.rect(SCREEN, PRIMARY_COLOR, input_box, 2, border_radius=10)
        input_text_surface = FONT.render(current_player.input_text, True, BLACK)
        input_rect = input_text_surface.get_rect(center=(input_box.x + 100, input_box.y + 25))
        SCREEN.blit(input_text_surface, input_rect)
        text_y_offset += 140  # Aumentar espacio vertical para el botón

        # Botón para ingresar el resultado del dado
        dice_button = pygame.Rect(WIDTH - 340, text_y_offset, 200, 50)
        pygame.draw.rect(SCREEN, PRIMARY_COLOR, dice_button, border_radius=25)
        draw_centered_text('INGRESAR', FONT, WHITE, SCREEN, dice_button.y + 30, x_offset=dice_button.x + 100)

        # Efecto hover para el botón
        mx, my = pygame.mouse.get_pos()
        if dice_button.collidepoint((mx, my)):
            pygame.draw.rect(SCREEN, ACCENT_COLOR, dice_button, border_radius=25)
            draw_centered_text('INGRESAR', FONT, WHITE, SCREEN, dice_button.y + 30, x_offset=dice_button.x + 100)
            if click:
                process_dice_input(current_player)
                if check_winner():
                    running = False
                    break

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    current_player.input_active = True
                else:
                    current_player.input_active = False
                if event.button == 1:
                    click = True
            if event.type == pygame.KEYDOWN:
                if current_player.input_active:
                    if event.key == pygame.K_BACKSPACE:
                        current_player.input_text = current_player.input_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        if current_player.input_text.isdigit():
                            process_dice_input(current_player)
                            if check_winner():
                                running = False
                                break
                    else:
                        if len(current_player.input_text) < 4 and event.unicode.isdigit():
                            current_player.input_text += event.unicode

        # Detectar si se hace clic en el botón para ingresar el resultado
        if dice_button.collidepoint(pygame.mouse.get_pos()) and click:
            process_dice_input(current_player)
            if check_winner():
                running = False
                break

        pygame.display.update()



# Función para dibujar información de jugadores
def draw_players_info():
    y_offset = 210  # Espaciado inicial desde la parte superior (reducido un 20% adicional)
    bar_width = 544
    bar_height = 22 
    avatar_radius = 32 
    text_spacing = 19  
    vertical_spacing = 64  

    for player in players:
        # Dibujar avatar
        avatar_x = 80
        avatar_y = y_offset + avatar_radius
        pygame.draw.circle(SCREEN, player.avatar_color, (avatar_x, avatar_y), avatar_radius)

        # Mostrar nombre y puntaje
        if player.score >= goal_score:
            name_score_text = FONT.render(f'{player.name}:    {player.score} puntos - ¡Ganado!', True, ACCENT_COLOR)
        else:
            name_score_text = FONT.render(f'{player.name}:    {player.score} puntos', True, BLACK)
        SCREEN.blit(name_score_text, (avatar_x + avatar_radius * 2 + text_spacing, y_offset))

        # Dibujar barra de progreso
        progress = min(player.score / goal_score, 1.0)
        bar_x = avatar_x + avatar_radius * 2 + text_spacing
        bar_y = y_offset + 40  # Ajustado para mantener proporción con la reducción
        pygame.draw.rect(SCREEN, LIGHT_GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        pygame.draw.rect(SCREEN, ACCENT_COLOR, (bar_x, bar_y, bar_width * progress, bar_height), border_radius=5)

        # Mostrar porcentaje al final de la barra
        progress_text = SMALL_FONT.render(f'{int(progress * 100)}%', True, BLACK)
        SCREEN.blit(progress_text, (bar_x + bar_width + 6, bar_y + 3))

        # Actualizar desplazamiento vertical
        y_offset += avatar_radius * 2 + vertical_spacing


# Función para procesar la entrada del dado
def process_dice_input(current_player):
    error_message = None  # Variable para almacenar el mensaje de error si ocurre
    message_display_time = 1000  # Duración del mensaje de error en milisegundos
    message_font = pygame.font.Font(None, 20)  # Fuente ajustada para mensajes

    # Validar si el input está vacío
    if not current_player.input_text.strip():
        error_message = 'El campo no puede estar vacío. Ingresa el resultado del dado.'
    elif not current_player.input_text.isdigit():
        # Validar si no es un número
        error_message = 'Por favor ingresa un número válido.'
    else:
        dice_result = int(current_player.input_text)
        # Validar rango del número
        if 1 <= dice_result <= 9999:
            if dice_result != 1:
                current_player.score += dice_result
                current_player.input_text = ''
                next_player()
            else:
                handle_ai_question(current_player)
                current_player.input_text = ''
                next_player()
        else:
            error_message = 'El número debe estar entre 1 y 9999.'

    # Mostrar mensaje de error si ocurre
    if error_message:
        # Dibujar la caja de mensaje
        error_box = pygame.Rect(WIDTH // 2 - 250, HEIGHT - 100, 500, 50)  # Caja más grande para mejor visibilidad
        pygame.draw.rect(SCREEN, ERROR_COLOR, error_box, border_radius=15)
        pygame.draw.rect(SCREEN, BLACK, error_box, 3, border_radius=15)  # Borde negro más grueso
        error_text = message_font.render(error_message, True, WHITE)

        # Centrar el mensaje en la caja
        text_rect = error_text.get_rect(center=error_box.center)
        SCREEN.blit(error_text, text_rect)
        pygame.display.update()

        # Mantener el mensaje visible por un tiempo
        pygame.time.delay(message_display_time)




# Función para cambiar al siguiente jugador
def next_player():
    global current_player_index
    current_player_index = (current_player_index + 1) % len(players)

# Función para verificar si hay un ganador
def check_winner():
    for player in players:
        if player.score >= goal_score:
            # Dimensiones del cuadro
            popup_width, popup_height = 850, 500
            popup_x = (WIDTH - popup_width) // 2
            popup_y = (HEIGHT - popup_height) // 2
            popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

            # Fondo difuminado
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(DARK_GRAY)
            SCREEN.blit(overlay, (0, 0))

            # Animación inicial: aparición con desenfoque y pulso
            for scale in range(1, 21):
                SCREEN.blit(overlay, (0, 0))
                scaled_rect = pygame.Rect(
                    popup_x + (popup_width // 2) * (1 - scale / 20),
                    popup_y + (popup_height // 2) * (1 - scale / 20),
                    popup_width * (scale / 20),
                    popup_height * (scale / 20)
                )
                pygame.draw.rect(SCREEN, WHITE, scaled_rect, border_radius=30)
                pygame.draw.rect(SCREEN, ACCENT_COLOR, scaled_rect, 12, border_radius=30)
                pygame.display.update()
                pygame.time.delay(15)

            # Dibujar ventana completamente escalada
            pygame.draw.rect(SCREEN, WHITE, popup_rect, border_radius=30)
            pygame.draw.rect(SCREEN, PRIMARY_COLOR, popup_rect, 14, border_radius=30)

            # Mostrar texto principal
            draw_centered_text(f'{player.name} ha ganado!', LARGE_FONT, ACCENT_COLOR, SCREEN, popup_y + 150)
            draw_centered_text('¡Felicidades!', LARGE_FONT, SECONDARY_COLOR, SCREEN, popup_y + 220)
            draw_centered_text('Presiona cualquier tecla para continuar', SMALL_FONT, BLACK, SCREEN, popup_y + 350)
            pygame.display.update()

            # Efecto avanzado de partículas
            particles = []
            for _ in range(150):  # Más partículas para un efecto impresionante
                particles.append({
                    'x': popup_x + popup_width // 2,
                    'y': popup_y + popup_height // 2,
                    'dx': random.uniform(-5, 5),
                    'dy': random.uniform(-5, 5),
                    'radius': random.randint(3, 10),
                    'color': random.choice([PRIMARY_COLOR, ACCENT_COLOR, SECONDARY_COLOR]),
                    'lifetime': random.randint(40, 80),
                    'fade_rate': random.uniform(0.02, 0.05),
                    'sparkle': random.choice([True, False])  # Efecto de brillo intermitente
                })

            for frame in range(120):  # Animar partículas por más tiempo
                SCREEN.blit(overlay, (0, 0))
                pygame.draw.rect(SCREEN, WHITE, popup_rect, border_radius=30)
                pygame.draw.rect(SCREEN, PRIMARY_COLOR, popup_rect, 14, border_radius=30)
                draw_centered_text(f'{player.name} ha ganado!', LARGE_FONT, ACCENT_COLOR, SCREEN, popup_y + 150)
                draw_centered_text('¡Felicidades!', LARGE_FONT, SECONDARY_COLOR, SCREEN, popup_y + 220)
                draw_centered_text('Presiona cualquier tecla para continuar', SMALL_FONT, BLACK, SCREEN, popup_y + 350)

                for p in particles[:]:
                    # Dibujar partícula con efecto de brillo
                    if p['sparkle'] and frame % 5 == 0:
                        pygame.draw.circle(SCREEN, WHITE, (int(p['x']), int(p['y'])), p['radius'] + 2)
                    pygame.draw.circle(SCREEN, p['color'], (int(p['x']), int(p['y'])), p['radius'])

                    # Actualizar posición
                    p['x'] += p['dx']
                    p['y'] += p['dy']
                    # Reducir tamaño y opacidad
                    p['radius'] = max(p['radius'] - p['fade_rate'], 0)
                    # Reducir tiempo de vida
                    p['lifetime'] -= 1
                    if p['lifetime'] <= 0 or p['radius'] <= 0:
                        particles.remove(p)

                pygame.display.update()
                pygame.time.delay(25)

            # Pausar hasta que el usuario interactúe
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        waiting = False
            return True
    return False


# Función para manejar preguntas de la IA
def handle_ai_question(player):
    question_event = threading.Event()
    question_data = {}

    def get_question():
        try:
            # Generar pregunta cerrada o abierta aleatoriamente
            question_type = random.choice(['cerrada', 'abierta'])
            topic = random.choice(TOPICS)

            if question_type == 'cerrada':
                question, options, correct_option = generate_multiple_choice_question(topic)
                if not all([question, options, correct_option]):
                    raise ValueError("Datos de pregunta de opción múltiple incompletos.")
                question_data['type'] = 'cerrada'
                question_data['question'] = question
                question_data['options'] = options
                question_data['correct_option'] = correct_option
            else:
                case_study = generate_open_ended_question(topic)
                if not case_study:
                    raise ValueError("Datos de pregunta abierta incompletos.")
                question_data['type'] = 'abierta'
                question_data['case_study'] = case_study
                question_data['topic'] = topic

        except Exception as e:
            logging.error(f"Error al generar la pregunta: {e}")
            question_data['type'] = 'error'
            question_data['error_message'] = str(e)
        finally:
            # Señalar que la pregunta ha sido obtenida (o ha ocurrido un error)
            question_event.set()

    # Iniciar hilo para obtener la pregunta
    question_thread = threading.Thread(target=get_question)
    question_thread.start()

    # Mostrar mensaje de espera mientras se obtiene la pregunta
    show_waiting_message(question_event)

    # Esperar a que el hilo de obtener la pregunta termine
    question_thread.join()

    # Procesar la pregunta obtenida o manejar el error
    if question_data.get('type') == 'cerrada':
        ask_multiple_choice_question(
            player,
            question_data['question'],
            question_data['options'],
            question_data['correct_option']
        )
    elif question_data.get('type') == 'abierta':
        ask_open_ended_question(
            player,
            question_data['case_study'],
            question_data['topic']
        )
    elif question_data.get('type') == 'error':
        # Mostrar mensaje de error y continuar el juego sin cambiar la puntuación
        draw_centered_text('Error con la IA. Continuando el juego...', FONT, ERROR_COLOR, SCREEN, 400)
        pygame.display.update()
        pygame.time.delay(2000)
    else:
        draw_centered_text('Error al generar la pregunta.', FONT, ERROR_COLOR, SCREEN, 400)
        pygame.display.update()
        pygame.time.delay(2000)

# Función para mostrar mensaje de espera
def show_waiting_message(question_event):
    animation_frames = ['.', '..', '...', '']
    frame = 0
    clock = pygame.time.Clock()
    while not question_event.is_set():
        SCREEN.fill(BACKGROUND_COLOR)
        draw_centered_text(
            'Esperando respuesta de la IA' + animation_frames[frame % len(animation_frames)],
            FONT, PRIMARY_COLOR, SCREEN, 350
        )
        pygame.display.update()
        pygame.time.delay(500)
        frame += 1
        # Manejar eventos para evitar que la ventana se congele
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)

def ask_multiple_choice_question(player, question, options, correct_option):
    answering = True
    click = False

    # Variables para el diseño
    margin = 50
    max_text_width = WIDTH - 2 * margin
    option_button_width = WIDTH - 2 * margin

    # Función para ajustar el texto dentro de un ancho máximo
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + word + ' '
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + ' '
        if current_line:
            lines.append(current_line)
        return lines

    # Ajustar el texto de la pregunta
    question_lines = wrap_text(question, FONT, max_text_width)

    # Variables para mostrar la retroalimentación
    selected_option_letter = None
    feedback_shown = False

    while True:
        SCREEN.fill(BACKGROUND_COLOR)
        # Dibujar un recuadro para la pregunta
        question_box_height = (FONT.get_height() + 5) * len(question_lines) + 30
        question_box = pygame.Rect(margin, 50, WIDTH - 2 * margin, question_box_height)
        pygame.draw.rect(SCREEN, LIGHT_GRAY, question_box, border_radius=10)
        pygame.draw.rect(SCREEN, PRIMARY_COLOR, question_box, 2, border_radius=10)

        # Mostrar la pregunta centrada dentro del recuadro
        y_text = question_box.y + 15
        for line in question_lines:
            draw_text(line, FONT, BLACK, SCREEN, question_box.x + 15, y_text)
            y_text += FONT.get_height() + 5

        mx, my = pygame.mouse.get_pos()

        # Mostrar opciones como botones
        buttons = []
        y_offset = question_box.y + question_box_height + 20
        for idx, (option_letter, option_text) in enumerate(options):
            # Ajustar el texto de la opción
            option_lines = wrap_text(f'{option_letter}: {option_text}', FONT, option_button_width - 30)
            option_height = (FONT.get_height() + 5) * len(option_lines) + 20

            button = pygame.Rect(margin, y_offset, option_button_width, option_height)
            buttons.append((button, option_letter))

            # Determinar el color del botón
            if feedback_shown:
                if option_letter.upper() == selected_option_letter:
                    # Si es la opción seleccionada
                    if selected_option_letter.upper() == correct_option.upper():
                        button_color = ACCENT_COLOR  # Correcto
                    else:
                        button_color = ERROR_COLOR  # Incorrecto
                elif option_letter.upper() == correct_option.upper():
                    # Mostrar la opción correcta
                    button_color = ACCENT_COLOR
                else:
                    button_color = PRIMARY_COLOR
            else:
                # Efecto hover
                if button.collidepoint((mx, my)):
                    button_color = ACCENT_COLOR
                else:
                    button_color = PRIMARY_COLOR

            pygame.draw.rect(SCREEN, button_color, button, border_radius=10)

            # Color del texto
            text_color = WHITE if button_color in [PRIMARY_COLOR, ACCENT_COLOR, ERROR_COLOR] else BLACK

            # Dibujar el texto de la opción dentro del botón
            text_y = y_offset + 10
            for line in option_lines:
                draw_text(line, FONT, text_color, SCREEN, button.x + 15, text_y)
                text_y += FONT.get_height() + 5

            y_offset += option_height + 15  # Espacio entre botones

        if feedback_shown:
            # Mostrar retroalimentación
            if selected_option_letter.upper() == correct_option.upper():
                draw_centered_text('¡Correcto!', LARGE_FONT, ACCENT_COLOR, SCREEN, HEIGHT - 100)
            else:
                draw_centered_text(f'Incorrecto. La respuesta correcta era {correct_option.upper()}.', FONT, ERROR_COLOR, SCREEN, HEIGHT - 100)

            # Botón 'Continuar'
            continue_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 60, 200, 50)
            pygame.draw.rect(SCREEN, PRIMARY_COLOR, continue_button, border_radius=25)
            draw_centered_text('CONTINUAR', FONT, WHITE, SCREEN, continue_button.y + 25)

            if continue_button.collidepoint((mx, my)):
                pygame.draw.rect(SCREEN, ACCENT_COLOR, continue_button, border_radius=25)
                draw_centered_text('CONTINUAR', FONT, WHITE, SCREEN, continue_button.y + 25)
        else:
            click = False
            for button, option_letter in buttons:
                if button.collidepoint((mx, my)):
                    if pygame.mouse.get_pressed()[0]:
                        selected_option_letter = option_letter
                        feedback_shown = True
                        if selected_option_letter.upper() != correct_option.upper():
                            player.score = max(0, player.score - 20)
                        break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if feedback_shown:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if continue_button.collidepoint(event.pos):
                            return  # Salir de la función y continuar con el juego

        pygame.display.update()


def ask_open_ended_question(player, case_study, topic):
    user_input = ''
    input_active = True

    # Función para ajustar el texto dentro de un ancho máximo
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + word + ' '
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + ' '
        if current_line:
            lines.append(current_line)
        return lines

    # Ajustar el texto del caso práctico
    max_text_width = WIDTH - 100  # Margen de 50 píxeles en cada lado
    case_study_lines = wrap_text(case_study, FONT, max_text_width)

    # Variables para la retroalimentación
    is_correct = False
    explanation = ''

    # Variable para controlar si estamos mostrando la retroalimentación
    showing_feedback = False

    while True:
        SCREEN.fill(BACKGROUND_COLOR)
        draw_centered_text('Caso Práctico:', FONT, PRIMARY_COLOR, SCREEN, 50)

        # Mostrar el caso práctico ajustado
        y_text = 90  # Posición vertical inicial para el texto
        for line in case_study_lines:
            draw_text(line, FONT, BLACK, SCREEN, 50, y_text)
            y_text += FONT.get_height() + 5  # Altura de la línea más un espacio

        # Posicionar el cuadro de entrada debajo del texto
        prompt_y = y_text + 20

        if not showing_feedback:
            draw_centered_text('Escribe tu respuesta y presiona Enter:', FONT, PRIMARY_COLOR, SCREEN, prompt_y)

            input_box = pygame.Rect(50, prompt_y + 30, WIDTH - 100, 32)
            pygame.draw.rect(SCREEN, WHITE, input_box, border_radius=10)
            pygame.draw.rect(SCREEN, PRIMARY_COLOR, input_box, 2, border_radius=10)
            user_text_surface = FONT.render(user_input, True, BLACK)
            SCREEN.blit(user_text_surface, (input_box.x + 10, input_box.y + 5))
        else:
            # Mostrar retroalimentación
            if is_correct:
                draw_centered_text('¡Respuesta Correcta!', LARGE_FONT, ACCENT_COLOR, SCREEN, prompt_y + 50)
            else:
                draw_centered_text('Respuesta Incorrecta.', LARGE_FONT, ERROR_COLOR, SCREEN, prompt_y + 50)
                # Ajustar el texto de la explicación
                explanation_lines = wrap_text(explanation, SMALL_FONT, WIDTH - 100)
                y_explanation = prompt_y + 100
                for line in explanation_lines:
                    draw_text(line, SMALL_FONT, BLACK, SCREEN, 50, y_explanation)
                    y_explanation += SMALL_FONT.get_height() + 5

            # Botón 'Continuar'
            continue_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 80, 200, 50)
            pygame.draw.rect(SCREEN, PRIMARY_COLOR, continue_button, border_radius=25)
            draw_centered_text('CONTINUAR', FONT, WHITE, SCREEN, continue_button.y + 25)

            mx, my = pygame.mouse.get_pos()
            if continue_button.collidepoint((mx, my)):
                pygame.draw.rect(SCREEN, ACCENT_COLOR, continue_button, border_radius=25)
                draw_centered_text('CONTINUAR', FONT, WHITE, SCREEN, continue_button.y + 25)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not showing_feedback:
                if event.type == pygame.KEYDOWN:
                    if input_active:
                        if event.key == pygame.K_RETURN:
                            is_correct, explanation = evaluate_response(user_input, topic, case_study)
                            if not is_correct:
                                player.score = max(0, player.score - 10)
                            showing_feedback = True
                        elif event.key == pygame.K_BACKSPACE:
                            user_input = user_input[:-1]
                        else:
                            user_input += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if continue_button.collidepoint((mx, my)):
                        return  # Salir de la función y continuar con el juego

        pygame.display.update()

# Iniciar el juego
if __name__ == "__main__":
    main()