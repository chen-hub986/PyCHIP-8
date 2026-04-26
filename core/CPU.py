import random


class Chip8cpu:
    def __init__(self) -> None:
        print("Initializing Chip8")

        self.memory: list[int] = [0] * 4096
        self.V: bytearray = bytearray(16)
        self.I: int = 0
        self.pc: int = 0x200
        self.stack: list[int] = []
        self.delay_timer: int = 0
        self.sound_timer: int = 0
        self.display: list[list[int]] = [[0] * 64 for _ in range(32)]
        self.keys: list[int] = [0] * 16

        self._load_fonts()

    def _load_fonts(self) -> None:
        fonts = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, #8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        for i, byte in enumerate(fonts):
            self.memory[i] = byte

    def load_rom(self, rom: str) -> None:
        print("Loading rom...")

        try:
            with open(rom, 'rb') as f:
                data = f.read()

            for i in range(len(data)):
                self.memory[0x200 + i] = data[i]
            print(" rom loaded")
        except FileNotFoundError:
            print(f"Error: File '{rom}' not found.")
        except Exception as e:
            print(f"An error occurred while loading the rom: {e}")

    def fetch(self) -> int:
        #print("Fetching...")

        high_byte = self.memory[self.pc]
        low_byte = self.memory[self.pc + 1]
        opcode = (high_byte << 8) | low_byte

        self.pc += 2

        return opcode

    def update_timers(self) -> None:
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def decode_and_execute(self, opcode: int) -> None:
        category = (opcode & 0xF000) >> 12
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        nn = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        if category == 0x0:
            if opcode == 0x00E0:
                self.display = [[0] * 64 for _ in range(32)]
            elif opcode == 0x00EE:
                self.pc = self.stack.pop()
        elif category == 0x1:
            self.pc = nnn
        elif category == 0x2:
            self.stack.append(self.pc)
            self.pc = nnn
        elif category == 0x3:
            if self.V[x] == nn:
                self.pc += 2
        elif category == 0xA:
            self.I = nnn
        elif category == 0x4:
            if self.V[x] != nn:
                self.pc += 2
        elif category == 0x5:
            if self.V[x] == self.V[y]:
                self.pc += 2
        elif category == 0x6:
            self.V[x] = nn
        elif category == 0x7:
            self.V[x] = (self.V[x] + nn) & 0xFF
        elif category == 0x8:
            if n == 0x0:
                self.V[x] = self.V[y]
            elif n == 0x1:
                self.V[x] |= self.V[y]
            elif n == 0x2:
                self.V[x] &= self.V[y]
            elif n == 0x3:
                self.V[x] ^= self.V[y]
            elif n == 0x4:
                total = self.V[x] + self.V[y]
                self.V[0xF] = 1 if total > 0xFF else 0
                self.V[x] = total & 0xFF
            elif n == 0x5:
                self.V[0xF] = 1 if self.V[x] >= self.V[y] else 0
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
            elif n == 0x6:
                self.V[0xF] = self.V[x] & 1
                self.V[x] >>= 1
            elif n == 0x7:
                self.V[0xF] = 1 if self.V[y] > self.V[x] else 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
            elif n == 0xE:
                self.V[0xF] = (self.V[x] >> 7) & 1
                self.V[x] = (self.V[x] << 1) & 0xFF
            else:
                print(f"Invalid opcode: {opcode:04X}")
        elif category == 0x9:
            if self.V[x] != self.V[y]:
                self.pc += 2
        elif category == 0xB:
            self.pc = nnn + self.V[0]
        elif category == 0xC:
            self.V[x] = random.randint(0, 255) & nn
        elif category == 0xD:
            self.V[0xF] = 0

            start_x = self.V[x] % 64
            start_y = self.V[y] % 32

            for row in range(n):
                sprite_byte = self.memory[self.I + row]
                for col in range(8):
                    pixel = (sprite_byte >> (7 - col)) & 1
                    if pixel:
                        if start_x + col < 64 and start_y + row < 32:
                            if self.display[start_y + row][start_x + col] == 1:
                                self.V[0xF] = 1
                            self.display[start_y + row][start_x + col] ^= 1
        elif category == 0xE:
            if nn == 0x9E:
                if self.keys[self.V[x]]:
                    self.pc += 2
            elif nn == 0xA1:
                if not self.keys[self.V[x]]:
                    self.pc += 2
            else:
                print(f"Invalid opcode: {opcode:04X}")
        elif category == 0xF:
            if nn == 0x07:
                self.V[x] = self.delay_timer
            elif nn == 0x0A:
                # Block until any mapped key is pressed.
                key_pressed = False
                for key, state in enumerate(self.keys):
                    if state:
                        self.V[x] = key
                        key_pressed = True
                        break
                if not key_pressed:
                    self.pc -= 2
            elif nn == 0x15:
                self.delay_timer = self.V[x]
            elif nn == 0x18:
                self.sound_timer = self.V[x]
            elif nn == 0x1E:
                self.I = (self.I + self.V[x]) & 0xFFF
            elif nn == 0x29:
                # Fonts are 5 bytes per character and loaded at address 0x000.
                self.I = self.V[x] * 5
            elif nn == 0x33:
                value = self.V[x]
                self.memory[self.I] = value // 100
                self.memory[self.I + 1] = (value // 10) % 10
                self.memory[self.I + 2] = value % 10
            elif nn == 0x55:
                for idx in range(x + 1):
                    self.memory[self.I + idx] = self.V[idx]
            elif nn == 0x65:
                for idx in range(x + 1):
                    self.V[idx] = self.memory[self.I + idx]
            else:
                print(f"Invalid opcode: {opcode:04X}")
        else:
            print(f"Invalid opcode: {opcode:04X}")


if __name__ == "__main__":
    chip8cpu = Chip8cpu()
