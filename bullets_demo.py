import os
import pygame


SIZE = WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode(SIZE)
all_sprites = pygame.sprite.Group()


# используемые на данный момент спрайты будут заменены
# как только всё остальное будет работать
# пока что здесь первые попавшиеся картинки из интернета
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


class MeleeEnemy(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('test_melee_enemy.png'), (30, 30))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = MeleeEnemy.image
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 150
        self.v = 2
        # первое число -- направление по X, второе -- по Y
        # третье -- время в секундах на это движение
        self.path = [(1, 0, 2), (-1, 0, 2)]
        self.current_phase = 0
        self.phase_started = pygame.time.get_ticks()

    def move(self):
        movement = self.path[self.current_phase]
        self.rect.x += self.v * movement[0]
        self.rect.y += self.v * movement[1]
        if pygame.time.get_ticks() - self.phase_started >= movement[2] * 1000:
            self.current_phase = (self.current_phase + 1) % len(self.path)
            self.phase_started = pygame.time.get_ticks()


def main():
    pygame.init()

    hero = Hero(all_sprites)
    enemy = MeleeEnemy(all_sprites)
    fps = 40
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        enemy.move()
        hero.move(pygame.key.get_pressed())
        screen.fill((255, 255, 255))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


main()