import os
import pygame
import math
from random import choice, uniform


SIZE = WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode(SIZE)

all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
bullets = pygame.sprite.Group()
hero_g = pygame.sprite.Group()
enemies = pygame.sprite.Group()
boss_keys = pygame.sprite.Group()
background = pygame.sprite.Group()
zones = pygame.sprite.Group()
doors = pygame.sprite.Group()
exits = pygame.sprite.Group()

BLOCK_SIDE = 32
INFECTED = pygame.Color('olivedrab')


def load_image(name, colorkey=None):
    """Загружает картинку из файла."""
    fullname = os.path.join('data', 'graphic', name)
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
    """Отвечает за загрузку уровней из текстовых файлов."""
    # получаем карту уровня
    fullname = os.path.join('data', 'levels', name)
    if not os.path.isfile(fullname):
        raise FileNotFoundError
    with open(fullname, encoding='utf-8') as f:
        level = [i[:-1] if i[-1] == '\n' else i for i in f]

    if 'boss' in name:
        return level, None

    # получаем информацию о траекториях врагов ближнего боя
    fullname = os.path.join('data', 'levels', 'm_' + name)
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


def load_text(name):
    """Загрузка текста в боссфайт."""
    fullname = os.path.join('data', 'levels', name)
    if not os.path.isfile(fullname):
        raise FileNotFoundError
    with open(fullname, encoding='utf-8') as f:
        text = f.read().splitlines()
    return text


def load_font(name):
    """Возвращает расположение файла шрифта."""
    fullname = os.path.join('data', 'graphic', name)
    return fullname


RU_FONT_LOCATION = load_font('BadFontPixel.ttf')
EN_FONT_LOCATION = load_font('nokiafc22.ttf')


def empty_groups(kill_hero=False):
    """Очищает группы спрайтов на переходе от
    уровня к боссу."""
    for sp in all_sprites:
        if not kill_hero and sp in hero_g:
            continue
        sp.kill()
    for tile in background:
        tile.kill()
    if not kill_hero:
        hero_g.add(all_sprites.sprites()[0])


class Level:
    """Класс основной части уровня."""
    def __init__(self, filename):
        self.map, self.melees = level_from_file(filename)
        self.completed = False

    def load(self):
        spawnpoint = None
        # расстановка элементов на уровне
        for row in range(len(self.map)):
            for block in range(len(self.map[row])):
                el = self.map[row][block]
                x = block * BLOCK_SIDE
                y = row * BLOCK_SIDE
                if el == '-':
                    continue
                Floor(x, y)
                if el == '@':
                    spawnpoint = x, y
                elif el == 'D':
                    Door(x, y)
                elif el == '#':
                    Wall(x, y)
                elif el in "><^_%":
                    RangeEnemy(x, y, el)
                elif el == '?':
                    Key(x, y)
                elif el == '~':
                    InfectedZone(x, y)
                elif el.isalpha():
                    MeleeEnemy(x, y, self.melees[el][0],
                               self.melees[el][1:])
        if spawnpoint is None:
            raise ValueError
        return spawnpoint


class BossRoom:
    """Класс битвы с боссом."""
    def __init__(self, filename):
        self.map = level_from_file(filename)[0]
        self.boss = None
        self.hero_attacks = False
        self.completed = False

    def load(self):
        spawnpoint = None
        for row in range(len(self.map)):
            for block in range(len(self.map[row])):
                el = self.map[row][block]
                x = block * BLOCK_SIDE
                y = row * BLOCK_SIDE
                if el == '-':
                    continue
                Floor(x, y)
                if el.isdigit():
                    self.boss = Boss(x, y, el, 8, 1, self)
                elif el == 'D':
                    Exit(x, y, self)
                elif el == '@':
                    spawnpoint = x, y
                elif el == '#':
                    Wall(x, y)
        if self.boss is None or spawnpoint is None:
            raise ValueError
        return spawnpoint

    def change_phase(self):
        self.hero_attacks = not self.hero_attacks
        self.boss.new_phase()


