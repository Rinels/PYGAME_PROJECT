import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enemy Example")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Класс игрока
class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = SCREEN_WIDTH // 1.5
        self.y = SCREEN_HEIGHT - self.height - 50
        self.vel_y = 0
        self.jump_power = -25
        self.gravity = 1
        self.is_jumping = False

    def draw(self):
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height))

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.vel_y = self.jump_power

    def update(self):
        self.vel_y += self.gravity
        self.y += self.vel_y

        if self.y >= SCREEN_HEIGHT - self.height - 50:
            self.y = SCREEN_HEIGHT - self.height - 50
            self.is_jumping = False
            self.vel_y = 0

# Класс врага
class Enemy:
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = 1  # 1 - вправо, -1 - влево
        self.is_alive = True

    def draw(self):
        if self.is_alive:
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

    def update(self):
        if self.is_alive:
            self.x += self.speed * self.direction

            # Если враг достигает границы экрана, меняем направление
            if self.x <= 0 or self.x + self.width >= SCREEN_WIDTH:
                self.direction *= -1

    def check_collision(self, player):
        if self.is_alive and player.x < self.x + self.width and player.x + player.width > self.x and player.y < self.y + self.height and player.y + player.height > self.y:
            # Если игрок прыгает на врага сверху
            if player.vel_y > 0 and player.y + player.height - player.vel_y <= self.y:
                self.is_alive = False
            else:
                # Игрок умирает
                print("Игрок умер!")
                pygame.quit()
                sys.exit()

# Создаем объекты
player = Player()
enemy = Enemy(100, SCREEN_HEIGHT - 100, 50, 50, 5)

# Основной цикл игры
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    # Обновление
    player.update()
    enemy.update()
    enemy.check_collision(player)

    # Отрисовка
    screen.fill(WHITE)
    player.draw()
    enemy.draw()
    pygame.display.flip()

    clock.tick(60)