import pygame


class Display:
    def __init__(self, scale=10):
        self.width = 64
        self.height = 32
        self.scale = scale
        self.screen = pygame.display.set_mode((self.width * self.scale, self.height * self.scale))
        pygame.display.set_caption("PyChip8 Emulator")

        self.color_black = (0, 0, 0)
        self.color_white = (255, 255, 255)

    def clear(self):
        self.screen.fill(self.color_black)
        pygame.display.flip()

    def render(self, cpu_display):
        for y in range(self.height):
            for x in range(self.width):
                color = self.color_white if cpu_display[y][x] else self.color_black
                pygame.draw.rect(self.screen, color, (x * self.scale, y * self.scale, self.scale, self.scale))
        pygame.display.flip()

    def quit(self):
        pygame.quit()
