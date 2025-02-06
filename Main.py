import pygame
import pytmx
import sys

# Константы
WIDTH = 1000  # Ширина экрана
HEIGHT = 700  # Высота экрана
FPS = 60

GRAVITY = 0.8
PLAYER_SPEED = 4  # Уменьшено на 20% (было 5)
JUMP_STRENGTH = -15

WHITE = (255, 255, 255)
CYAN = (0, 255, 255)

# Инициализация Pygame
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
        """
        Возвращает новое положение спрайта с учетом смещения камеры.
        """
        return target_rect.move(-self.camera_rect.x, -self.camera_rect.y)

    def update(self, target):
        """
        Центрирует камеру на цели (персонаже), ограничивая ее границами карты.
        """
        x = target.rect.centerx - WIDTH // 2
        y = target.rect.centery - HEIGHT // 2

        # Ограничиваем камеру границами карты
        x = max(0, min(x, self.width - WIDTH))
        y = max(0, min(y, self.height - HEIGHT))

        self.camera_rect = pygame.Rect(x, y, WIDTH, HEIGHT)

class BabyFerret(pygame.sprite.Sprite):
    def __init__(self, x, y, tmx_data):
        super().__init__()
        self.image = pygame.image.load("BabyFerret.png")
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
            self.image = pygame.transform.flip(pygame.image.load("BabyFerret.png"), True, False)
            self.image = pygame.transform.scale(self.image, (32, 32))
            for tile in blocked_tiles:
                if self.rect.colliderect(tile):
                    self.rect.left = tile.right
                    break

        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
            self.image = pygame.transform.flip(pygame.image.load("BabyFerret.png"), False, False)
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

            screen.fill(CYAN)
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

    def start_screen(self):
        screen.fill(WHITE)
        font = pygame.font.Font(None, 74)
        text = font.render("Супер Малыш Хорек", True, (0, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

        font = pygame.font.Font(None, 36)
        text = font.render("Нажмите любую клавишу, чтобы начать (Управление: WASD)", True, (0, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False

if __name__ == "__main__":
    level = FirstLevel("FirstLevel.tmx")
    level.start_screen()
    level.run()
    pygame.quit()
    sys.exit()