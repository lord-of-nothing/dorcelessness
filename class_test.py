import os
import pygame


SIZE = WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode(SIZE)

all_sprites = pygame.sprite.Group()
borders = pygame.sprite.Group()
bullets = pygame.sprite.Group()
hero_g = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemies_ranged = pygame.sprite.Group()
enemies_melee = pygame.sprite.Group()

SPAWNPOINT = 300, 300
BLOCK_SIDE = 50


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


def load_level(name):
    # получаем карту уровня
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        raise FileNotFoundError
    with open(fullname, encoding='utf-8') as f:
        level = [i[:-1] if i[-1] == '\n' else i for i in f]

    # получаем информацию о траекториях врагов ближнего боя
    fullname = os.path.join('data', 'm_' + name)
    if not os.path.isfile(fullname):
        raise FileNotFoundError
    with open(fullname, encoding='utf-8') as f:
        melees = dict()
        for en in f.readlines():
            en = en.replace('\n', '').split(' -> ')
            melees[en[0]] = []
            melees[en[0]].append(int(en[1]))

            moves = [tuple([int(i) for i in move.split(':')]) for move in en[2].split(' / ')]
            for move in moves:
                melees[en[0]].append(move)

    return level, melees


def check_hero_collision(hero):
    """Вспомогательная функция, чтобы не писать
    код проверки героя на столкновения дважды."""
    obstacle = pygame.sprite.spritecollideany(hero, enemies)
    if obstacle:
        hero.get_damage()
    else:
        obstacle = pygame.sprite.spritecollideany(hero, borders)
    return obstacle


class Unit(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(all_sprites, *group)
        self.image = self.__class__.image
        self.rect = self.image.get_rect()


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, im=None):
        super().__init__(borders, all_sprites)
        if im is None:
            self.image = load_image('test_wall.jpg')
        else:
            self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Level:
    def __init__(self, filename):
        self.map, self.melees = load_level(filename)

    def load(self):
        for row in range(len(self.map)):
            for block in range(len(self.map[row])):
                el = self.map[row][block]
                if el == '#':
                    Wall(block * BLOCK_SIDE, row * BLOCK_SIDE)
                elif el in "><^_":
                    RangeEnemy(block * BLOCK_SIDE, row * BLOCK_SIDE, el)
                elif el.isalpha():
                    MeleeEnemy(block * BLOCK_SIDE, row * BLOCK_SIDE,
                               self.melees[el][0], self.melees[el][1:])


class Hero(Unit):
    image = load_image('test_hero.png')

    def __init__(self):
        super().__init__(hero_g)
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

        blt = pygame.sprite.spritecollideany(self, bullets)
        if blt:
            blt.kill()
            self.get_damage()

        # чтобы враги ближнего боя сдвигали при столкновении
        if movement == [0, 0]:
            en = pygame.sprite.spritecollideany(self, enemies_melee)
            if not en or type(en) != MeleeEnemy:
                return
            phase = en.path[en.current_phase]
            if phase[0] == 1:
                self.rect.left = en.rect.right + 5
            else:
                self.rect.right = en.rect.left - 5
            if phase[1] == 1:
                self.rect.top = en.rect.bottom + 5
            else:
                self.rect.bottom = en.rect.top - 5

        # не ходим сквозь стены и врагов по горизонтали
        self.rect.x += movement[0] * self.v
        obstacle = check_hero_collision(self)
        if obstacle:
            if movement[0] == 1:
                self.rect.right = obstacle.rect.left
            elif movement[0] == -1:
                self.rect.left = obstacle.rect.right

        self.rect.y += movement[1] * self.v
        obstacle = check_hero_collision(self)
        if obstacle:
            if movement[1] == 1:
                self.rect.bottom = obstacle.rect.top
            elif movement[1] == -1:
                self.rect.top = obstacle.rect.bottom

    def get_damage(self):
        pass


class MeleeEnemy(Unit):
    image = load_image('test_melee_enemy.png')

    def __init__(self, x, y, v, phases):
        super().__init__(enemies, enemies_melee)
        self.rect.x = x
        self.rect.y = y
        self.v = v
        self.path = phases
        self.current_phase = 0
        self.phase_started = pygame.time.get_ticks()

    def update(self):
        movement = self.path[self.current_phase]
        self.rect.x += self.v * movement[0]
        self.rect.y += self.v * movement[1]
        if pygame.time.get_ticks() - self.phase_started >= movement[2] * 1000:
            self.current_phase = (self.current_phase + 1) % len(self.path)
            self.phase_started = pygame.time.get_ticks()


class RangeEnemy(Unit):
    image = load_image('test_range_enemy.png')

    def __init__(self, x, y, type):
        super().__init__(enemies, enemies_ranged)
        self.rect.x = x
        self.rect.y = y
        self.last_shot = pygame.time.get_ticks()
        self.dt = 1
        self.type = type
        if self.type == '<':
            self.image = pygame.transform.flip(self.image, True, False)
        elif self.type == '^':
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.type == '_':
            self.image = pygame.transform.rotate(self.image, -90)

    def shoot(self):
        if self.type == '>':
            Bullet(self, 1, 0)
        elif self.type == '<':
            Bullet(self, -1, 0)
        elif self.type == '^':
            Bullet(self, 0, -1)
        elif self.type == '_':
            Bullet(self, 0, 1)
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.last_shot >= self.dt * 1000:
            self.shoot()


class Bullet(Unit):
    image = load_image('test_bullet.png')

    def __init__(self, sender, dirx, diry):
        # изображение пули не меняет ориентацию в зависимости
        # от направления движения, т.к. планируется, что
        # в конечной версии пули будут центрально симметричными
        super().__init__(enemies, bullets)
        self.rect.x = sender.rect.x + 30
        self.rect.y = sender.rect.y + 15
        self.v = 10
        self.dir = dirx, diry

    def update(self):
        self.rect.x += self.dir[0] * self.v
        self.rect.y += self.dir[1] * self.v

        if pygame.sprite.spritecollideany(self, borders):
            self.kill()


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def main():
    pygame.init()

    hero = Hero()
    cam = Camera()

    zero_level = Level('test_level.txt')
    zero_level.load()

    fps = 50
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update()
        cam.update(hero)
        for sprite in all_sprites:
            cam.apply(sprite)

        screen.fill((255, 255, 255))
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(fps)


main()