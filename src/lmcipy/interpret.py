#! /usr/bin/env python

from functools import partial

from .util import copy_args, tokenize
from .machine import MachineState, HaltSignal


class SyntaxError(Exception):

    def __init__(self, line_num, msg):
        self.line_num = line_num
        self.msg = msg

        super().__init__("SyntaxError on line {}: {}".format(line_num + 1, msg))


@copy_args('machine')
def process_labels(machine, program):

    def process(line, line_num):

        if line:
            possible_label, rest_of_line = line[0], line[1:]

            if possible_label not in machine.mnemonics_to_opcodes:
                machine.labels[possible_label] = line_num
                return rest_of_line

        return line

    return machine, [process(line, line_num) for line_num, line in enumerate(program)]


@copy_args('machine')
def generate_opcodes(machine, program):

    def check_arg(check_func, arg):
        if check_func is None:
            return True if arg is None else False

        if arg is None:
            return check_func()

        return check_func(arg)

    def resolve_arg(arg):
        if arg is None:
            return None
        elif arg.isnumeric():
            return int(arg)

        return machine.labels[arg]

    def generate(line, line_num):
        if len(line) > 2:
            raise SyntaxError(line_num, 'Too many tokens. Tokens: {}'.format(line))

        mnem, arg = line[0], line[1] if len(line) == 2 else None
        func, arg_check = machine.mnemonics_to_opcodes[mnem]
        resolved_arg = resolve_arg(arg)

        try:
            if not check_arg(arg_check, resolved_arg):
                raise SyntaxError(line_num, 'Invalid argument. Argument: {}'.format(resolved_arg))
        except TypeError:
            raise SyntaxError(line_num, 'Missing argument.')

        return func(*([resolved_arg] if resolved_arg is not None else []))

    return [generate(line, line_num) if line else 0 for line_num, line in enumerate(program)]


def opcode_func_deconstruct(machine, opcode):
    if len(opcode) < 3:
        return machine.opcodes_to_funcs['0']

    if opcode[0] in ('9', '0'):
        return machine.opcodes_to_funcs[opcode]

    def get_func():
        res = [func for p_opcode, func in machine.opcodes_to_funcs.items()
               if opcode[0] == p_opcode[0]]
        if not res or len(res) > 1:
            raise Exception("Invalid opcode {}".format(opcode))

        return res[0]

    func = get_func()
    arg = int(opcode[1:3])

    return partial(func, value=arg)


@copy_args('machine')
def eval_opcode(machine, opcode):
    func = opcode_func_deconstruct(machine, str(opcode))
    machine.counter += 1

    try:
        func(machine=machine)
    except HaltSignal:
        return None

    return machine


@copy_args('machine')
def load_opcodes(machine, opcodes):
    machine.memory[0:len(opcodes)] = opcodes
    return machine


def run(machine, debug=False):

    if machine is None:
        return

    if debug:
        print(machine)

    run(
        machine=eval_opcode(machine=machine,
                            opcode=machine.memory[machine.counter]),
        debug=debug
    )


@copy_args('program')
def interpret(program, debug=False):
    machine = MachineState()
    machine, program = process_labels(machine=machine, program=program)
    opcodes = generate_opcodes(machine=machine, program=program)
    machine = load_opcodes(machine=machine, opcodes=opcodes)
    run(machine=machine, debug=debug)

    return machine
