import asyncio
from json import load
from os import listdir
from random import randint, randrange, choice
from sys import exit as sys_exit

import pygame



pygame.init()


TILE_SIZE = 16
vec = pygame.Vector2
FPS = 60
SYSTEM_METRICS = [pygame.display.Info().current_w, pygame.display.Info().current_h]
AR = SYSTEM_METRICS[0] / SYSTEM_METRICS[1]

#===========================================================================



def state_float():
    pass

def state_exit():
    States.current = None

def state_fullscreen(mode=0):
    global full_screen

    if mode>0:
        States.full_screen = not States.full_screen

    if mode<0:
        States.full_screen = False

    if States.full_screen:
        return pygame.display.set_mode(SYSTEM_METRICS, pygame.FULLSCREEN, pygame.SCALED)
    else:
        W =  1200
        WC, HC = W, round(W / AR)
        print(SYSTEM_METRICS, WC,HC)
        return pygame.display.set_mode([WC,HC]) #, pygame.SCALED)

class States:
    states = {"exit":state_exit, "float":state_float, "fullscreen": state_fullscreen}
    current = None
    name = "float"
    has_changed = False
    clear_change = False
    last = "float"
    full_screen = False


    def __init__(self, name):
        if self.states.get(name, None) is None:
            try:
                self.states[name] = globals()[name]().draw

                print(f"Game State {name=} ready !")
            except KeyError:
                print(f"Game State {name=} not ready yet")

        self.state = name

    def __call__(self):
        self.select(self.state)

    @classmethod
    def select(cls, state):
        if state != cls.name:
            print("state: ", cls.name, "=>", state )
            if cls.states.get(state,None) is None:
                cls(state)

            cls.last = cls.name
            cls.name = state
            cls.current = cls.states[state]
            cls.has_changed = True

    @classmethod
    def changed(cls, *args):
        cls.clear_change = True
        if cls.has_changed:
            return cls.last not in args
        return False


    @classmethod
    def draw(cls):
        if cls.current:
            if cls.clear_change:
                cls.has_changed = False

            Base.display.fill((0, 0, 0))
            cls.current()
            if cls.current:
                pygame.display.update()

        return cls.current


    @classmethod
    def previous(cls):
        cls.select(cls.last)


#===========================================================================









def get_image_from_surface(loaded_image, x, y, width, height):
    surf = pygame.Surface((width, height))
    surf.blit(loaded_image, (0, 0), pygame.Rect(x, y, width, height))
    surf.set_colorkey((0, 0, 0))
    return surf


def load_img(img):
    img = pygame.image.load(f'data/image/{img}.png').convert_alpha()
    return img


def load_snd(snd):
    return pygame.mixer.Sound(f'data/sfx/{snd}.wav.ogg')




class HealthBar:
    def __init__(self, pos, width, height, h_color=(205, 22, 22), o_color=(0, 0, 0), o_width=1):
        self.pos = vec(pos)
        self.width = width
        self.init_width = width
        self.height = height
        self.h_color = h_color
        self.o_color = o_color
        self.o_width = o_width

    def damage(self, percent):
        self.width -= ((percent / 100) * self.init_width)
        if self.width > self.init_width:
            self.width = self.init_width
        if self.width < 0:
            self.width = 0

    def update(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(self.pos, (self.init_width, self.height)))
        pygame.draw.rect(surface, self.h_color, pygame.Rect(self.pos, (self.width, self.height)))
        pygame.draw.rect(surface, self.o_color, pygame.Rect(self.pos, (self.init_width, self.height)), self.o_width)


class ImageButton:

    def __init__(self, pos, loaded_image, func):
        self.p = pos
        self.orig_img = loaded_image
        self.image = loaded_image.copy()
        self.rect = loaded_image.get_rect(center=self.p)
        self.clicked = False
        self.func = func

    def blit_button(self, surface, mouse_point):
        if self.rect.collidepoint(mouse_point):
            self.image = pygame.transform.scale(self.image,
                                                (int(self.rect.width * 1.2), int(self.rect.height * 1.2)))
            if pygame.mouse.get_pressed()[0]:
                self.clicked = True
                self.image = self.orig_img
            else:
                if self.clicked:
                    self.func()
                    self.clicked = False
        else:
            self.image = self.orig_img

        rect = self.image.get_rect(center=self.p)
        surface.blit(self.image, rect)


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft=pos)


