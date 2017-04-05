#! /usr/bin/env python

from functools import partial

from .util import copy_args, tokenize
from .machine import MachineState, HaltSignal


class SyntaxError(Exception):
    """
    Error in LMC program syntax.

    Args:
        line_num (int): Number of line with error.
        msg (str): Error.
    """

    def __init__(self, line_num, msg):
        self.line_num = line_num
        self.msg = msg

        super().__init__("SyntaxError on line {}: {}".format(line_num + 1, msg))


class UnknownOpcodeError(Exception):
    """
    Opcode unknown.

    Args:
        opcode (int): Opcode.
    """

    def __init__(self, opcode):
        self.opcode = opcode

        super().__init__("Opcode {} is not specified".format(self.opcode))


@copy_args('machine')
def process_labels(machine, program):
    """
    Remove labels from `program` and store (label: line number) in `machine.labels`.

    Args:
        machine (obj): Instance of class:`MachineState`.
        program (list): List of lists of strings representing tokenized lines of program.

    Returns:
        obj: Instance of class:`MachineState` with set labels.
        list: `program` without labels.
    """
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
    """
    Translate syntactical mnemonics into opcodes.

    Args:
        machine (obj): Instance of class:`MachineState`.
        program (list): List of lists of strings representing tokenized lines of program.

    Raises:
        SyntaxError: Raised when trying to generate opcode for invalid line of program.

    Returns:
        list: List of opcodes converted from `program`.
    """
    def check_arg(check_func, arg):
        """
        Check that `arg` satisfies checking func of opcode.

        Args:
            check_func (func): Checking fuc of opcode, makes sure that no invalid argument
                               is supplied.
            arg (str or int or None): Argument to be checked against check_func.

        Raises:
            TypeError: Raised when check_func is supplied with wrong number of arguments.

        Returns:
            True or False
        """
        if check_func is None:
            return True if arg is None else False

        if arg is None:
            return check_func()

        return check_func(arg)

    def resolve_arg(arg):
        """
        Converte numerical arguments to ``int`` and replaces labels with their address.

        Args:
            arg (str): Mnemonics argument.

        Returns:
            None or int or str: Argument ready for use in generating opcode.
        """
        if arg is None:
            return None
        elif arg.isnumeric():
            return int(arg)

        return machine.labels[arg]

    def generate(line, line_num):
        """
        Convert single line of tokens into opcode.

        Args:
            line (list): List of strings representating single mnemonics + argument.
            line_num (int): Line number.

        Raises:
            SyntaxError: Raised when trying to generate opcode for invalid line of program.

        Returns:
            int: Opcode.
        """
        if len(line) > 2:
            raise SyntaxError(line_num, 'Too many tokens. Tokens: {}'.format(line))

        mnem, arg = line[0], line[1] if len(line) == 2 else None
        func, arg_check = machine.mnemonics_to_opcodes[mnem]
        resolved_arg = resolve_arg(arg)

        try:
            if not check_arg(arg_check, resolved_arg):
                raise SyntaxError(line_num, 'Invalid argument. Argument: {}'.format(resolved_arg))
        except TypeError:
            raise SyntaxError(line_num, 'Wrong ammount of arguments.')

        return func(*([resolved_arg] if resolved_arg is not None else []))


    return [generate(line, line_num) if line else 0 for line_num, line in enumerate(program)]


def opcode_func_deconstruct(machine, opcode):
    """
    Find and return funcion that belongs to opcode and partialy apply its argument.

    Args:
        machine (obj): Instance of class:`MachineState`.
        opcode (int): Opcode.

    Raises:
        UnknownOpcodeError: Raised when opcode is not found in `machine.opcodes_to_funcs`.

    Returns:
        func: Function that represents opcode behaviour with curried argument.
    """
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
    """
    Perform action defined for `opcode`.

    Args:
        machine (obj): Instance of class:`MachineState`.
        opcode (int): Opcode.

    Raises:
        UnknownOpcodeError: Raised when opcode is not found in `machine.opcodes_to_funcs`.

    Returns:
        obj: Instance of class :`MachineState` opcode action was performed on.
    """
    func = opcode_func_deconstruct(machine, str(opcode))
    machine.counter += 1

    try:
        func(machine=machine)
    except HaltSignal:
        return None

    return machine


@copy_args('machine')
def load_opcodes(machine, opcodes):
    """
    Copy opcodes into `machine.memory`.

    Args:
        machine (obj): Instance of class:`MachineState`.
        opcode (list): List of integers - opcodes.

    Returns:
        obj: Instance of class :`MachineState` opcodes were loaded into.
    """
    machine.memory[0:len(opcodes)] = opcodes

    return machine


def run(machine, debug=False):
    """
    Recursive function that runs opcodes from `machine.memory` until halt.

    Args:
        machine (obj): Instance of class:`MachineState`.
        debug (bool): Whether to print debug information for each cycle.

    Raises:
        UnknownOpcodeError: Raised when opcode is not found in `machine.opcodes_to_funcs`.
    """
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
    """
    Convert `program` into opcode and evaluate them.

    Args:
        program (list): List of lists of strings representing tokenized lines of program.
        debug (bool): Whether to print debug information for each cycle.

    Raises:
        SyntaxError: Raised when trying to generate opcode for invalid line of program.
        UnknownOpcodeError: Raised when opcode is not found in `machine.opcodes_to_funcs`.
    """
    machine = MachineState()
    machine, program = process_labels(machine=machine, program=program)
    opcodes = generate_opcodes(machine=machine, program=program)
    machine = load_opcodes(machine=machine, opcodes=opcodes)
    run(machine=machine, debug=debug)
