import pygame
import sys

from CPU import Chip8cpu
from Display import Display
from input import get_key_state


def main():
    pygame.init()
    pygame.mixer.init()
    beep_sound = pygame.mixer.Sound("beep.mp3")
    pygame.display.set_caption("PyChip8")
    display = Display(scale=10)
    cpu = Chip8cpu()
    clock = pygame.time.Clock()

    time_event = pygame.USEREVENT + 1
    pygame.time.set_timer(time_event, 17)

    cpu.load_rom("Pong.ch8")

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == time_event:
                cpu.update_timers()

        cpu.keys = get_key_state()

        for _ in range(10):
            opcode = cpu.fetch()
            cpu.decode_and_execute(opcode)
        display.render(cpu.display)

        if cpu.sound_timer > 0 and not pygame.mixer.get_busy():
            beep_sound.play()
            print("BEEP!")

        clock.tick(60)

    display.quit()
    sys.exit()


if __name__ == "__main__":
    main()
