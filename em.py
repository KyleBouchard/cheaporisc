from pprint import pprint
import sys
from typing import List

class Emulator:
    def __init__(self, source):
        source = [x.split('//')[0].strip() for x in source.splitlines()]

        self.ip = 0
        self.flag = 0
        self.registers = {f'r{x}': 0 for x in range(32)}
        self.text = []
        self.text_labels = {}
        self.data = bytearray(4096)
        self.data_labels = {}
        self.stopped = False
        self.breakpoints = []
        
        data_pointer = 0
        section = None
        for line in source:
            if line.startswith('.'):
                section = line[1:]
            elif section == 'text':
                insn = line.replace(' ', ',').split(',')
                insn = list(filter(lambda x: len(x) > 0, insn))

                if len(insn) == 0:
                    continue
                elif insn[0].endswith(':'):
                    self.text_labels[insn[0][:-1]] = len(self.text)
                else:
                    self.text.append(insn)
            elif section == 'data':
                label, values = line.split(':')

                self.data_labels[label.strip()] = data_pointer

                for v in values.split(','):
                    self.data[data_pointer] = int(v.strip())
                    data_pointer += 1
            else:
                print(f'Unknown section: {section}')
    
    def line(self):
        return self.text[self.ip]

    def step(self):
        insn = self.text[self.ip]
        self.ip += 1

        match insn[0]:
            case 'add':
                self.registers[insn[1]] = self.flag = self.registers[insn[2]] + self.registers[insn[3]]
            case 'sub':
                self.registers[insn[1]] = self.flag = self.registers[insn[2]] - self.registers[insn[3]]
            case 'shr':
                self.registers[insn[1]] = self.flag = self.registers[insn[2]] >> 1
            case 'shl':
                self.registers[insn[1]] = self.flag = self.registers[insn[2]] << 1
            case 'and':
                self.registers[insn[1]] = self.flag = self.registers[insn[2]] & self.registers[insn[3]]
            case 'or':
                self.registers[insn[1]] = self.flag = self.registers[insn[2]] | self.registers[insn[3]]
            case 'mv':
                self.registers[insn[1]] = self.flag = self.registers[insn[2]]
            case 'not':
                self.registers[insn[1]] = self.flag = ~self.registers[insn[2]]
            case 'br':
                self.ip = self.text_labels[insn[1]]
            case 'brz':
                if self.flag == 0:
                    self.ip = self.text_labels[insn[1]]
            case 'brnz':
                if self.flag != 0:
                    self.ip = self.text_labels[insn[1]]
            case 'brlz':
                if self.flag < 0:
                    self.ip = self.text_labels[insn[1]]
            case 'brgez':
                if self.flag >= 0:
                    self.ip = self.text_labels[insn[1]]
            case 'ld':
                self.registers[insn[1]] = self.flag = self.data[self.registers[insn[2].removeprefix('(').removesuffix(')')]]
            case 'st':
                self.data[self.registers[insn[1].removeprefix('(').removesuffix(')')]] = flag = self.registers[insn[2]]
            case 'ldi':
                try:
                    self.registers[insn[1]] = self.flag = int(insn[2])
                except ValueError:
                    self.registers[insn[1]] = self.flag = self.data_labels[insn[2]]
            case 'stop':
                self.stopped = True
            case _:
                print('unknown insn ' + insn[0])

    def run(self):
        while not self.stopped:
            self.step()

            if self.ip in self.breakpoints:
                print(f'Breakpoint hit: {self.line()}')
                break


def main(argv: List[str]):
    if len(argv) != 2:
        print(f'Usage {__file__ if len(argv) == 0 else argv[0]} file.asm')
        return 1

    with open(argv[1], 'r') as f:
        emu = Emulator(f.read())
    
    while True:
        dbcmd = input('> ').split(' ')

        match dbcmd[0]:
            case 'help':
                opts = {
                    'help': 'Show this message',
                    's|step': 'Steps an instruction',
                    'c|continue': 'Continues until breakpoint',
                    'r|regs [registers]': 'Show registers',
                    'f|flag': 'Shows flag',
                    'd|data [start_addr [, n_bytes]]': 'Shows data',
                    'b|break addr': 'Toggle breakpoint',
                    'b|break': 'List breakpoints',
                    'ip': 'Shows ip',
                    'dis': 'Disassemble',
                    'exit': 'Exit',
                }

                for k, v in opts.items():
                    print(f'{k}: {v}')
            case 's' | 'step':
                if len(dbcmd) < 2:
                    steps = 1
                else:
                    steps = int(dbcmd[1])
                
                for i in range(steps):
                    print(emu.line())
                    emu.step()
            case 'c' | 'continue':
                emu.run()
            case 'r' | 'regs':
                if len(dbcmd) < 2:
                    pprint(emu.registers)
                else:
                    pprint({k: v for k, v in emu.registers.items() if k in dbcmd[1:]})
            case 'f' | 'flag':
                print(emu.flag)
            case 'd' | 'data':
                start_addr = int(dbcmd[1]) if len(dbcmd) >= 2 else 0
                n_bytes = int(dbcmd[2]) if len(dbcmd) >= 3 else 10
                
                for i, x in enumerate(emu.data[start_addr:start_addr+n_bytes]):
                    print(f'{i}: {x}')
            case 'ip':
                print(emu.ip)
            case 'dis':
                for i, insn in enumerate(emu.text):
                    print(i, *[k for k, v in emu.text_labels.items() if v == i], insn)
            case 'exit':
                return 0
            case 'b' | 'break':
                if len(dbcmd) == 1:
                    for i, insn in enumerate(emu.text):
                        if i in emu.breakpoints:
                            print(i, insn)
                else:
                    for b in dbcmd[1:]:
                        b = int(b)
                        if b in emu.breakpoints:
                            emu.breakpoints.remove(b)
                        else:
                            emu.breakpoints.append(b)
            case _:
                print('Type help for all commands')

        print()


if __name__ == '__main__':
    exit(main(sys.argv))