class TextAttack:
    """Класс виджета текстового ввода
    в бою с боссом."""
    def __init__(self, filename, level):
        self.w = int(WIDTH * 0.8)
        self.h = int(HEIGHT * 0.2)

        self.level = level
        self.inp_start = pygame.time.get_ticks()  # начало атаки

        self.font_size = int(HEIGHT * 0.1)
        self.font = pygame.font.Font(EN_FONT_LOCATION,
                                     self.font_size)
        self.bg_color = pygame.Color('darkslategray')
        self.ahead_color = pygame.Color('white')
        self.already_color = pygame.Color('azure4')
        self.right_color = pygame.Color('aquamarine3')
        self.wrong_color = pygame.Color('coral2')

        self.text = load_text(filename)
        self.str = self.text[0].split()
        self.str_n = 0
        self.word = 0
        self.char = 0
        self.wrong = False

        self.boss = self.level.boss
        self.boss.hp = self.get_text_len()

    def get_text_len(self):
        return sum([sum([1 for j in i if j != ' ']) for i in self.text])

    def render(self, wrong):
        """Отрисовываем это окно."""
        bg = pygame.Surface((self.w, self.h))
        bg.fill(self.bg_color)
        word = self.str[self.word].upper()
        ch = self.char
        alr = self.font.render(word[:ch], True, self.already_color)
        if wrong:
            wrng = self.font.render(word[ch], True, self.wrong_color)
            ch += 1
        now = self.font.render(word[ch:], True, self.ahead_color)

        if wrong:
            sum_w = alr.get_width() + wrng.get_width() + \
                    now.get_width()
        else:
            sum_w = alr.get_width() + now.get_width()
        left = self.w // 2 - sum_w // 2
        top = self.h // 2 - alr.get_height() // 2
        bg.blit(alr, (left, top))
        if wrong:
            bg.blit(wrng, (left + alr.get_width(), top))
            bg.blit(now, (left + alr.get_width() + wrng.get_width(), top))
        else:
            bg.blit(now, (left + alr.get_width(), top))

        b = 5  # толщина белой обводки
        pygame.draw.rect(screen, (255, 255, 255), (int(WIDTH * 0.1) - b,
                                                   int(HEIGHT * 0.4) - b,
                                                   self.w + 2 * b, self.h + 2 * b))
        screen.blit(bg, (int(WIDTH * 0.1), int(HEIGHT * 0.4)))

    def get_press(self, key):
        """Обработка нажатий клавиатуры."""
        word = self.str[self.word]
        try:
            if chr(key) == word[self.char]:
                self.char += 1
                self.boss.hp -= 1
                self.wrong = False
            else:
                self.wrong = True
        except ValueError:
            return True
        if self.char == len(word):
            self.word += 1
            self.char = 0
        if self.word == len(self.str):
            self.word = 0
            self.str_n += 1
            if self.str_n == len(self.text):
                self.boss.kill()
                return False
            self.str = self.text[self.str_n].split()
            self.level.change_phase()
            return False
        return True


