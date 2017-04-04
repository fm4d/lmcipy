#! /usr/bin/env python

class HaltSignal(Exception):
    pass

class InvalidMachineOperationError(Exception):
    pass


def opc_add(machine, value):
    accumulator = (machine.accumulator * (-1)) if machine.minus_flag else machine.accumulator

    res = accumulator + machine.memory[value]
    machine.minus_flag = False if res >= 0 else True

    machine.accumulator = abs(res)


def opc_sub(machine, value):
    accumulator = (machine.accumulator * (-1)) if machine.minus_flag else machine.accumulator

    res = accumulator - machine.memory[value]
    machine.minus_flag = False if res >= 0 else True

    machine.accumulator = abs(res)


def opc_sta(machine, value):
    machine.memory[value] = machine.accumulator


def opc_lda(machine, value):
    machine.accumulator = machine.memory[value]
    machine.minus_flag = False


def opc_bra(machine, value):
    machine.counter = value


def opc_brz(machine, value):
    if machine.accumulator == 0:
        machine.counter = value


def opc_brp(machine, value):
    if machine.minus_flag is False:
        machine.counter = value


def opc_inp(machine):
    machine.accumulator = int(input("Input: "))


def opc_out(machine):
    print("Output:", machine.accumulator)


def opc_halt(machine):
    raise HaltSignal()


class RestrictedAttribute:

    def __init__(self, validate_func):
        self._validate_func = validate_func

    def __get__(self, instance, owner):
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        if not self._validate_func(value):
            raise InvalidMachineOperationError("Value {} did not pass validation.".format(value))

        instance.__dict__[self._name] = value

    def __set_name__(self, owner, name):
        self._name = name


class MachineMemory:

    def __init__(self):
        self._data = [0] * 99

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        check = lambda v: v >= 0 and v <= 999

        if not all(check(v) for v in (value if isinstance(value, list) else list([value]))):
            raise InvalidMachineOperationError("Value {} not in range 0 - 999.".format(value))

        self._data[index] = value

    def __str__(self):
        return str(self._data)


class MachineState():

    counter = RestrictedAttribute(lambda x: x >= 0 and x <= 99)
    accumulator = RestrictedAttribute(lambda x: x >= 0 and x <= 999)
    minus_flag = RestrictedAttribute(lambda x: x in (True, False))

    def __init__(self):
        self.counter = 0
        self.accumulator = 0
        self.minus_flag = False
        self.memory = MachineMemory()
        self.labels = {}

    def __setattr__(self, name, value):
        if name not in ('counter', 'accumulator', 'minus_flag', 'memory', 'labels'):
            raise InvalidMachineOperationError("Name {} not allowed in {}.".format(
                name, self.__class__.__name__
            ))
        super().__setattr__(name, value)


    def __str__(self):
        return "\nCounter: {}\nAccumulator: {}\nMinus flag: {}\nMemory: {}\nLabels: {}\n".format(
            self.counter,
            self.accumulator,
            self.minus_flag,
            self.memory,
            self.labels
        )


    mnemonics_to_opcodes = {
        'ADD': (lambda x: 100 + x, lambda x: x >= 0 and x <= 99),
        'SUB': (lambda x: 200 + x, lambda x: x >= 0 and x <= 99),
        'STA': (lambda x: 300 + x, lambda x: x >= 0 and x <= 99),
        'LDA': (lambda x: 500 + x, lambda x: x >= 0 and x <= 99),
        'BRA': (lambda x: 600 + x, lambda x: x >= 0 and x <= 99),
        'BRZ': (lambda x: 700 + x, lambda x: x >= 0 and x <= 99),
        'BRP': (lambda x: 800 + x, lambda x: x >= 0 and x <= 99),
        'INP': (lambda: 901, None),
        'OUT': (lambda: 902, None),
        'HLT': (lambda: 0, None),
        'DAT': (lambda x=0: x, lambda x=0: x >= 0 and x <= 999),
    }
    opcodes_to_funcs = {
        '1XX': opc_add,
        '2XX': opc_sub,
        '3XX': opc_sta,
        '5XX': opc_lda,
        '6XX': opc_bra,
        '7XX': opc_brz,
        '8XX': opc_brp,
        '901': opc_inp,
        '902': opc_out,
        '0': opc_halt
    }

