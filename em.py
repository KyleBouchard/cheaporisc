from pprint import pprint

# keep sections (.text, .data) in this order
code='''
.text

.data

'''

source = [x.split('//')[0].strip() for x in code.splitlines()]

data_sect_idx = source.index('.data')
code = source[:data_sect_idx]

counters = {}

registers = {f'r{x}': 0 for x in range(32)}

data = [0] * 4096
data_ptrs = {}
for i, (k, v) in enumerate([x.split(':') for x in source[data_sect_idx + 1:]]):
    data_ptrs[k] = i
    data[i] = int(v)

line = 0
flag = 0
while True:
    insn = code[line].replace(' ', ',').split(',')
    insn = list(filter(lambda x: len(x) > 0, insn))
    if len(insn) == 0 or insn[0].endswith(':') or insn[0].startswith('.'):
        line += 1
        continue

    counters[insn[0]] = counters.get(insn[0], 0) + 1

    match insn[0]:
        case 'add':
            registers[insn[1]] = flag = registers[insn[2]] + registers[insn[3]]
        case 'sub':
            registers[insn[1]] = flag = registers[insn[2]] - registers[insn[3]]
        case 'shr':
            registers[insn[1]] = flag = registers[insn[2]] >> 1
        case 'shl':
            registers[insn[1]] = flag = registers[insn[2]] << 1
        case 'and':
            registers[insn[1]] = flag = registers[insn[2]] & registers[insn[3]]
        case 'or':
            registers[insn[1]] = flag = registers[insn[2]] | registers[insn[3]]
        case 'mv':
            registers[insn[1]] = flag = registers[insn[2]]
        case 'not':
            registers[insn[1]] = flag = ~registers[insn[2]]
        case 'br':
            line = code.index(insn[1] + ':')
        case 'brz':
            if flag == 0:
                line = code.index(insn[1] + ':')
        case 'brnz':
            if flag != 0:
                line = code.index(insn[1] + ':')
        case 'brlz':
            if flag < 0:
                line = code.index(insn[1] + ':')
        case 'brgez':
            if flag >= 0:
                line = code.index(insn[1] + ':')
        case 'ld':
            registers[insn[1]] = flag = data[registers[insn[2].removeprefix('(').removesuffix(')')]]
        case 'st':
            data[registers[insn[1].removeprefix('(').removesuffix(')')]] = flag = registers[insn[2]]
        case 'ldi':
            try:
                registers[insn[1]] = flag = int(insn[2])
            except ValueError:
                registers[insn[1]] = flag = data_ptrs[insn[2]]
        case 'stop':
            break
        case _:
            print('unknown insn ' + insn[0])
    
    line += 1

pprint(counters)
print(f'{sum(counters.values())} instruction executed')