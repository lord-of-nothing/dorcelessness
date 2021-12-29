import os
import pygame


SIZE = WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode(SIZE)
bullets = pygame.sprite.Group()
hero_g = pygame.sprite.Group()
enemies = pygame.sprite.Group()
SPAWNPOINT = 300, 300


# этот файл предназначен для написания классов
# и базовой проверки их работоспособности
# в готовой игре он фигурировать не будет
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
        self.rect.x, self.rect.y = SPAWNPOINT
        self.v = 8

    def update(self):
        keys = pygame.key.get_pressed()
        movement = [0, 0]
        if keys[pygame.K_UP]:
            movement[1] = -1
        if keys[pygame.K_DOWN]:
            movement[1] = 1
        if keys[pygame.K_LEFT]:
            movement[0] = -1
        if keys[pygame.K_RIGHT]:
            movement[0] = 1
        if pygame.sprite.spritecollideany(self, enemies) or \
                pygame.sprite.spritecollideany(self, bullets):
            self.rect.x, self.rect.y = SPAWNPOINT
        self.rect.x += movement[0] * self.v
        self.rect.y += movement[1] * self.v


class MeleeEnemy(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('test_melee_enemy.png'), (30, 30))

    def __init__(self, x, y, v, *group):
        super().__init__(*group)
        self.image = MeleeEnemy.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.v = v

    def set_path(self, *phases):
        # первое число -- направление по X, второе -- по Y
        # третье -- время в секундах на это движение
        self.path = list(phases)
        self.current_phase = 0
        self.phase_started = pygame.time.get_ticks()

    def update(self):
        if not self.path:
            raise NameError
        movement = self.path[self.current_phase]
        self.rect.x += self.v * movement[0]
        self.rect.y += self.v * movement[1]
        if pygame.time.get_ticks() - self.phase_started >= movement[2] * 1000:
            self.current_phase = (self.current_phase + 1) % len(self.path)
            self.phase_started = pygame.time.get_ticks()


class RangeEnemy(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('test_range_enemy.png'), (30, 30))

    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = RangeEnemy.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.last_shot = pygame.time.get_ticks()
        self.dt = 1

    def shoot(self):
        if pygame.time.get_ticks() - self.last_shot >= self.dt * 1000:
            new_bullet = Bullet(self, bullets)
            self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.shoot()


class Bullet(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('test_bullet.png'), (15, 15))

    def __init__(self, sender, *group):
        super().__init__(*group)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.rect.x = sender.rect.x + 30
        self.rect.y = sender.rect.y + 15
        self.v = 10
        self.dir = (1, 0)

    def update(self):
        self.rect.x += self.dir[0] * self.v
        self.rect.y += self.dir[1] * self.v


def main():
    pygame.init()

    hero = Hero(hero_g)
    enemy1 = MeleeEnemy(100, 100, 2, enemies)
    enemy1.set_path((1, 0, 4), (0, 1, 4), (-1, 0, 4), (0, -1, 4))
    enemy2 = MeleeEnemy(0, 0, 1, enemies)
    enemy2.set_path((1, 1, 10), (-1, -1, 10))
    renemy = RangeEnemy(50, 500, enemies)

    fps = 40
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        hero.update()
        enemies.update()
        bullets.update()

        screen.fill((255, 255, 255))
        hero_g.draw(screen)
        enemies.draw(screen)
        bullets.draw(screen)

        pygame.display.flip()
        clock.tick(fps)


main()