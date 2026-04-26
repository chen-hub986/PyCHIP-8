import pygame
import sys
from pathlib import Path

from core.CPU import Chip8cpu
from core.Display import Display
from core.input import get_key_state


def main() -> None:
    base_dir = Path(__file__).resolve().parent

    pygame.init()
    pygame.mixer.init()
    beep_sound = pygame.mixer.Sound(str(base_dir / "beep.mp3"))
    beep_sound.set_volume(0.1)
    pygame.display.set_caption("PyChip8")
    display = Display(scale=10)
    cpu = Chip8cpu()
    clock = pygame.time.Clock()

    time_event = pygame.USEREVENT + 1
    pygame.time.set_timer(time_event, 17)

    cpu.load_rom(str(base_dir / "roms" / "Pong.ch8"))

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