class Font:
    def __init__(self, font_img):
        self.font_img = pygame.image.load(font_img)
        self.spacing = 1
        self.ordered_characters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
                                   'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                                   'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                                   'z', '.', '-', ',', ':', '+', '\'', '!', '?', '0', '1', '2', '3', '4', '5', '6', '7',
                                   '8', '9', '(', ')', '/', '_', '=', '\\', '[', ']', '*', '"', '<', '>', ';']
        self.font_img_map = {}
        cur_char_width = 0
        char_counter = 0
        for x in range(self.font_img.get_width()):
            c = self.font_img.get_at((x, 0))
            if c[0] == 127:
                img = get_image_from_surface(self.font_img, x - cur_char_width, 0, cur_char_width,
                                             self.font_img.get_height())
                cur_char_width = 0
                self.font_img_map[self.ordered_characters[char_counter]] = img
                char_counter += 1
            else:
                cur_char_width += 1
        self.space_width = self.font_img_map['A'].get_width()
        self.font_height = self.font_img.get_height()

    def render_font(self, surface, text, pos, color):
        x_offset = 0
        y_offset = 0
        for chars in text:
            if chars != ' ' and chars != '\n':
                img = self.font_img_map[chars]
                surface.blit(self.change_color(img, color), (pos[0] + x_offset, pos[1] + y_offset))
                x_offset += img.get_width() + self.spacing
            elif chars == '\n':
                y_offset += self.font_height + 5
                x_offset = 0
            else:
                x_offset += self.space_width

    @staticmethod
    def change_color(img, color):
        surf = pygame.Surface((img.get_width(), img.get_height()))
        surf.blit(img, (0, 0))
        surf.set_colorkey((255, 0, 0))
        surf2 = pygame.Surface(surf.get_size())
        surf2.fill(color)
        surf2.blit(surf, (0, 0))
        surf2.set_colorkey((0, 0, 0))
        return surf2


class QuantumMap:
    def __init__(self, filepath):
        self.filepath = filepath
        self.map_data = self.read_map_data()
        self.image_file = pygame.image.load(self.map_data['image path'])
        self.tile_size = self.map_data["tile_size"]
        self.map_size = self.map_data["map_size"]
        self.image_portions = self.map_data["images"]
        self.objects = self.map_data['objects']
        self.tile_images = self.cut_out_tile_images()
        self.map_img = self.make_map_surface()

    def read_map_data(self):
        with open(self.filepath, 'r') as f:
            return load(f)

    def cut_out_tile_images(self):
        tile_images = {}
        for ID, portion in self.image_portions.items():
            tile_images[ID] = get_image_from_surface(self.image_file, portion[0], portion[1], portion[2], portion[3])

        return tile_images

    def make_map_surface(self):
        surface = pygame.Surface(self.map_size)
        surface.fill('cyan')
        for i in range(1, 5):
            for info in self.map_data[f'layer_{i}']:
                surface.blit(self.tile_images[info[0]], vec(info[1]) * self.tile_size)

        surface.set_colorkey('cyan')
        return surface


class CircleExplosion:
    def __init__(self, pos, color, initial_width, radius_increment=3, lighting_color=None):
        self.radius, self.width, self.pos, self.killed, self.color, self.radius_increment = 10, initial_width, pos, False, color, radius_increment
        self.lighting_color = lighting_color

    def update(self, dt, surface):
        self.radius += self.radius_increment * dt
        self.width -= 0.5 * dt
        if self.width > 1:
            pygame.draw.circle(surface, self.color, self.pos, self.radius, int(self.width))
        else:
            self.killed = True


class JumpParticles:
    def __init__(self, pos, num, colors):
        self.killed = False
        self.particle_list = []
        for i in range(num):
            self.particle_list.append(
                [[pos[0], pos[1]],
                 list(vec(randrange(0, 3), 0).rotate((randint(60, 120)))),
                 randrange(1, 5), choice(colors)])

    def update(self, dt, surface):
        for particle in sorted(self.particle_list, reverse=True):
            if particle[1] == [0, 0]:
                self.particle_list.remove(particle)
            particle[0][0] += particle[1][0] * dt
            particle[0][1] += particle[1][1] * dt
            particle[0][1] += 0.5
            particle[2] -= 0.3 * dt
            pygame.draw.circle(surface, particle[3], particle[0], particle[2])
            if particle[2] <= 0:
                try:
                    self.particle_list.remove(particle)
                except:
                    pass
        if len(self.particle_list) <= 0:
            self.killed = True


class BlastParticles:
    def __init__(self, pos, num, colors, type='all_directions', lighting_color=None):
        self.particle_list = []
        self.killed = False
        self.type = type
        self.lighting_color = lighting_color

        for i in range(num):
            if self.type == 'horizontal':
                rot = choice([0, 360])
            else:
                rot = randrange(-360, 360)
            self.particle_list.append(
                [[randrange(-10, 10) + pos[0], randrange(-10, 10) + pos[1]],
                 list(vec(randrange(-3, 3), 0).rotate(rot)),
                 randrange(1, 7), choice(colors)])

    def update(self, dt, surface):
        for particle in sorted(self.particle_list, reverse=True):
            if particle[1] == [0, 0]:
                self.particle_list.remove(particle)
            particle[0][0] += particle[1][0] * dt
            particle[0][1] += particle[1][1] * dt
            particle[0][1] += 0.5
            particle[2] -= 0.14 * dt
            pygame.draw.circle(surface, particle[3], particle[0], particle[2])
            radius = particle[2] * 2
            if particle[2] <= 0:
                try:
                    self.particle_list.remove(particle)
                except:
                    pass
        if len(self.particle_list) <= 0:
            self.killed = True


