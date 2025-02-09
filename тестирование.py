import pygame
import os

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

class SlimeEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet_path):
        super().__init__()

        # Constants
        self.FRAME_WIDTH = 32
        self.FRAME_HEIGHT = 32
        self.ANIMATION_SPEED = 10  # Slower animation speed for walking
        self.DEATH_ANIMATION_SPEED = 5  # Faster death animation
        self.MOVE_SPEED = 2
        self.LEFT_ANIMATION_ROW = 0
        self.RIGHT_ANIMATION_ROW = 1
        self.DEATH_ANIMATION_ROW = 2

        # Load sprite sheet
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.frames = []
        self.load_frames()

        # Initial properties
        self.image = self.frames[self.LEFT_ANIMATION_ROW][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.frame_index = 0
        self.animation_timer = 0
        self.is_dead = False
        self.direction = 1  # 1 for right, -1 for left

    def load_frames(self):
        """Extract frames from sprite sheet for each animation row."""
        for row in range(3):
            row_frames = []
            for col in range(4):  # Corrected to 4 columns
                frame = self.sprite_sheet.subsurface(
                    (col * self.FRAME_WIDTH, row * self.FRAME_HEIGHT, self.FRAME_WIDTH, self.FRAME_HEIGHT)
                )
                row_frames.append(frame)
            self.frames.append(row_frames)

    def update(self):
        """Update enemy's movement, animation, and death state."""
        if self.is_dead:
            self.animate(self.DEATH_ANIMATION_ROW, self.DEATH_ANIMATION_SPEED)
            if self.frame_index == len(self.frames[self.DEATH_ANIMATION_ROW]) - 1:
                self.kill()  # Remove the slime from the game
            return

        # Movement logic
        self.rect.x += self.direction * self.MOVE_SPEED

        # Switch direction at screen bounds (example logic)
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1

        # Update animation based on direction
        animation_row = self.RIGHT_ANIMATION_ROW if self.direction > 0 else self.LEFT_ANIMATION_ROW
        self.animate(animation_row, self.ANIMATION_SPEED)

    def animate(self, row, speed):
        """Handle frame updates for the given animation row."""
        self.animation_timer += 1
        if self.animation_timer >= speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames[row])
        self.image = self.frames[row][self.frame_index]

    def die(self):
        """Trigger the death state for the slime."""
        self.is_dead = True
        self.frame_index = 0  # Reset animation to start

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 128, 255))  # Player color
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed_x = 0
        self.speed_y = 0
        self.gravity = 1
        self.jump_power = -15
        self.on_ground = False

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        self.speed_x = 0

        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        if keys[pygame.K_RIGHT]:
            self.speed_x = 5
        if keys[pygame.K_SPACE] and self.on_ground:
            self.speed_y = self.jump_power
            self.on_ground = False

    def update(self):
        self.handle_keys()
        self.rect.x += self.speed_x

        # Gravity
        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        # Stay within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT - 32:
            self.rect.bottom = SCREEN_HEIGHT - 32  # Align with slime height
            self.speed_y = 0
            self.on_ground = True

# Initialize the game
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slime Game")
clock = pygame.time.Clock()

# Load assets
sprite_sheet_path = "slime-spritesheet.png"  # Update this path if needed

# Create sprite groups
all_sprites = pygame.sprite.Group()
slime_group = pygame.sprite.Group()

# Create player and enemy instances
player = Player(100, SCREEN_HEIGHT - 64)
slime = SlimeEnemy(300, SCREEN_HEIGHT - 64, sprite_sheet_path)

all_sprites.add(player, slime)
slime_group.add(slime)

# Game loop
running = True
while running:
    screen.fill((50, 50, 50))  # Clear screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update sprites
    all_sprites.update()

    # Collision detection
    hits = pygame.sprite.spritecollide(player, slime_group, False)
    for slime in hits:
        if player.speed_y > 0 and player.rect.bottom <= slime.rect.top + 10:  # Player is falling and slightly above slime
            slime.die()
            player.speed_y = player.jump_power // 2  # Bounce the player after killing the slime
        else:
            print("Player died!")
            running = False

    # Draw sprites
    all_sprites.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
