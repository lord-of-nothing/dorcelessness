import pygame
from classes import *


def main():
    pygame.init()

    zero_level = Level('test_level.txt')
    sp = zero_level.load()

    hero = Hero(*sp)
    cam = Camera()

    overlay = Overlay(hero)

    fps = 50
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not hero.is_alive():
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


main()