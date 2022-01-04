from classes import *
import pygame


def main():
    pygame.init()

    zero_boss = BossRoom('test_boss.txt')
    sp = zero_boss.load()

    hero = Hero(*sp, zero_boss)
    cam = Camera()

    overlay = Overlay(hero)
    text_field = TextAttack('t_test_boss.txt', zero_boss)

    fps = 50
    clock = pygame.time.Clock()
    running = True
    while running:
        attack = zero_boss.get_phase()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if attack:
                    attack = text_field.get_press(event.key)

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
        if attack:
            text_field.render(text_field.wrong)
        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    main()