class Overlay:
    def __init__(self, hero):
        self.hero = hero
        self.boss = None
        self.max_hp = -1
        self.color = pygame.Color("gray31")
        self.image_hp = load_image('hp.png')
        self.image_key = load_image('key_large.png')
        # не удалось найти информацию о лицензии данного шрифта
        # вроде как он бесплатный для личного использования
        # если окажется, что это не так, заменю на что-то другое
        self.font_file = RU_FONT_LOCATION

        self.w = 140
        self.bar_block = (self.w - 20) // self.hero.full_charge
        self.bar_h = 10
        self.h = self.image_key.get_height() + \
                 self.image_hp.get_height() + 40 + \
                 self.bar_h
        self.x = WIDTH - self.w
        self.y = HEIGHT - self.h

    def render(self):
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

        # заряд
        pygame.draw.rect(bg, (255, 0, 0), (10, self.h - 20,
                                           self.w - 20, self.bar_h))
        pygame.draw.rect(bg, (0, 255, 0), (10, self.h - 20,
                                           self.bar_block * self.hero.charge,
                                           self.bar_h))

        screen.blit(bg, (self.x, self.y))

        if self.boss is None:
            return

        bar_h = 30
        bg = pygame.Surface((self.max_hp + 12, bar_h))
        bg.fill((0, 0, 0))
        pygame.draw.rect(bg, (255, 255, 255),
                         (0, 0, bg.get_width(), bg.get_height()), 3)
        pygame.draw.rect(bg, (255, 255, 255), (6, 6, self.boss.hp, 18))

        screen.blit(bg, (10, HEIGHT - 10 - bar_h))

    def set_boss(self, boss):
        self.boss = boss
        self.max_hp = self.boss.hp

    def remove_boss(self):
        self.boss = None
        self.max_hp = -1


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


class AnimatedUnit(Unit):
    def __init__(self, x, y, columns, rows, *group):
        super().__init__(x, y, *group)
        self.frames = []
        self.cut_sheet(self.image, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.right = True

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))


class Wall(Unit):
    image = load_image('wall.png')

    def __init__(self, x, y):
        super().__init__(x, y, obstacles)


class Door(Unit):
    image = load_image('closed_door.png')

    def __init__(self, x, y):
        super().__init__(x, y, obstacles, doors)
        self.hero = None
        self.open = False

    def update(self):
        if self.hero is None:
            if hero_g.sprites():
                self.hero = hero_g.sprites()[0]
            else:
                return
        if not self.open and self.hero.keys == 4:
            self.image = load_image('open_door.png')
            self.open = True


class Exit(Unit):
    image = load_image('closed_door.png')

    def __init__(self, x, y, level):
        super().__init__(x, y, obstacles, exits)
        self.hero = hero_g.sprites()[0]
        self.level = level
        self.open = False
        self.boss = None

    def update(self):
        if self.boss is None and self.level.boss is not None:
            self.boss = self.level.boss
        if not self.open and self.boss.hp == 0:
            self.image = load_image('open_door.png')
            self.open = True


class Floor(Unit):
    image = load_image('floor.png')

    def __init__(self, x, y):
        super().__init__(x, y, background)
        self.remove(all_sprites)  # чтобы ничего не перекрывалось


class Hero(AnimatedUnit):
    image = load_image('hero.png')

    def __init__(self, x, y, level):
        super().__init__(x, y, 6, 1, hero_g)
        self.v = 8
        self.hp = 4
        # получив урон, герой становится бессмертным
        # на несколько секунд, и проходит через врагов
        self.immortal = False
        self.imm_start = 0
        self.image.set_alpha(255)
        self.keys = 0

        self.charge = self.full_charge = 20
        self.dot_period = 150
        self.last_tick = 0

        self.level = level

        self.last_frame_time = pygame.time.get_ticks()
        self.change_frame_dt = 100

        self.score = 322

    def update(self):
        if self.level.__class__ == BossRoom and self.level.hero_attacks:
            return

        if pygame.time.get_ticks() - self.change_frame_dt >= self.last_frame_time:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if not self.right:
                self.image = pygame.transform.flip(self.image, True, False)
            self.last_frame_time = pygame.time.get_ticks()
            self.mask = pygame.mask.from_surface(self.image)
            if self.immortal:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)

        # смотрим, куда нужно пойти
        keys = pygame.key.get_pressed()
        movement = [0, 0]
        if keys[pygame.K_UP]:
            movement[1] = -1
        if keys[pygame.K_DOWN]:
            movement[1] = 1
        if keys[pygame.K_LEFT]:
            movement[0] = -1
            if self.right:
                self.right = False
        if keys[pygame.K_RIGHT]:
            movement[0] = 1
            if not self.right:
                self.right = True

        # сбор ключей
        key = pygame.sprite.spritecollideany(self, boss_keys)
        if key and not self.immortal and keys[pygame.K_e]:
            self.keys += 1
            key.kill()

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

        # заражённые области
        inf = pygame.sprite.spritecollideany(self, zones)
        if inf and pygame.sprite.collide_mask(self, inf):
            self.get_dot()

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
            if wall in doors and not self.immortal and \
                    self.keys == 4 and keys[pygame.K_e]:
                self.level.completed = True
            if wall in exits and self.level.boss.hp == 0 and \
                    keys[pygame.K_e]:
                self.level.completed = True
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
            self.score *= 0.9

    def get_dot(self):
        if self.charge == 0:
            if pygame.time.get_ticks() - self.last_tick >= self.dot_period:
                self.get_damage()
        if not self.immortal:
            if pygame.time.get_ticks() - self.last_tick >= self.dot_period:
                self.charge -= 1
                self.last_tick = pygame.time.get_ticks()

    def is_alive(self):
        return self.hp > 0


