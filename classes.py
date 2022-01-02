import os
import pygame

SIZE = WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode(SIZE)

all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
bullets = pygame.sprite.Group()
hero_g = pygame.sprite.Group()
enemies = pygame.sprite.Group()
boss_keys = pygame.sprite.Group()
background = pygame.sprite.Group()

SPAWNPOINT = 0, 0
BLOCK_SIDE = 32


# этот файл предназначен для написания классов
# и базовой проверки их работоспособности
# используемые на данный момент спрайты будут заменены
# как только всё остальное будет работать
# пока что используется симпатичный, но не соответствующий
# тематике игры пак ассетов из интернета
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


def level_from_file(name):
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


class Level:
    def __init__(self, filename):
        self.map, self.melees = level_from_file(filename)

    def load(self):
        global SPAWNPOINT
        for row in range(len(self.map)):
            for block in range(len(self.map[row])):
                el = self.map[row][block]
                x = block * BLOCK_SIDE
                y = row * BLOCK_SIDE
                if el == '-':
                    continue
                Floor(x, y)
                if el == '@':
                    SPAWNPOINT = x, y
                elif el == '#':
                    Wall(x, y)
                elif el in "><^_%":
                    RangeEnemy(x, y, el)
                elif el == '?':
                    Key(x, y)
                elif el.isalpha():
                    MeleeEnemy(x, y, self.melees[el][0],
                               self.melees[el][1:])


class Overlay:
    def __init__(self, hero):
        self.hero = hero
        self.color = pygame.Color("gray31")
        self.image_hp = load_image('hp.png')
        self.image_key = load_image('key_large.png')
        # не удалось найти информацию о лицензии данного шрифта
        # вроде как он бесплатный для личного использования
        # если окажется, что это не так, заменю на что-то другое
        self.font_file = 'data/BadFontPixel.ttf'

        self.w = 140
        self.h = self.image_key.get_height() + \
                 self.image_hp.get_height() + 30
        self.x = WIDTH - self.w
        self.y = HEIGHT - self.h

    def show(self):
        bg = pygame.Surface((self.w, self.h))
        bg.fill(self.color)

        # ключей собрано
        bg.blit(self.image_key, (10, 10))
        font = pygame.font.Font(self.font_file,
                                self.image_key.get_height())
        txt = font.render(f"{self.hero.keys}/4", True,
                          (255, 255, 255))
        bg.blit(txt, (self.w - txt.get_width() - 10, 10))

        # жизней осталось
        dist_from_top = self.image_key.get_height() + 20
        bg.blit(self.image_hp, (10, dist_from_top))
        font = pygame.font.Font(self.font_file,
                                self.image_hp.get_height())
        txt = font.render(str(self.hero.hp), True, (255, 255, 255))
        bg.blit(txt, (self.w - txt.get_width() - 10, dist_from_top))

        screen.blit(bg, (self.x, self.y))


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