class CircleTransition:
    def __init__(self, game):
        self.game = game
        self.center = [self.game.screen.get_width() / 2, self.game.screen.get_height() / 2]
        self.radius = self.game.screen.get_width() / 2 * 2.5
        self.killed = False

    def update(self, dt, surface):
        pygame.draw.circle(surface, (11, 22, 42), self.center, self.radius)
        if self.radius >= self.game.screen.get_width() / 1.5:
            self.game.font.render_font(surface, f'Level {self.game.levels[self.game.level_index]}',
                                       vec(self.center) - vec(20, 3), (106, 190, 48))
            if self.game.level_index == 4:
                self.game.font.render_font(surface, f'Boss Level',
                                           vec(self.center) - vec(26, -15), (222, 50, 48))
        self.radius -= 2.5
        if self.radius < 0:
            self.killed = True


class Player(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        super().__init__()
        self.frames = {'idle': ['idle1', 'idle2', 'idle3'],
                       'run': ['run1', 'run2', 'run3', 'run4'],
                       'jump': ['jump1', 'jump2', 'jump3', 'jump4', 'jump5'],
                       'fall': ['fall']}
        self.frame_duration = {'idle': 230, 'run': 60, 'jump': 150, 'fall': 10}
        self.frame_index = 0
        self.last_update = 0
        self.layer = 5
        self.game = game
        self.state = 'idle'
        self.image = load_img('player/idle/idle1')
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = vec(pos)
        self.velocity = vec(0, 0)
        self.on_ground = False
        self.facing_right = True
        self.can_damage = True
        self.last_alpha = 0
        self.can_fire = True
        self.last_shot = 0
        self.jump_snd = load_snd('jump')
        self.life = 100
        self.health_bar = HealthBar([14, 5], 100, 6, [0, 200, 0])

    def get_state(self):
        if self.velocity.x != 0 and self.on_ground:
            self.state = 'run'
        elif self.velocity.x == 0 and self.on_ground:
            self.state = 'idle'
        elif self.velocity.y < -0.4:
            self.state = 'jump'
        elif self.velocity.y > 1:
            self.state = 'fall'

    def animate(self):
        self.get_state()
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration[self.state]:
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.state])
            self.image = pygame.transform.flip(
                load_img(f'player/{self.state}/{self.frames[self.state][self.frame_index]}'),
                not self.facing_right, False)
            self.last_update = now

    def get_keys(self, dt):
        keys = pygame.key.get_pressed()
        self.velocity.x *= 0.8
        if abs(self.velocity.x) < 0.1:
            self.velocity.x = 0
        self.velocity.y += 0.25 * dt
        x_vel = 1.9
        self.facing_right = True
        if self.game.get_mouse_pos().x < self.rect.centerx:
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = x_vel
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = -x_vel
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.jump_snd.play()
            self.game.particles.append(JumpParticles(self.rect.midbottom, 15, [(100, 100, 100)]))
            self.velocity.y = -5
            self.on_ground = False
        if self.velocity.y > 4:
            self.velocity.y = 4

    def move(self, tiles_group):
        self.pos.x += self.velocity.x
        self.rect.x = int(self.pos.x)
        hits = pygame.sprite.spritecollide(self, tiles_group, False)
        for hit in hits:
            if self.velocity.x > 0:
                self.rect.right = hit.rect.left
            if self.velocity.x < 0:
                self.rect.left = hit.rect.right
            self.pos.x = self.rect.x

        self.pos.y += self.velocity.y
        self.rect.y = int(self.pos.y)
        hits = pygame.sprite.spritecollide(self, tiles_group, False)
        self.on_ground = False
        for hit in hits:
            if self.velocity.y > 0:
                self.rect.bottom = hit.rect.top
                self.velocity.y = 0
                self.on_ground = True
                self.game.gun.sprite.num_recoils = 3
            if self.velocity.y < 0:
                self.rect.top = hit.rect.bottom
                self.velocity.y = 0
            self.pos.y = self.rect.y

    def scroll(self, scroll):
        self.pos.x -= scroll[0]
        self.pos.y -= scroll[1]
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

    def draw(self, surface):
        self.image.blit(surface, self.rect.topleft)

    def update(self, dt):
        self.get_keys(dt)
        self.move(self.game.tiles)
        self.animate()
        if self.life >= 100:
            self.life = 100
        if self.life <= 0:
            self.life = 0
            self.game.game_over = 1


class EnemyBullet:
    def __init__(self, game, vector, pos):
        self.game = game
        try:
            self.vector = vector.normalize()
        except:
            self.vector = vec(0, 0)
        self.pos = vec(pos)
        self.blast_snd = load_snd('blast')
        self.hurt_snd = load_snd('hurt')

    def update(self, dt):
        for tile in self.game.tiles:
            if tile.rect.collidepoint(self.pos):
                self.blast_snd.play()
                self.game.last_shake = pygame.time.get_ticks()
                self.game.particles.append(BlastParticles(self.pos, 100, [(38, 70, 75), (32, 44, 61), (95, 109, 67)]))
                try:
                    self.game.bullets.remove(self)
                except:
                    pass
        if self.game.player.sprite.rect.collidepoint(self.pos):
            self.hurt_snd.play()
            self.game.player.sprite.life -= 5
            self.game.player.sprite.health_bar.damage(5)
            self.game.particles.append(CircleExplosion(self.pos, (106, 190, 48), 10))
            try:
                self.game.bullets.remove(self)
            except:
                pass

        self.pos += self.vector * 5 * dt
        if not (-50 <= self.pos.x <= self.game.screen.get_width() + 50):
            try:
                self.game.bullets.remove(self)
            except:
                pass
        if not (-50 <= self.pos.y <= self.game.screen.get_height() + 50):
            try:
                self.game.bullets.remove(self)
            except:
                pass

    def draw(self, surface):
        pygame.draw.line(surface, (255, 50, 50), self.pos, self.pos + self.vector * 10, 2)


