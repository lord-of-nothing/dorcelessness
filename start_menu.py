import sys
import pygame
from classes import load_image, load_font, screen, WIDTH, HEIGHT


def draw_start_menu():
    bg = load_image('start_menu_bg.png')
    screen.blit(bg, (0, 0))

    font_ru = pygame.font.Font(load_font('BadFontPixel.ttf'), 30)
    invite_0 = font_ru.render("для начала игры нажмите ", True, (240, 240, 240))
    font_en = pygame.font.Font(load_font('LastPriestess.ttf'), 35)
    invite_1 = font_en.render(" ENTER", True, (255, 255, 255))

    full_width = invite_0.get_width() + invite_1.get_width()
    x = WIDTH // 2 - full_width // 2
    y = int(HEIGHT * 0.1)
    screen.blit(invite_0, (x, y))
    screen.blit(invite_1, (x + invite_0.get_width(), y))


def main():
    pygame.init()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
        draw_start_menu()
        pygame.display.flip()