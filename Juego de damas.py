import pygame

# Inicialización de Pygame
pygame.init()

# Configuración del bucle del juego
running = True

# Dimensiones de la ventana
width, height = 400, 400
square_size = width // 4

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Crear la ventana
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Juego de damas 4x4 Julián López")

# Representación del tablero
board = [
    [0, -1, 0, -1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [1, 0, 1, 0]
]

# Función para dibujar el tablero
def draw_board():
    for row in range(4):
        for col in range(4):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

# Función para dibujar las fichas
def draw_pieces():
    for row in range(4):
        for col in range(4):
            if board[row][col] == 1:
                pygame.draw.circle(screen, BLUE, (col * square_size + square_size // 2, row * square_size + square_size // 2), square_size // 4)
            elif board[row][col] == -1:
                pygame.draw.circle(screen, RED, (col * square_size + square_size // 2, row * square_size + square_size // 2), square_size // 4)

# Función para obtener todos los movimientos posibles
def get_possible_moves(board, player):
    moves = []
    for row in range(4):
        for col in range(4):
            if board[row][col] == player or board[row][col] == player * 2:  # Incluye fichas coronadas
                directions = [(-1, 1), (-1, -1), (1, 1), (1, -1)]
                for dr, dc in directions:
                    new_row = row + dr
                    new_col = col + dc
                    while 0 <= new_row < 4 and 0 <= new_col < 4:
                        if board[new_row][new_col] == 0:
                            moves.append((row, col, new_row, new_col))
                            break  # Detenerse si la casilla está vacía
                        elif board[new_row][new_col] == -player:
                            new_row += dr
                            new_col += dc
                            if 0 <= new_row < 4 and 0 <= new_col < 4 and board[new_row][new_col] == 0:
                                moves.append((row, col, new_row, new_col))
                                break  # Detenerse si se ha encontrado una captura
                        else:
                            break  # Detenerse si se encuentra una ficha del mismo color
                    new_row = row + dr
                    new_col = col + dc

    return moves

def make_move(board, move):
    start_row, start_col, end_row, end_col = move
    new_board = [row.copy() for row in board]  # Crear una copia del tablero
    new_board[end_row][end_col] = new_board[start_row][start_col]
    new_board[start_row][start_col] = 0

    # Verificar si hay una captura y eliminar la ficha capturada
    row_diff = end_row - start_row
    col_diff = end_col - start_col
    capture_row = start_row + row_diff // 2
    capture_col = start_col + col_diff // 2
    if abs(row_diff) == 2 and abs(col_diff) == 2:
        new_board[capture_row][capture_col] = 0

    return new_board

# Función para coronar una ficha
def coronate(board, row, col):
    if row == 0 and board[row][col] == 1:
        board[row][col] = 2  # Ficha roja coronada
    elif row == 3 and board[row][col] == -1:
        board[row][col] = -2  # Ficha azul coronada

# Función de evaluación
def evaluate(board, player):
    evaluation = 0
    opponent = -player

    # Recuento de piezas con bonificación por piezas con rey
    piece_value = 1.5 if abs(player) == 2 else 1
    evaluation += (sum(row.count(player) * piece_value for row in board) -
                   sum(row.count(opponent) * piece_value for row in board))

    # Bonificación posicional
    for row, col in [(0, 1), (0, 3), (3, 1), (3, 3)]:
        if board[row][col] == player:
            evaluation += 0.75  # Bonificación por córners
        elif board[row][col] == opponent:
            evaluation -= 0.25  # Penalización para el oponente en las esquinas
        if 1 <= row <= 2 and 1 <= col <= 2 and board[row][col] == player:
            evaluation += 0.25  # Bonificación por casillas centrales

    # Bonificación por fila de rey
    if (player == 1 and sum(row.count(2) for row in board[0:2])) > 0:
        evaluation += 1  # Bonificación por piezas con rey en las dos primeras filas del jugador
    elif (player == -1 and sum(row.count(-2) for row in board[2:4])) > 0:
        evaluation += 1  # Bonificación por piezas con rey en las dos primeras filas del oponente

    # Potencial de ataque
    for move in get_possible_moves(board, player):
        new_board = make_move(board.copy(), move)
        if len(get_possible_moves(new_board, opponent)) < len(get_possible_moves(board, opponent)):
            evaluation += 0.2  # Bonificación por movimientos que capturan las piezas del oponente.

    # Posicionamiento defensivo
    capturable_pieces = 0
    for row, col in [(r, c) for r in range(4) for c in range(4) if board[r][c] == opponent]:
        for dr, dc in [(-1, 1), (-1, -1), (1, 1), (1, -1)]:
            new_row, new_col = row + dr, col + dc
            while 0 <= new_row < 4 and 0 <= new_col < 4:
                if board[new_row][new_col] == player:
                    capturable_pieces += 1
                    break
                elif board[new_row][new_col] != 0:
                    break
                new_row += dr
                new_col += dc
    evaluation -= 0.1 * capturable_pieces  # Penalización por exponer piezas a capturar

    return evaluation

def game_over(board):
    for player in [1, -1]:
        if len(get_possible_moves(board, player)) > 0:
            return False  # Si hay movimientos, el juego continúa
    return True  # Si no hay movimientos para ninguno, el juego ha terminado

# Algoritmo Minimax
def minimax(board, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or game_over(board):
        return evaluate(board, maximizingPlayer)

    if maximizingPlayer:
        maxEval = -float('inf')
        for move in get_possible_moves(board, 1):
            new_board = make_move(board, move)
            eval = minimax(new_board, depth - 1, alpha, beta, False)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = float('inf')
        for move in get_possible_moves(board, -1):
            new_board = make_move(board, move)
            eval = minimax(new_board, depth - 1, alpha, beta, True)
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval


# Función para el movimiento de la IA
def make_ai_move(board):
  best_move = None
  best_eval = -float('inf')

  for move in get_possible_moves(board, -1):  # La IA juega como jugador (oponente)
    new_board = make_move(board.copy(), move)  # Crea una copia del tablero para evitar modificar el original.
    eval = minimax(new_board, 3, -float('inf'), float('inf'), False)  # Minimizar para IA (profundidad=3)
    if eval > best_eval:
      best_eval = eval
      best_move = move

  board[:] = make_move(board, best_move)  # Actualiza el tablero real con el mejor movimiento.
  
  
# Definir jugador
player = 1  

selected_piece = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            col, row = event.pos[0] // square_size, event.pos[1] // square_size
            if event.button == 1:  # Haga clic izquierdo para seleccionar
                if selected_piece is None:
                    if board[row][col] == player:
                        selected_piece = (row, col)
                else:
                    move = (selected_piece[0], selected_piece[1], row, col)
                    if move in get_possible_moves(board, player):
                        board = make_move(board, move)
                        selected_piece = None
                        if not game_over(board):
                            player = -player
                            make_ai_move(board)
                            player = -player
            elif event.button == 3:  # Haga clic derecho para deseleccionar
                if selected_piece is not None:
                    selected_piece = None

# Dibuja el tablero y las piezas
    draw_board()
    draw_pieces()
    
    # Resaltar la pieza seleccionada 
    if selected_piece:
        pygame.draw.circle(screen, GREEN, (selected_piece[1] * square_size + square_size // 2, selected_piece[0] * square_size + square_size // 2), square_size // 3)

    pygame.display.update()

pygame.quit()