class Unit(pygame.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(all_sprites, *group)
        self.image = self.__class__.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


class Wall(Unit):
    image = load_image('wall.png')

    def __init__(self, x, y):
        super().__init__(x, y, obstacles)


class Floor(Unit):
    image = load_image('floor.png')

    def __init__(self, x, y):
        super().__init__(x, y, background)
        self.remove(all_sprites)


class Hero(Unit):
    image = load_image('hero.png')

    def __init__(self):
        super().__init__(*SPAWNPOINT, hero_g)
        self.v = 8
        self.hp = 4
        # получив урон, герой становится бессмертным
        # на несколько секунд, и проходит через врагов
        self.immortal = False
        self.imm_start = 0
        self.keys = 0

    def update(self):
        # смотрим, куда нужно пойти
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

        # сбор ключей
        key = pygame.sprite.spritecollideany(self, boss_keys)
        if key and not self.immortal and keys[pygame.K_e]:
            self.keys += 1
            key.kill()
            if self.keys == 4:
                self.hp = 0
            # пока что завершаем игру, если все ключи собраны
            # ибо то, для чего нужны ключи, ещё не написано(

        # проверяем, не поймали ли пулю
        blt = pygame.sprite.spritecollideany(self, bullets)
        if blt and not self.immortal:
            if pygame.sprite.collide_mask(self, blt):
                blt.kill()
                self.get_damage()

        # проверка на контакт с врагами
        enm = pygame.sprite.spritecollideany(self, enemies)
        if enm and pygame.sprite.collide_mask(self, enm):
            self.get_damage()

        # не ходим сквозь стены и врагов по горизонтали
        self.rect.x += movement[0] * self.v
        wall = pygame.sprite.spritecollideany(self, obstacles)
        if wall:
            if movement[0] == 1:
                self.rect.right = wall.rect.left
            elif movement[0] == -1:
                self.rect.left = wall.rect.right

        self.rect.y += movement[1] * self.v
        wall = pygame.sprite.spritecollideany(self, obstacles)
        if wall:
            if movement[1] == 1:
                self.rect.bottom = wall.rect.top
            elif movement[1] == -1:
                self.rect.top = wall.rect.bottom

        # завершаем период бессмертия (если уже пора)
        if self.immortal and \
                pygame.time.get_ticks() - self.imm_start >= 2000:
            self.immortal = False
            self.image.set_alpha(255)

    def get_damage(self):
        if not self.immortal:
            self.hp -= 1
            self.immortal = True
            self.imm_start = pygame.time.get_ticks()
            self.image.set_alpha(128)

    def is_alive(self):
        return self.hp > 0


class MeleeEnemy(Unit):
    image = load_image('melee_enemy.png')

    def __init__(self, x, y, v, phases):
        super().__init__(x, y, enemies)
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
    image = load_image('range_enemy.png')

    def __init__(self, x, y, type):
        super().__init__(x, y, enemies)
        self.last_shot = pygame.time.get_ticks()
        self.dt = 1
        self.v_bullet = 10
        self.type = type
        if self.type == '<':
            self.image = pygame.transform.flip(self.image, True, False)
            self.last_shot += 250
        elif self.type == '^':
            self.image = pygame.transform.rotate(self.image, 90)
            self.last_shot += 500
        elif self.type == '_':
            self.image = pygame.transform.rotate(self.image, -90)
            self.last_shot += 750
        elif self.type == '%':
            self.image = load_image('circular_range_enemy.png')
            self.last_shot += 1000
            self.v_bullet = 5

    def shoot(self):
        if self.type == '>' or self.type == '%':
            Bullet(self, 1, 0, self.v_bullet)
        if self.type == '<' or self.type == '%':
            Bullet(self, -1, 0, self.v_bullet)
        if self.type == '^' or self.type == '%':
            Bullet(self, 0, -1, self.v_bullet)
        if self.type == '_' or self.type == '%':
            Bullet(self, 0, 1, self.v_bullet)
        if self.type == '%':
            Bullet(self, 1, 1, self.v_bullet)
            Bullet(self, 1, -1, self.v_bullet)
            Bullet(self, -1, 1, self.v_bullet)
            Bullet(self, -1, -1, self.v_bullet)
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.last_shot >= self.dt * 1000:
            self.shoot()


class Bullet(Unit):
    image = load_image('bullet.png')

    def __init__(self, sender, dirx, diry, v):
        # изображение пули не меняет ориентацию в зависимости
        # от направления движения, т.к. планируется, что
        # в конечной версии пули будут центрально симметричными
        super().__init__(sender.rect.x + BLOCK_SIDE // 2,
                         sender.rect.y + 8, bullets)
        self.v = v
        self.dir = dirx, diry

    def update(self):
        self.rect.x += self.dir[0] * self.v
        self.rect.y += self.dir[1] * self.v

        if pygame.sprite.spritecollideany(self, obstacles):
            self.kill()


class Key(Unit):
    image = load_image('key_small.png')

    def __init__(self, x, y):
        super().__init__(x, y, boss_keys)


def main():
    pygame.init()

    zero_level = Level('test_level.txt')
    zero_level.load()

    hero = Hero()
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
        overlay.show()

        pygame.display.flip()
        clock.tick(fps)


main()