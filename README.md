# PolyRISC Debugger/Emulator

## Introduction

PolyRISC Debugger/Emulator is a tool designed to debug and emulate programs written for the PolyRISC architecture. It provides various commands to help users debug their programs efficiently.

## Usage

`python em.py ./path/to/file.asm`

## Options

- `help`: Show this message
- `s|step`: Steps an instruction
- `c|continue`: Continues until breakpoint
- `r|regs [registers]`: Show registers
- `f|flag`: Shows flag
- `d|data [start_addr [, n_bytes]]`: Shows data
- `b|break addr`: Toggle breakpoint
- `b|break`: List breakpoints
- `ip`: Shows ip
- `dis`: Disassemble
- `exit`: Exit

## Usage example

```
> b 3

> run
Type help for all commands

> b 3

> b 3

> c  
Breakpoint hit: ['sub', 'r14', 'r11', 'r10']

> r r14 r11 r10
{'r10': 5, 'r11': 0, 'r14': 0}

> data
0: 5
1: 1
2: 2
3: 0
4: 0
5: 0
6: 0
7: 0
8: 0
9: 0
```