class MeleeEnemy(AnimatedUnit):
    image = load_image('melee_enemy.png')

    def __init__(self, x, y, v, phases):
        super().__init__(x, y, 4, 1, enemies)
        self.v = v
        self.path = phases
        self.current_phase = 0
        self.phase_started = pygame.time.get_ticks()

        self.last_frame_time = pygame.time.get_ticks()
        self.change_frame_dt = 100

    def update(self):
        if pygame.time.get_ticks() - self.change_frame_dt >= self.last_frame_time:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if not self.right:
                self.image = pygame.transform.flip(self.image, True, False)
            self.mask = pygame.mask.from_surface(self.image)
            self.last_frame_time = pygame.time.get_ticks()

        movement = self.path[self.current_phase]
        self.rect.x += self.v * movement[0]
        if movement[0] > 0:
            self.right = True
        elif movement[0] < 0:
            self.right = False
        self.rect.y += self.v * movement[1]
        if pygame.time.get_ticks() - self.phase_started >= movement[2] * 1000:
            self.current_phase = (self.current_phase + 1) % len(self.path)
            self.phase_started = pygame.time.get_ticks()


class RangeEnemy(AnimatedUnit):
    image = load_image('range_enemy.png')

    def __init__(self, x, y, type):
        super().__init__(x, y, 9, 1, enemies)
        self.last_shot = pygame.time.get_ticks()
        self.dt = 1
        self.v_bullet = 10
        self.type = type
        if self.type == '<':
            self.last_shot += 250
        elif self.type == '^':
            self.last_shot += 500
        elif self.type == '_':
            self.last_shot += 750
        elif self.type == '%':
            self.last_shot += 1000
            self.v_bullet = 5

        self.last_frame_time = pygame.time.get_ticks()
        self.change_frame_dt = 135

    def shoot(self):
        if self.type == '>' or self.type == '%':
            Bullet(self, self.v_bullet, 0)
        if self.type == '<' or self.type == '%':
            Bullet(self, -self.v_bullet, 0)
        if self.type == '^' or self.type == '%':
            Bullet(self, 0, -self.v_bullet)
        if self.type == '_' or self.type == '%':
            Bullet(self, 0, self.v_bullet)
        if self.type == '%':
            Bullet(self, self.v_bullet, self.v_bullet)
            Bullet(self, self.v_bullet, -self.v_bullet)
            Bullet(self, -self.v_bullet, self.v_bullet)
            Bullet(self, -self.v_bullet, -self.v_bullet)
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.change_frame_dt >= self.last_frame_time:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.mask = pygame.mask.from_surface(self.image)
            self.last_frame_time = pygame.time.get_ticks()

        if pygame.time.get_ticks() - self.last_shot >= self.dt * 1000:
            self.shoot()


