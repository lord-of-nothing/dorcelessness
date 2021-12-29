import os
import pygame


SIZE = WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode(SIZE)
all_sprites = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        raise FileNotFoundError
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Hero(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('test_hero.png'), (30, 30))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Hero.image
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 300
        self.v = 8

    def move(self, keys):
        movement = [0, 0]
        if keys[pygame.K_UP]:
            movement[1] = -1
        if keys[pygame.K_DOWN]:
            movement[1] = 1
        if keys[pygame.K_LEFT]:
            movement[0] = -1
        if keys[pygame.K_RIGHT]:
            movement[0] = 1
        self.rect.x += movement[0] * self.v
        self.rect.y += movement[1] * self.v


def main():
    pygame.init()

    hero = Hero(all_sprites)
    fps = 40
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        hero.move(pygame.key.get_pressed())
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


main()