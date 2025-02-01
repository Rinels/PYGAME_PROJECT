import pygame
import sys

# Константы
WIDTH = 800  # Ширина экрана
HEIGHT = 600  # Высота экрана
LEVEL_WIDTH = WIDTH * 3  # Ширина уровня (в 3 раза больше экрана)
FPS = 60

GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_STRENGTH = -15

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Супер Малыш Хорек")
clock = pygame.time.Clock()


class BabyFerret(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 4, HEIGHT - 100)  # Начальная позиция
        self.velocity_y = 0
        self.is_jumping = False

    def update(self, keys, platforms):
        # Движение влево и вправо
        if keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED

        # Гравитация
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Коллизия с платформами
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.velocity_y > 0:
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False

        # Прыжок
        if keys[pygame.K_w] and not self.is_jumping:
            self.velocity_y = JUMP_STRENGTH
            self.is_jumping = True

        # Ограничение движения по краям уровня
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.is_jumping = False


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class FirstLevel:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()

        self.Ferret = BabyFerret()
        self.all_sprites.add(self.Ferret)

        # Создание платформ
        level_layout = [
            # Стартовая зона
            (0, HEIGHT - 20, LEVEL_WIDTH, 20),  # Земля
            (200, 500, 150, 20),
            (400, 400, 150, 20),
            (600, 300, 150, 20),

            # Зона с препятствиями
            (800, 500, 150, 20),
            (1000, 400, 150, 20),
            (1200, 300, 150, 20),

            # Финал
            (1400, 200, 150, 20),
            (1600, 100, 150, 20),
        ]

        for x, y, width, height in level_layout:
            platform = Platform(x, y, width, height)
            self.platforms.add(platform)
            self.all_sprites.add(platform)

    def run(self):
        running = True
        camera_x = 0  # Смещение камеры

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            # Обновление спрайтов
            self.Ferret.update(keys, self.platforms)

            # Камера следует за игроком
            if self.Ferret.rect.x > WIDTH * 0.6:
                camera_x = self.Ferret.rect.x - WIDTH * 0.6

            # Отрисовка
            screen.fill(CYAN)
            for sprite in self.all_sprites:
                screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))
            pygame.display.flip()
            clock.tick(FPS)

    def start_screen(self):
        screen.fill(BLUE)
        font = pygame.font.Font(None, 74)
        text = font.render("Супер Малыш Хорек", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

        font = pygame.font.Font(None, 36)
        text = font.render("Нажмите любую клавишу, чтобы начать (Управление: WASD)", True, WHITE)
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
    level = FirstLevel()
    level.start_screen()
    level.run()
    pygame.quit()
    sys.exit()