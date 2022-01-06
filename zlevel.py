import sys
import pygame
from classes import *


def main():
    pygame.init()

    zero_level = Level('test_level.txt')
    sp = zero_level.load()

    hero = Hero(*sp, zero_level)
    cam = Camera()

    overlay = Overlay(hero)

    fps = 50
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        if not hero.is_alive():
            sys.exit()

        if zero_level.completed:
            running = False

        all_sprites.update()
        cam.update(hero)
        for sprite in all_sprites:
            cam.apply(sprite)
        for tile in background:
            cam.apply(tile)

        screen.fill((0, 0, 0))
        background.draw(screen)
        all_sprites.draw(screen)
        overlay.render()

        pygame.display.flip()
        clock.tick(fps)

    empty_groups()

    zero_boss = BossRoom('test_boss.txt')
    sp = zero_boss.load()

    hero.level = zero_boss
    hero.rect.x, hero.rect.y = sp

    text_field = TextAttack('t_test_boss.txt', zero_boss)

    overlay.set_boss(zero_boss.boss)

    running = True

    while running:
        attack = zero_boss.hero_attacks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if attack:
                    attack = text_field.get_press(event.key)

        if not hero.is_alive():
            running = False

        if zero_boss.boss.hp == 0:
            overlay.remove_boss()
            zero_boss.hero_attacks = False
            attack = False

        all_sprites.update()
        cam.update(hero)
        for sprite in all_sprites:
            cam.apply(sprite)
        for tile in background:
            cam.apply(tile)

        screen.fill((0, 0, 0))
        background.draw(screen)
        all_sprites.draw(screen)
        overlay.render()
        if attack:
            text_field.render(text_field.wrong)
        pygame.display.flip()
        clock.tick(fps)


main()