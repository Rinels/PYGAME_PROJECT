import pygame
import pytmx
import sys
import random
import time
import sqlite3

WIDTH = 1000
HEIGHT = 700
FPS = 60
GRAVITY = 0.8
PLAYER_SPEED = 4
JUMP_STRENGTH = -15
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Супер Малыш Хорек")
clock = pygame.time.Clock()


class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, target_rect):
        return target_rect.move(-self.camera_rect.x, -self.camera_rect.y)

    def update(self, target):
        x = target.rect.centerx - WIDTH // 2
        y = target.rect.centery - HEIGHT // 2

        x = max(0, min(x, self.width - WIDTH))
        y = max(0, min(y, self.height - HEIGHT))

        self.camera_rect = pygame.Rect(x, y, WIDTH, HEIGHT)


class BabyFerret(pygame.sprite.Sprite):
    def __init__(self, x, y, tmx_data):
        super().__init__()
        self.image = pygame.image.load("Ferret.png")
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocity_y = 0  # Начальная вертикальная скорость
        self.is_jumping = False
        self.tmx_data = tmx_data

    def update(self, keys, platforms, blocked_tiles):
        # Движение влево и вправо
        if keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
            self.image = pygame.transform.flip(pygame.image.load("Ferret.png"), True, False)
            self.image = pygame.transform.scale(self.image, (32, 32))
            for tile in blocked_tiles:
                if self.rect.colliderect(tile):
                    self.rect.left = tile.right
                    break

        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
            self.image = pygame.transform.flip(pygame.image.load("Ferret.png"), False, False)
            self.image = pygame.transform.scale(self.image, (32, 32))
            for tile in blocked_tiles:
                if self.rect.colliderect(tile):
                    self.rect.right = tile.left
                    break

        # Гравитация
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        self.is_jumping = True
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.is_jumping = False

        for tile in blocked_tiles:
            if self.rect.colliderect(tile):
                if self.velocity_y > 0:
                    self.rect.bottom = tile.top
                    self.velocity_y = 0
                    self.is_jumping = False
                elif self.velocity_y < 0:
                    self.rect.top = tile.bottom
                    self.velocity_y = 0

        if keys[pygame.K_w] and not self.is_jumping:
            self.velocity_y = JUMP_STRENGTH
            self.is_jumping = True

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.tmx_data.width * self.tmx_data.tilewidth:
            self.rect.right = self.tmx_data.width * self.tmx_data.tilewidth

        if self.rect.top > self.tmx_data.height * self.tmx_data.tileheight:
            self.reset_position()

    def reset_position(self):
        for obj in self.tmx_data.objects:
            if obj.name == "Player":
                self.rect.topleft = (obj.x, obj.y)
                self.velocity_y = 0
                self.is_jumping = False
                break


class Enemy:
    def __init__(self, x, y, tmx_data):
        super().__init__()
        self.image = pygame.image.load("Enemy.png")
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocity_y = 0  # Начальная вертикальная скорость
        self.tmx_data = tmx_data


class FirstLevel:
    def __init__(self, map_file):
        self.all_sprites = pygame.sprite.Group()
        self.platforms = []
        self.blocked_tiles = []

        self.tmx_data = pytmx.load_pygame(map_file)

        self.Ferret = None
        for obj in self.tmx_data.objects:
            if obj.name == "Player":
                self.Ferret = BabyFerret(obj.x, obj.y, self.tmx_data)
                self.all_sprites.add(self.Ferret)
                break

        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        tile_rect = pygame.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight,
                                                self.tmx_data.tilewidth, self.tmx_data.tileheight)
                        if gid == 1116:
                            self.blocked_tiles.append(tile_rect)
                        else:
                            self.platforms.append(tile_rect)

        self.camera = Camera(self.tmx_data.width * self.tmx_data.tilewidth,
                              self.tmx_data.height * self.tmx_data.tileheight)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            self.Ferret.update(keys, self.platforms, self.blocked_tiles)
            self.camera.update(self.Ferret)

            screen.fill("CYAN")

            self.render_map()
            for sprite in self.all_sprites:
                screen.blit(sprite.image, self.camera.apply(sprite.rect))

            pygame.display.flip()
            clock.tick(FPS)

    def render_map(self):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * self.tmx_data.tilewidth - self.camera.camera_rect.x,
                                           y * self.tmx_data.tileheight - self.camera.camera_rect.y))


