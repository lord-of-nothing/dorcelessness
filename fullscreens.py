import sys

import pygame

from classes import *


def show_gameover():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    empty_groups(True)
                    return

        bg = pygame.Surface((WIDTH, HEIGHT))
        bg.fill((0, 0, 0))

        font = pygame.font.Font(EN_FONT_LOCATION, 79)
        game_over_text = font.render("GAME OVER", True, (255, 255, 255))
        x = WIDTH // 2 - game_over_text.get_width() // 2
        y = int(HEIGHT * 0.2)
        bg.blit(game_over_text, (x, y))

        font = pygame.font.Font(RU_FONT_LOCATION, 43)
        congrats = font.render("поздравляю, вы умерли", True, (255, 255, 255))
        x = WIDTH // 2 - congrats.get_width() // 2
        y = int(HEIGHT * 0.4)
        bg.blit(congrats, (x, y))

        font = pygame.font.Font(RU_FONT_LOCATION, 30)
        font_en = pygame.font.Font(EN_FONT_LOCATION, 35)
        offer_0 = font.render("нажмите ", True, (243, 243, 243))
        offer_1 = font_en.render(" R, ", True, (250, 250, 250))
        offer_2 = font.render("чтобы начать уровень заново", True, (243, 243, 243))
        offer_surf = pygame.Surface((offer_0.get_width() + offer_1.get_width() +
                                     offer_2.get_width(), offer_1.get_height()))
        offer_surf.blit(offer_0, (0, 0))
        offer_surf.blit(offer_1, (offer_0.get_width(), 0))
        offer_surf.blit(offer_2, (offer_0.get_width() + offer_1.get_width(), 0))

        x = WIDTH // 2 - offer_surf.get_width() // 2
        y = int(HEIGHT * 0.9)
        bg.blit(offer_surf, (x, y))

        screen.blit(bg, (0, 0))

        pygame.display.flip()


def show_start_menu():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

        bg = load_image('start_menu_bg.png')
        screen.blit(bg, (0, 0))

        font_ru = pygame.font.Font(RU_FONT_LOCATION, 30)
        invite_0 = font_ru.render("для начала игры нажмите ", True, (240, 240, 240))
        font_en = pygame.font.Font(EN_FONT_LOCATION, 35)
        invite_1 = font_en.render(" ENTER", True, (255, 255, 255))

        full_width = invite_0.get_width() + invite_1.get_width()
        x = WIDTH // 2 - full_width // 2
        y = int(HEIGHT * 0.1)
        screen.blit(invite_0, (x, y))
        screen.blit(invite_1, (x + invite_0.get_width(), y))

        pygame.display.flip()


def show_level_completed(n, score, fullscore):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

        # уровень пройден
        bg = pygame.Surface((WIDTH, HEIGHT))
        font = pygame.font.Font(RU_FONT_LOCATION, 50)
        text = font.render(f"Уровень {n} пройден!", True, (234, 234, 234))
        left_border = WIDTH // 2 - text.get_width() // 2
        bg.blit(text, (left_border, int(HEIGHT * 0.2)))

        # пояснения о счёте
        font = pygame.font.Font(RU_FONT_LOCATION, 35)
        text = font.render("Счёт за уровень: ", True, (234, 234, 234))
        left_border = WIDTH // 2 - text.get_width() // 2
        bg.blit(text, (left_border, int(HEIGHT * 0.4)))
        text = font.render("Суммарный счёт: ", True, (234, 234, 234))
        left_border = WIDTH // 2 - text.get_width() // 2
        bg.blit(text, (left_border, int(HEIGHT * 0.6)))

        # счёт
        font = pygame.font.Font(RU_FONT_LOCATION, 40)
        text = font.render(str(score), True, (255, 255, 255))
        left_border = WIDTH // 2 - text.get_width() // 2
        bg.blit(text, (left_border, int(HEIGHT * 0.45)))
        text = font.render(str(fullscore), True, (255, 255, 255))
        left_border = WIDTH // 2 - text.get_width() // 2
        bg.blit(text, (left_border, int(HEIGHT * 0.65)))

        # сообщение "для продолжения нажмите ENTER"
        font = pygame.font.Font(RU_FONT_LOCATION, 35)
        text_l = font.render("Для продолжения нажмите ", True, (234, 234, 234))
        font = pygame.font.Font(EN_FONT_LOCATION, 40)
        text_r = font.render(" ENTER", True, (234, 234, 234))
        left_border = WIDTH // 2 - (text_r.get_width() + text_l.get_width()) // 2
        bg.blit(text_l, (left_border, int(HEIGHT * 0.9)))
        bg.blit(text_r, (left_border + text_l.get_width(), int(HEIGHT * 0.9)))

        screen.fill((0, 0, 0))
        screen.blit(bg, (0, 0))

        pygame.draw.line(screen, (234, 234, 234), (65, int(HEIGHT * 0.3)),
                         (WIDTH - 65, int(HEIGHT * 0.3)), 5)

        pygame.display.flip()