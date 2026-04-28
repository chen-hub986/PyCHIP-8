import pygame
import sys

from core.CPU import Chip8cpu
from core.Display import Display
from core.input import get_key_state


def main() -> None:
    if len(sys.argv) == 1:
        print("USAGE: python.exe play.py [rom_path]")
        sys.exit(1)

    pygame.init()
    pygame.mixer.init()
    beep_sound = pygame.mixer.Sound(str("beep.mp3"))
    beep_sound.set_volume(0.1)  # You can adjust the volume as needed
    pygame.display.set_caption("PyChip8")
    display = Display(scale=10)
    cpu = Chip8cpu()
    clock = pygame.time.Clock()

    time_event = pygame.USEREVENT + 1
    pygame.time.set_timer(time_event, 17)

    cpu.load_rom(str(sys.argv[1]))

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

        clock.tick(50) #You can change the value to adjust the speed of the emulation

    display.quit()
    sys.exit()


if __name__ == "__main__":
    main()