class BulletThrower(pygame.sprite.Sprite):
    def __init__(self, game, pos, range_=[2000, 5000]):
        super().__init__()
        self.game = game
        self.images = [load_img('shooter/shooter1'), load_img('shooter/shooter2')]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=vec(pos) + vec(0, 2))
        self.last_shot = 0
        self.last_animate = 0
        self.range = range_
        self.shot_dur = randint(self.range[0], self.range[1])
        self.life = 100
        self.dead_snd = load_snd('bul_dead')
        self.shoot_snd = load_snd('laser_shoot')
        self.shoot_snd.set_volume(0.5)
        self.health_bar = HealthBar(self.rect.topleft, 20, 4, o_color=(222, 202, 84))

    def draw_health(self, surface):
        if self.life < 100:
            self.health_bar.update(surface)

    def update(self, dt):
        if -20 < self.rect.centerx < self.game.screen.get_width() + 20:
            self.health_bar.pos = self.rect.topleft - vec(3, 7)
            if self.life <= 0:
                self.game.player.sprite.life += 10
                self.game.player.sprite.health_bar.damage(-10)
                self.dead_snd.play()
                self.game.particles.append(CircleExplosion(self.rect.center, (38, 70, 75), 20, 5))
                self.game.particles.append(
                    BlastParticles(self.rect.center, 100, [(38, 70, 75), (32, 44, 61), (95, 109, 67), (70, 70, 70)]))
                self.kill()
            now = pygame.time.get_ticks()
            if now - self.last_animate > 400:
                self.last_animate = now
                self.index = (self.index + 1) % len(self.images)
                self.image = self.images[self.index]

            if now - self.last_shot > self.shot_dur:
                self.shoot_snd.play()
                self.last_shot = now
                self.shot_dur = randint(self.range[0], self.range[1])
                self.game.bullets.append(
                    EnemyBullet(self.game,
                                (vec(self.game.player.sprite.rect.center) - vec(self.rect.center)).rotate(
                                    randint(-10, 10)),
                                vec(self.rect.center) - vec(0, 8)))


