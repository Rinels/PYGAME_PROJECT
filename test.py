import pygame
from pytmx.util_pygame import load_pygame
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

class BabyFerret(pygame.sprite.Sprite):
    def __init__(self, x, y, tmx_data):
        super().__init__()
        self.image = pygame.image.load("BabyFerret.png")
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocity_y = 0  # Начальная вертикальная скорость
        self.is_jumping = False
        self.tmx_data = tmx_data  # Передаем tmx_data в объект

    def update(self, keys, platforms, blocked_tiles):
        # Движение влево и вправо
        if keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
            # Отражение спрайта при движении влево
            self.image = pygame.transform.flip(pygame.image.load("BabyFerret.png"), True, False)
            self.image = pygame.transform.scale(self.image, (32, 32))
            # Проверка коллизий с непроходимыми тайлами
            for tile in blocked_tiles:
                if self.rect.colliderect(tile):
                    self.rect.left = tile.right  # Останавливаем движение влево
                    break

        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
            # Отображение спрайта в нормальном положении при движении вправо
            self.image = pygame.transform.flip(pygame.image.load("BabyFerret.png"), False, False)
            self.image = pygame.transform.scale(self.image, (32, 32))
            # Проверка коллизий с непроходимыми тайлами
            for tile in blocked_tiles:
                if self.rect.colliderect(tile):
                    self.rect.right = tile.left  # Останавливаем движение вправо
                    break

        # Гравитация
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Проверка коллизий с платформами и непроходимыми тайлами
        self.is_jumping = True
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_y > 0:  # Падение вниз
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.is_jumping = False

        # Проверка коллизий с непроходимыми тайлами по вертикали
        for tile in blocked_tiles:
            if self.rect.colliderect(tile):
                if self.velocity_y > 0:  # Падение вниз
                    self.rect.bottom = tile.top
                    self.velocity_y = 0
                    self.is_jumping = False
                elif self.velocity_y < 0:  # Прыжок вверх
                    self.rect.top = tile.bottom
                    self.velocity_y = 0

        # Прыжок
        if keys[pygame.K_w] and not self.is_jumping:
            self.velocity_y = JUMP_STRENGTH
            self.is_jumping = True

        # Ограничение выхода за границы карты по горизонтали
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.tmx_data.width * self.tmx_data.tilewidth:
            self.rect.right = self.tmx_data.width * self.tmx_data.tilewidth

        # Падение за нижнюю границу карты
        if self.rect.top > self.tmx_data.height * self.tmx_data.tileheight:
            self.reset_position()  # Возвращаем игрока на стартовую позицию

    def reset_position(self):
        """Сбрасывает позицию игрока на стартовую точку."""
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
        self.blocked_tiles = []  # Список для непроходимых тайлов

        # Загрузка карты из TMX файла
        self.tmx_data = load_pygame(map_file)
        self.camera_x = 0
        self.camera_y = 0

        # Создаем игрока из стартовой точки
        self.Ferret = None
        for obj in self.tmx_data.objects:
            if obj.name == "Player":
                self.Ferret = BabyFerret(obj.x, obj.y, self.tmx_data)  # Передаем tmx_data
                self.all_sprites.add(self.Ferret)
                break
        else:
            print("Ошибка: объект 'Player' не найден в TMX-файле.")
            sys.exit()

        # Загружаем платформы и непроходимые тайлы из карты
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        tile_rect = pygame.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight,
                                                self.tmx_data.tilewidth, self.tmx_data.tileheight)
                        if gid == 1116:  # Если тайл имеет номер 1116
                            self.blocked_tiles.append(tile_rect)  # Добавляем в список непроходимых тайлов
                        else:
                            self.platforms.append(tile_rect)  # Остальные тайлы добавляем как платформы

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            # Обновление спрайтов
            self.Ferret.update(keys, self.platforms, self.blocked_tiles)


            self.camera_x = max(0, min(self.camera_x, self.tmx_data.width * self.tmx_data.tilewidth - WIDTH))
            self.camera_y = max(0, min(self.camera_y, self.tmx_data.height * self.tmx_data.tileheight - HEIGHT))
            screen.fill(CYAN)
            self.render_map()
            self.all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

    def render_map(self):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):  # Для тайловых слоев
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * self.tmx_data.tilewidth - self.camera_x,
                                           y * self.tmx_data.tileheight - self.camera_y))
            elif hasattr(layer, 'objects'):  # Для объектных слоев
                for obj in layer:
                    if obj.image:
                        screen.blit(obj.image, (obj.x - self.camera_x, obj.y - self.camera_y))

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
    level = FirstLevel("FirstLevel.tmx")  # Укажите путь к карте
    level.start_screen()
    level.run()
    pygame.quit()
    sys.exit()