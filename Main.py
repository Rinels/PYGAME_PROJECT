import pygame
import sys

WIDTH = 800
HEIGHT = 600
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

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Супер Малыш Хорек")
clock = pygame.time.Clock()


class BabyFerret(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 100)
        self.velocity_y = 0
        self.is_jumping = False

    def update(self, keys, platforms):
        if keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED

        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.velocity_y > 0:
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False

        if keys[pygame.K_w] and not self.is_jumping:
            self.velocity_y = JUMP_STRENGTH
            self.is_jumping = True

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.is_jumping = False


class Princess(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


class Fungus(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


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

        level_layout = [
            (0, HEIGHT - 20, WIDTH, 20),
            (200, 500, 150, 20),
            (400, 400, 150, 20),
            (600, 300, 150, 20),
            (300, 200, 100, 20)
        ]

        for x, y, width, height in level_layout:
            platform = Platform(x, y, width, height)
            self.platforms.add(platform)
            self.all_sprites.add(platform)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            self.Ferret.update(keys, self.platforms)
            screen.fill(CYAN)
            self.all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)


class SecondLevel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


class FinalLevel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":

    def start_screen():
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


    pygame.init()
    start_screen()
    level = FirstLevel()
    level.run()
    pygame.quit()
    sys.exit()