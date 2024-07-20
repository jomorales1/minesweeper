# Example file showing a basic pygame "game loop"
from models.game import Board, BoardState, BoardResult

import pygame

# constants
ROWS = 20
COLUMNS = 20
CELL_SIZE = 25
LEFT = 1
RIGHT = 3
GREY = (185, 185, 185)

# assets
UNOPENED = pygame.image.load('assets/unopened.png')
FLAG = pygame.image.load('assets/flag.png')
FLAG_WRONG = pygame.image.load('assets/flag_wrong.png')
MINE = pygame.image.load('assets/mine.png')
EXPLODED_MINE = pygame.image.load('assets/exploded_mine.png')
NUMBERS = [pygame.image.load(f'assets/{i}.png') for i in range(0, 9)]

# pygame setup
pygame.init()
screen = pygame.display.set_mode((COLUMNS * CELL_SIZE, ROWS * CELL_SIZE))
clock = pygame.time.Clock()
running = True

# minesweeper setup
board = Board(ROWS, COLUMNS)
completed = False

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    mouse_pos = None
    mouse_btn_pressed = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP and event.key == pygame.K_r:
            board = Board(ROWS, COLUMNS)
            completed = False
        if event.type == pygame.MOUSEBUTTONUP and event.button in [LEFT, RIGHT] and board.state != BoardState.FINISHED:
            mouse_pos = pygame.mouse.get_pos()
            mouse_btn_pressed = event.button

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(GREY)

    # RENDER YOUR GAME HERE
    if mouse_pos:
        mouse_x = mouse_pos[1] // CELL_SIZE
        mouse_y = mouse_pos[0] // CELL_SIZE
        if board.state == BoardState.EMPTY:
            board.fill(mouse_x, mouse_y)
        elif board.state == BoardState.STARTED:
            if mouse_btn_pressed == LEFT:
                board.reveal_cell(mouse_x, mouse_y)
            elif mouse_btn_pressed == RIGHT:
                board.place_flag(mouse_x, mouse_y)
        else:
            board.reveal_all()

    # Draw board
    for i in range(board.rows):
        for j in range(board.columns):
            asset = UNOPENED
            if board.cells[i][j].flagged:
                asset = FLAG
                if board.state == BoardState.FINISHED and not board.cells[i][j].is_mine:
                    asset = FLAG_WRONG
            elif board.cells[i][j].is_mine and board.cells[i][j].revealed:
                if board.cells[i][j].exploded:
                    asset = EXPLODED_MINE
                else:
                    asset = MINE
            elif board.cells[i][j].revealed:
                asset = NUMBERS[board.cells[i][j].value]
            cell_img = pygame.transform.scale(asset, (CELL_SIZE, CELL_SIZE))
            cell_rect = cell_img.get_rect()
            cell_rect.topleft = (j * CELL_SIZE, i * CELL_SIZE)
            cell_rect.topright = (j * CELL_SIZE, (i + 1) * CELL_SIZE)
            cell_rect.bottomleft = ((j + 1) * CELL_SIZE, i * CELL_SIZE)
            cell_rect.bottomright = ((j + 1) * CELL_SIZE, (i + 1) * CELL_SIZE)
            screen.blit(cell_img, cell_rect)
    
    # Check if board was completed
    if not completed:
        if board.state == BoardState.FINISHED and board.result == BoardResult.LOST:
            print('You lost...')
            completed = True
        if board.state == BoardState.FINISHED and board.result == BoardResult.WON:
            print('You won!!!')
            completed = True

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()