class SecondLevel:
    def __init__(self, map_file):
        self.all_sprites = pygame.sprite.Group()
        self.platforms = []
        self.blocked_tiles = []

        self.tmx_data = pytmx.load_pygame(map_file)

        self.Ferret = None
        for obj in self.tmx_data.objects:
            if obj.name == "Player":
                self.Ferret = BabyFerret(obj.x, obj.y, self.tmx_data)
                self.all_sprites.add(self.Ferret)
                break


class Button:
    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.text_surf = self.font.render(text, True, BLACK)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, (self.rect.centerx - self.text_surf.get_width() // 2,
                                     self.rect.centery - self.text_surf.get_height() // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def start_screen():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render("Супер Малыш Хорек", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))

    start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, "Начать игру")
    exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, "Выход")

    buttons = [start_button, exit_button]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons:
                        if button.is_clicked(event.pos):
                            if button.text == "Начать игру":
                                download_screen = DownloadScreen()
                                download_screen.loading_screen()
                                return
                            elif button.text == "Выход":
                                pygame.quit()
                                sys.exit()

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

class DownloadScreen:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.offers = [
            'А вы знаете, что очень трудно найти спрайт хорька?',
            'Warning: хорек обнаружил неинициализированную переменную. Он ее унес.',
            'Мы подозреваем, что это не ошибка, а хорьки устроили вечеринку в коде.',
            'Факт: хорьки используют рекурсию, чтобы прятать носки в бесконечном цикле.',
            'Ошибка 404: хорек не найден. Он ушел в отладку.',
            'Если хорек завис — это не баг, он просто размышляет о смысле жизни.',
            'Кажется, хорьки вырыли нору в текстурах. Мы копаем следом.',
            'Ошибка: хорек украл часть уровня. Сейчас вернем.',
            'Если враг не двигается, хорьки говорят, что это "режим стелса".',
            'Хорьки утверждают, что багов нет — это новые механики.',
            'Ваш хорек застрял в текстурах? Это его зона комфорта.',
            'Секретный факт: хорьки заменяют баги своей харизмой.',
            'Баг или фича? Хорьки молчат, как шпионы.',
            'Ошибка: хорьки решили, что музыка в игре лишняя.',
            'Если игра вылетела, это потому что хорьки решили устроить перерыв.'
        ]
        self.loading_text = "Загрузка уровня"
        self.additional_text = random.choice(self.offers)

        # Анимация точек
        self.dots = ["", ".", "..", "..."]
        self.current_dot_index = 0
        self.last_update = pygame.time.get_ticks()
        self.dot_animation_speed = 500

    def draw_loading_screen(self):
        self.screen.fill(WHITE)
        loading_surface = self.font.render(self.loading_text + self.dots[self.current_dot_index], True, BLACK)
        self.screen.blit(loading_surface, (WIDTH // 2 - loading_surface.get_width() // 2, HEIGHT // 2 - 50))

        additional_surface = self.small_font.render(self.additional_text, True, BLACK)
        self.screen.blit(additional_surface, (WIDTH // 2 - additional_surface.get_width() // 2, HEIGHT // 2 + 50))
        pygame.display.flip()

    def loading_screen(self):
        duration = 5
        start_time = time.time()
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            now = pygame.time.get_ticks()
            if now - self.last_update > self.dot_animation_speed:
                self.current_dot_index = (self.current_dot_index + 1) % len(self.dots)
                self.last_update = now

            self.draw_loading_screen()
            self.clock.tick(FPS)


if __name__ == "__main__":
    #download_screen = DownloadScreen()
    #download_screen.loading_screen()
    level = FirstLevel("FirstLevel.tmx")
    #level = SecondLevel("SecondLevel.tmx")
    start_screen()
    level.run()
    pygame.quit()
    sys.exit()