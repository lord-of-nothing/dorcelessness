import sys
import classes
from classes import *


def draw_gameover():
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill((0, 0, 0))

    font = pygame.font.Font(load_font('LastPriestess.ttf'), 79)
    game_over_text = font.render("GAME OVER", True, (255, 255, 255))
    x = WIDTH // 2 - game_over_text.get_width() // 2
    y = int(HEIGHT * 0.2)
    bg.blit(game_over_text, (x, y))

    font = pygame.font.Font(load_font('BadFontPixel.ttf'), 43)
    congrats = font.render("поздравляю, вы умерли", True, (255, 255, 255))
    x = WIDTH // 2 - congrats.get_width() // 2
    y = int(HEIGHT * 0.4)
    bg.blit(congrats, (x, y))

    font = pygame.font.Font(load_font('BadFontPixel.ttf'), 30)
    font_en = pygame.font.Font(load_font('LastPriestess.ttf'), 35)
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


def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    classes.empty_groups(True)
                    return

        draw_gameover()
        pygame.display.flip()