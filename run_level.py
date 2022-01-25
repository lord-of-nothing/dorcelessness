import sys
from classes import *
from fullscreens import show_gameover


def run_level(n):
    pygame.init()

    zero_level = Level(n)
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
            show_gameover()
            return None

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
        hero.score -= 0.02

    empty_groups()

    zero_boss = BossRoom(n)
    sp = zero_boss.load()

    hero.level = zero_boss
    hero.rect.x, hero.rect.y = sp

    text_field = TextAttack(n, zero_boss)

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
            show_gameover()
            return None

        if zero_boss.boss.hp == 0:
            overlay.remove_boss()
            zero_boss.hero_attacks = False
            attack = False

        if zero_boss.completed:
            running = False

        all_sprites.update()
        cam.update(hero)
        for sprite in all_sprites:
            cam.apply(sprite)
        for tile in background:
            cam.apply(tile)
        if zero_boss.boss.last_hero_pos is not None:
            zero_boss.boss.last_hero_pos[0] += cam.dx
            zero_boss.boss.last_hero_pos[1] += cam.dy

        screen.fill((0, 0, 0))
        background.draw(screen)
        all_sprites.draw(screen)
        overlay.render()
        if attack:
            text_field.render(text_field.wrong)
        pygame.display.flip()
        hero.score -= 0.02
        clock.tick(fps)

    empty_groups(True)

    return int(hero.score) if hero.score > 0 else 0