class UFO(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        super().__init__()
        self.game = game
        self.pos = vec(pos)
        self.images = [load_img('ufo/ufo1'), load_img('ufo/ufo2')]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(topleft=pos)
        self.last_animate = 0
        self.last_shot = 0
        self.shot_dur = 500
        self.life = 100
        self.dead_snd = load_snd('ufo_dead')
        self.shoot_snd = load_snd('laser_shoot')
        self.shoot_snd.set_volume(0.4)
        self.health_bar = HealthBar(self.rect.topleft, 40, 4, o_color=(222, 202, 84), h_color=(220, 20, 20))

    def draw_health(self, surface):
        if self.life < 100:
            self.health_bar.update(surface)

    def update(self, dt):
        if self.life <= 0:
            self.dead_snd.play()
            self.game.player.sprite.life += 10
            self.game.player.sprite.health_bar.damage(-10)
            self.game.particles.append(CircleExplosion(self.rect.center, (38, 70, 75), 20, 5))
            self.game.particles.append(
                BlastParticles(self.rect.center, 100, [(38, 70, 75), (32, 44, 61), (95, 109, 67), (70, 70, 70)]))
            self.kill()
        self.health_bar.pos = self.rect.topleft - vec(4, 6)
        self.rect.center = self.pos
        if (self.game.player.sprite.pos - self.pos).magnitude_squared() < 40000:
            self.pos.x += (-self.pos.x + self.game.player.sprite.rect.centerx) / 80
            self.rect.center = self.pos
            now = pygame.time.get_ticks()
            for ufo in self.game.ufos:
                if self.rect.colliderect(ufo.rect):
                    if ufo.pos.x > self.pos.x:
                        self.pos.x = ufo.rect.left - self.rect.w / 2 + 5
            if now - self.last_animate > 500:
                self.image = self.images[self.index]
                self.last_animate = now
                self.index = (self.index + 1) % len(self.images)
            if now - self.last_shot > self.shot_dur:
                self.shoot_snd.play()
                self.last_shot = now
                self.shot_dur = randint(2100, 5000)
                self.game.bullets.append(
                    EnemyBullet(self.game,
                                (vec(self.game.player.sprite.rect.center) - vec(self.rect.center)).rotate(
                                    randint(-10, 10)),
                                vec(self.rect.midbottom) - vec(0, 8)))


class BOSS(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        super().__init__()
        self.game = game
        self.pos = vec(pos)
        self.images = [load_img('boss/boss1'), load_img('boss/boss2')]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(topleft=pos)
        self.last_animate = 0
        self.last_shot = 0
        self.shot_dur = 500
        self.life = 100
        self.dead_snd = load_snd('ufo_dead')
        self.health_bar = HealthBar(self.rect.topleft, 80, 4, o_color=(84, 202, 84), h_color=(220, 20, 20))
        self.beep_snd = load_snd('beep')
        self.beep_snd.set_volume(0.3)
        self.can_beep = True
        self.boss_played = False

    def draw_health(self, surface):
        if self.life < 100:
            self.health_bar.update(surface)

    def update(self, dt):
        if len(self.game.ufos) == 1 and not len(self.game.bullet_thrower):
            if (self.game.player.sprite.pos - self.game.ufos.sprites()[0].pos).length() < 100:
                if not self.boss_played:
                    self.boss_played = True
                    pygame.mixer.music.load('data/sfx/boss.mp3.ogg')
                    pygame.mixer.music.set_volume(1.0)
                    pygame.mixer.music.play(-1)
        if len(self.game.ufos) == 1 and not len(self.game.bullet_thrower):
            if self.life <= 0:
                self.dead_snd.play()
                self.game.particles.append(CircleExplosion(self.rect.center, (38, 70, 75), 30, 5))
                self.game.particles.append(
                    BlastParticles(self.rect.center, 500,
                                   [(38, 70, 75), (32, 44, 61), (95, 109, 67), (70, 70, 70), (180, 0, 0)]))
                self.kill()
            self.health_bar.pos = self.rect.topleft - vec(4, 6)
            self.rect.center = self.pos
            if (self.game.player.sprite.pos - self.pos).magnitude_squared() < 40000:
                self.pos.x += (-self.pos.x + self.game.player.sprite.rect.centerx) / 100
                self.rect.center = self.pos
                now = pygame.time.get_ticks()
                for ufo in self.game.ufos:
                    if self.rect.colliderect(ufo.rect):
                        if ufo.pos.x > self.pos.x:
                            self.pos.x = ufo.rect.left - self.rect.w / 2 + 5
                if now - self.last_animate > 500:
                    self.can_beep = not self.can_beep
                    if self.can_beep:
                        self.beep_snd.play()
                    self.image = self.images[self.index]
                    self.last_animate = now
                    self.index = (self.index + 1) % len(self.images)
                if now - self.last_shot > self.shot_dur:
                    self.last_shot = now
                    self.shot_dur = randint(1100, 4000)
                    self.game.bullets.append(
                        EnemyBullet(self.game,
                                    (vec(self.game.player.sprite.rect.center) - vec(self.rect.center)),
                                    vec(self.rect.midbottom) - vec(0, 8)))
                    self.game.bullets.append(
                        EnemyBullet(self.game,
                                    (vec(self.game.player.sprite.rect.center) - vec(self.rect.center)),
                                    vec(self.rect.midbottom) - vec(15, 3)))
                    self.game.bullets.append(
                        EnemyBullet(self.game,
                                    (vec(self.game.player.sprite.rect.center) - vec(self.rect.midbottom) + vec(15, -3)),
                                    vec(self.rect.midbottom) + vec(15, -3)))


class Bullet:
    def __init__(self, game, vector, pos):
        self.game = game
        try:
            self.vector = vector.normalize()
        except:
            self.vector = vec(0, 0)
        self.pos = vec(pos)
        self.blast_snd = load_snd('blast')
        self.bul_throw_hit_snd = load_snd('bul_thro_hit')

    def update(self, dt):
        for ufo in self.game.ufos.sprites():
            if ufo.rect.collidepoint(self.pos):
                if isinstance(ufo, BOSS):
                    ufo.health_bar.damage(1)
                    ufo.life -= 1
                else:
                    ufo.pos.x += (self.pos.x - self.game.player.sprite.pos.x) / abs(
                        (self.pos.x - self.game.player.sprite.pos.x)) * 5
                    ufo.health_bar.damage(15)
                    ufo.life -= 15
                self.bul_throw_hit_snd.play()
                self.game.last_shake = pygame.time.get_ticks()
                self.game.particles.append(CircleExplosion(self.pos, (38, 70, 75), 5, 1))
                self.game.particles.append(
                    BlastParticles(self.pos, 20, [(38, 70, 75), (32, 44, 61), (95, 109, 67), (222, 202, 84)]))
                try:
                    self.game.bullets.remove(self)
                except:
                    pass
        for bul_thrower in self.game.bullet_thrower.sprites():
            if bul_thrower.rect.collidepoint(self.pos):
                bul_thrower.health_bar.damage(10)
                bul_thrower.life -= 10
                self.bul_throw_hit_snd.play()
                self.game.last_shake = pygame.time.get_ticks()
                self.game.particles.append(BlastParticles(self.pos, 40,
                                                          [(38, 70, 75), (32, 44, 61), (95, 109, 67), (200, 0, 0),
                                                           (0, 200, 200)]))
                try:
                    self.game.bullets.remove(self)
                except:
                    pass
        for tile in self.game.tiles:
            if tile.rect.collidepoint(self.pos):
                self.blast_snd.play()
                self.game.last_shake = pygame.time.get_ticks()
                self.game.particles.append(BlastParticles(self.pos, 100, [(38, 70, 75), (32, 44, 61), (95, 109, 67)]))
                try:
                    self.game.bullets.remove(self)
                except:
                    pass
        self.pos += self.vector * 8 * dt
        if not (-50 <= self.pos.x <= self.game.screen.get_width() + 50):
            try:
                self.game.bullets.remove(self)
            except:
                pass
        if not (-50 <= self.pos.y <= self.game.screen.get_height() + 50):
            try:
                self.game.bullets.remove(self)
            except:
                pass

    def draw(self, surface):
        pygame.draw.line(surface, (50, 255, 50), self.pos, self.pos + self.vector * 10, 2)


class Gun(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = load_img('gun/gun')
        self.base_img = load_img('gun/gun')
        self.rect = self.image.get_rect(center=self.game.player.sprite.rect.center)
        self.angle = 0
        self.layer = 8
        self.fire_snd = load_snd('fire')
        self.num_recoils = 3

    def fire(self):
        self.fire_snd.play()
        if self.num_recoils:
            self.num_recoils -= 1
            self.game.player.sprite.velocity = (vec(self.game.get_mouse_pos()) - vec(self.rect.center)).normalize() * -2
        self.game.bullets.append(
            Bullet(self.game, (vec(self.game.get_mouse_pos()) - vec(self.rect.center)),
                   self.game.player.sprite.rect.center))

    def update(self, dt):
        player = self.game.player.sprite
        self.rect.center = player.rect.center
        self.angle = (vec(self.game.get_mouse_pos()) - vec(self.rect.center)).angle_to(vec(1, 0))
        if self.angle < 0:
            self.angle = self.angle + 360
        self.image = pygame.transform.rotate(self.base_img, self.angle)
        if 90 <= self.angle <= 270:
            self.image = pygame.transform.rotate(self.base_img, -self.angle)
            self.image = pygame.transform.flip(self.image, False, True)
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center


class Portal(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        super().__init__()
        self.game = game
        self.images = [load_img('portal/portal1'), load_img('portal/portal2')]
        self.index = 0
        self.last_anim = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, dt):
        now = pygame.time.get_ticks()
        if now - self.last_anim > 500:
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]
            self.last_anim = now

        if self.game.player.sprite.rect.colliderect(self.rect):
            if not len(self.game.ufos) and not len(self.game.bullet_thrower):
                if self.game.level_index<6:
                    self.game.particles.append(CircleTransition(self.game))
                    self.game.level_index += 1
                    self.game.new_game()
                else:
                    self.game.show_go = 1
            else:
                self.game.eligible = False


class Base:
    pygame.mixer.pre_init(44100, -16, 40, 512)
    pygame.init()
    pygame.mixer.init()
    Clock = pygame.time.Clock()
    display = state_fullscreen()
    screen = pygame.Surface((300, round(300 / AR)))

    pygame.display.set_caption('Alien Dimension')

    player_logo = load_img('player_logo')
    pygame.display.set_icon(player_logo)

    font = Font('data/font/large_font.png')
    small_font = Font('data/font/small_font.png')
    gradient_img = pygame.transform.scale(load_img('light').convert_alpha(), [100, 100])



class Game(Base):
    instruct_img = load_img('button/instructions')
    levels = ['1', '2', '3', '4', '5']

    def __init__(self):
        self.menu = True
        self.paused = False
        self.shake = False
        self.last_shake = 0
        self.full_screen = False

        self.level_index = 0
        self.main_menu_ = 0
        self.show_go = False
        self.game_over = False
        self.eligible = True
        self.instructions = True
        self.bg_rects = []
        self.main_menu_playing = False

        self.gradient_img.fill((55, 50, 0), special_flags=pygame.BLEND_RGBA_MULT)


    def show_instructions(self):
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.instructions = 0

                if event.key == pygame.K_ESCAPE:
                    self.instructions = 0
                    States.select("Menu_main")

                if event.key == pygame.K_f:
                    self.full_screen = not self.full_screen
                    States.select("fullscreen")
            elif event.type == pygame.QUIT:
                States.select("exit")


        self.screen.blit(self.instruct_img, [0, 0])
        self.display.blit(pygame.transform.scale(self.screen, self.display.get_size()), [0, 0])




    def screen_shake(self):
        self.shake = True
        now = pygame.time.get_ticks()
        if now - self.last_shake > 150:
            self.shake = False

    def scroll(self):
        self.screen_shake()
        scroll = [0, 0]
        if self.shake:
            scroll = [randint(-2, 2), randint(-2, 2)]
        scroll[0] += (self.player.sprite.rect.centerx - scroll[0] - self.screen.get_width() / 2) / 20
        scroll[1] += (self.player.sprite.rect.centery - scroll[1] - self.screen.get_height() / 2) / 20
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])
        for sprites in self.all_sprites:
            if isinstance(sprites, Player):
                sprites.scroll(scroll)
            elif isinstance(sprites, UFO):
                sprites.pos -= scroll
            elif isinstance(sprites, BOSS):
                sprites.pos -= scroll
            else:
                sprites.rect.center -= vec(scroll)
        for sprites in self.tiles:
            sprites.rect.center -= vec(scroll)
        for sprites in self.bullets:
            sprites.pos -= vec(scroll)
        for rect in self.bg_rects:
            rect[1][0] -= vec(scroll) * rect[0]
        self.map_pos -= vec(scroll)
        self.map_rect.topleft = self.map_pos
        for light in self.lights:
            light -= vec(scroll)

    def new_game(self):
        self.eligible = True
        if self.main_menu_playing:
            pygame.mixer.music.unload()
            pygame.mixer.music.fadeout(1000)
            self.main_menu_playing = False
            pygame.mixer.music.load('data/sfx/music.mp3.ogg')
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        new_map = QuantumMap(f'data/level/{self.levels[self.level_index]}.json')
        self.map_img = new_map.map_img
        self.map_pos = vec(0, 0)
        self.map_rect = self.map_img.get_rect()
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.player = pygame.sprite.GroupSingle()
        self.bullet_thrower = pygame.sprite.Group()
        self.ufos = pygame.sprite.Group()
        self.gun = pygame.sprite.GroupSingle()
        self.tiles = pygame.sprite.Group()
        self.bullets = []
        self.particles = []
        self.lights = []
        self.target_img = load_img('target')
        self.trans = []
        self.trans.append(CircleTransition(self))
        pygame.mouse.set_visible(0)
        self.bg_rects.clear()
        factor = 0.25
        for i in range(3):
            for _ in range(int(self.map_rect.w / 80)):
                self.bg_rects.append([factor,
                                      [vec(randint(0, self.map_rect.w), randint(50, 150)), vec(randint(20, 50), 300)]])
            factor += 0.25
        for object in new_map.objects:
            position = [object[1][0] * TILE_SIZE, object[1][1] * TILE_SIZE]
            if object[0] == 'rects':
                tile = Tile(position, object[1][2] * TILE_SIZE, object[1][3] * TILE_SIZE)
                self.tiles.add(tile)
            elif object[0] == 'player':
                P = Player(self, position)
                self.all_sprites.add(P)
                self.player.add(P)
            elif object[0] == 'bul':
                b = BulletThrower(self, position)
                self.all_sprites.add(b)
                self.bullet_thrower.add(b)
            elif object[0] == 'ufo':
                u = UFO(self, position)
                self.all_sprites.add(u)
                self.ufos.add(u)
            elif object[0] == 'boss':
                B = BOSS(self, position)
                self.all_sprites.add(B)
                self.ufos.add(B)
            elif object[0] == 'port':
                p = Portal(self, position)
                self.all_sprites.add(p)
        gun = Gun(self)
        self.all_sprites.add(gun)
        self.gun.add(gun)
        for image in new_map.map_data['layer_3']:
            if image[0] == '10' or image[0] == '9':
                self.lights.append(vec(image[1]) * TILE_SIZE - vec(self.gradient_img.get_size()) / 2 + vec(7, 9))

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.gun.sprite.fire()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.sprite.velocity.y *= 0.5
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    States.select("Menu_main")
                if event.key == pygame.K_SPACE:
                    pass
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if event.key == pygame.K_m:
                    pass
                if event.key == pygame.K_f:
                    state_fullscreen(1)
            elif event.type == pygame.QUIT:
                States.select("exit")


    def draw(self):

        if self.instructions:
            self.show_instructions()

        elif self.show_go:
            self.show_go_screen()

        elif States.changed("Pause",):
            print("NEW GAME")
            self.new_game()
        else:
            self.draw_game()


    def draw_game(self):
        global FPS


        self.dt = self.Clock.tick(FPS) / 1000 * 60

        self.events()


        self.screen.fill((125, 18, 67))
        pygame.draw.rect(self.screen, (80, 0, 30), pygame.Rect(0, 100, self.screen.get_width(), 100))
        for rect in self.bg_rects:
            color = (85, 0, 35) if rect[0] == 0.75 else (99, 5, 47)
            if rect[0] == 0.25:
                color = (110, 16, 54)
            pygame.draw.rect(self.screen, color, pygame.Rect(rect[1][0], rect[1][1]))
        self.screen.blit(self.map_img, self.map_rect)
        self.all_sprites.draw(self.screen)
        for bul_throwers in self.bullet_thrower.sprites():
            bul_throwers.draw_health(self.screen)
        for ufo in self.ufos.sprites():
            ufo.draw_health(self.screen)
        for bul in self.bullets:
            bul.draw(self.screen)
        for particle in self.particles:
            particle.update(self.dt, self.screen)
            if particle.killed:
                self.particles.remove(particle)
        for light in self.lights:
            self.screen.blit(self.gradient_img, light, special_flags=pygame.BLEND_RGB_ADD)
        self.player.sprite.health_bar.update(self.screen)
        self.screen.blit(self.player_logo, [4, 3])
        if not self.eligible:
            self.small_font.render_font(self.screen, 'Destroy all Enemies', [130, 130], [222, 202, 84])
        if len(self.ufos) + len(self.bullet_thrower):
            self.small_font.render_font(self.screen, f'Enemies Left {len(self.ufos) + len(self.bullet_thrower)}',
                                        [240, 3], [222, 202, 84])
        else:
            self.small_font.render_font(self.screen, f'Enemies Left {len(self.ufos) + len(self.bullet_thrower)}',
                                        [240, 3], [108, 230, 48])
        self.screen.blit(self.target_img, self.get_mouse_pos() - vec(self.target_img.get_size()) / 2)
        self.eligible = True
        for tran in self.trans:
            tran.update(self.dt, self.screen)
            if tran.killed:
                try:
                    self.trans.remove(tran)
                except:
                    pass
        self.display.blit(pygame.transform.scale(self.screen, self.display.get_size()), (0, 0))


        self.scroll()
        self.all_sprites.update(self.dt)
        for bul in self.bullets:
            bul.update(self.dt)


    def game_over_screen(self):
        if States.changed():
            pygame.mixer.music.fadeout(2000)
            pygame.mouse.set_visible(0)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                States.select("exit")

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_over = 0
                    States.select("Menu_main")
                if event.key == pygame.K_RETURN:
                    self.game_over = 0
                    States.select("float")
                    States.select("Game")

                if event.key == pygame.K_f:
                    States.select("fullscreen")
        self.font.render_font(self.screen, 'PRESS', [130, 30], [38, 70, 75])
        self.font.render_font(self.screen, 'ESCAPE for Menu', [100, 70], [190, 50, 50])
        self.font.render_font(self.screen, 'ENTER for Replay', [100, 100], [106, 190, 48])
        self.display.blit(pygame.transform.scale(self.screen, self.display.get_size()), [0, 0])


    def show_go_screen(self):
        self.level_index = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                States.select("exit")

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    States.select("exit")
                if event.key == pygame.K_RETURN:
                    self.show_go = 0
                    States.select("Menu_main")
                if event.key == pygame.K_f:
                    States.select("fullscreen")
        self.font.render_font(self.screen, 'THE END', [125, 50], (106, 190, 48))
        self.small_font.render_font(self.screen, 'Press enter to go back to main menu', [82, 100], (106, 190, 48))
        self.display.blit(pygame.transform.scale(self.screen, self.display.get_size()), [0, 0])


    def get_mouse_pos(self):
        return vec(pygame.mouse.get_pos()) / (self.display.get_width() / self.screen.get_width())


    def back_more(self):
        self.more_ = False
        self.main_menu()



