import sys
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра с заставкой")
clock = pygame.time.Clock()

def terminate():
    pygame.quit()
    sys.exit()

def load_image(name, colorkey=None):
    try:
        image = pygame.image.load(name)
    except pygame.error as message:
        print(f"Cannot load image: {name}")
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image

def start_screen():
    intro_text = ["ЛИЦЕЙ?",
                  "ДА"]

    fon = pygame.transform.scale(load_image('B620EB0D-4C6B-48C6-AAFA-CB8B2E696DC6_1_105_c.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 200
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)

def main():
    start_screen()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    terminate()

if __name__ == "__main__":
    main()