class Boss(AnimatedUnit):
    def __init__(self, x, y, n, cols, rows, stage):
        Boss.image = load_image(f"boss_{n}.png")
        super().__init__(x, y, cols, rows, enemies)
        self.stage = stage
        self.hp = -1

        self.phase_len = 10000
        self.phase_start = self.last_shot = pygame.time.get_ticks()

        self.shot_types = ['hero', 'round']
        self.current_type = self.pick_attack()

        self.dt = 500
        self.last_shot = 0

        self.shoot = False
        self.timeout = 1350
        self.timeout_start = pygame.time.get_ticks()

        self.last_frame_time = pygame.time.get_ticks()
        self.change_frame_dt = 100

    def update(self):
        if pygame.time.get_ticks() - self.change_frame_dt >= self.last_frame_time:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if not self.right:
                self.image = pygame.transform.flip(self.image, True, False)
            self.mask = pygame.mask.from_surface(self.image)
            self.last_frame_time = pygame.time.get_ticks()

        if self.stage.hero_attacks:
            if pygame.time.get_ticks() - self.phase_start >= self.phase_len:
                self.stage.change_phase()
                self.new_phase()
                self.phase_start = pygame.time.get_ticks()
            return

        if not self.shoot:
            if pygame.time.get_ticks() - self.timeout_start >= self.timeout:
                self.shoot = True
            return

        if self.shoot and pygame.time.get_ticks() - self.last_shot >= self.dt:
            if self.current_type == 'hero':
                self.dt = 135
                self.attack_hero()
            elif self.current_type == 'round':
                self.dt = 351
                self.attack_around()
            self.last_shot = pygame.time.get_ticks()

        if pygame.time.get_ticks() - self.phase_start >= self.phase_len:
            self.stage.change_phase()
            self.phase_start = pygame.time.get_ticks()

    def new_phase(self):
        self.phase_start = pygame.time.get_ticks()
        self.current_type = self.pick_attack()
        self.timeout_start = pygame.time.get_ticks()
        self.shoot = False
        bullets.empty()

    def pick_attack(self):
        return choice(self.shot_types)

    def attack_around(self):
        v = 4
        # Bullet(self, v, 0)
        # Bullet(self, 0, v)
        # Bullet(self, -v, 0)
        # Bullet(self, 0, -v)

        for _ in range(16):
            mult_x = uniform(0.0, 1.0) * choice([-1, 1])
            vx = v * mult_x
            vy = round(math.sqrt(v ** 2 - vx ** 2), 2) * choice([-1, 1])
            Bullet(self, vx, vy)

    def attack_hero(self):
        """Выстрел в текущее местоположение героя.
        Математика позаимствована со StackOverflow."""
        hero = hero_g.sprites()[0]
        h_mid = hero.rect.x + hero.rect.w // 2, \
                hero.rect.y + hero.rect.h // 2
        dir = (h_mid[0] - self.rect.x,
               h_mid[1] - self.rect.y)
        length = math.hypot(*dir)
        if length == 0.0:
            dir = (0, -1)
        else:
            dir = (dir[0] / length, dir[1] / length)
        v = 7
        Bullet(self, v * dir[0], v * dir[1])


class InfectedZone(Unit):
    r = 63
    image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    circle = pygame.draw.circle(image, INFECTED, (r, r), r)
    image.set_alpha(63)

    def __init__(self, x, y):
        super().__init__(x, y, zones)


class Bullet(Unit):
    image = load_image('bullet.png')

    def __init__(self, sender, vx, vy):
        # изображение пули не меняет ориентацию в зависимости
        # от направления движения, т.к. планируется, что
        # в конечной версии пули будут центрально симметричными
        super().__init__(sender.rect.x + BLOCK_SIDE // 2,
                         sender.rect.y + 8, bullets)
        self.vx = vx
        self.vy = vy

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        if pygame.sprite.spritecollideany(self, obstacles):
            self.kill()


class Key(Unit):
    image = load_image('key_small.png')

    def __init__(self, x, y):
        super().__init__(x, y, boss_keys)


if __name__ == '__main__':
    print("you failed, now suffer")