game = Game()


class Menu(Base):
    mouse = load_img('mouse')

    def draw(self):
        print(f"menu {self.__class__.__name__} n/i")
        States.previous()


class Menu_more_games(Menu):
    def draw(self):
        if States.changed():
            state_fullscreen(-1)
            from webbrowser import open
            print("Begin navigation")
            open('https://quantum-hg.itch.io/')
            print("End navigation")
            States.select("Menu_main")



class Menu_more(Menu):

    credit_img = load_img('button/credits')
    bg = load_img('main_menu_bg')
    bg.set_alpha(120)
    back = ImageButton([300, 600], load_img('button/back'), States("Menu_main") )
    more_games = ImageButton([900, 600], load_img('button/more games'), States("Menu_more_games"))


    def draw(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                States.select("exit")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    States.select("exit")
        self.display.blit(self.bg, [0, 0])
        self.display.blit(self.credit_img, [0, 40])
        self.back.blit_button(self.display, pygame.mouse.get_pos())
        self.more_games.blit_button(self.display, pygame.mouse.get_pos())
        self.display.blit(self.mouse, pygame.mouse.get_pos())



class Menu_main(Menu):

    bg = load_img('main_menu_bg')

    def __init__(self):

        pygame.mouse.set_visible(0)
        self.main_menu_playing = False
        self.play = ImageButton([930, 400], load_img('button/play'), States("Game"))
        self.more = ImageButton([930, 500], load_img('button/more'), States("Menu_more"))
        self.exit_but = ImageButton([930, 600], load_img('button/exit'), States("exit") )

    def draw(self):

        if not self.main_menu_playing:
            pygame.mixer.music.load('data/sfx/menu.mp3.ogg')
            pygame.mixer.music.play(-1)
            self.main_menu_playing = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                States.select("exit")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    States.select("exit")

        self.display.blit(self.bg, [0, 0])
        self.play.blit_button(self.display, pygame.mouse.get_pos())
        self.exit_but.blit_button(self.display, pygame.mouse.get_pos())
        self.more.blit_button(self.display, pygame.mouse.get_pos())
        self.display.blit(self.mouse, pygame.mouse.get_pos())


async def main():
    while States.draw():
        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit(0)


States.select("Menu_main")

if __name__ == "__main__":
    asyncio.run(main())


































#
