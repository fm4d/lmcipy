#! /usr/bin/env python

import pytest

from lmcipy.interpret import (
    process_labels,
    generate_opcodes,
    opcode_func_deconstruct,
    load_opcodes,
    eval_opcode,
    interpret,
    SyntaxError
)
from lmcipy.machine import MachineState


@pytest.fixture
def empty_machine():
    return MachineState()


def test_process_labels(empty_machine):
    test_program = [
        ['INP'],
        ['LABEL1', 'DAT'],
        ['SUB', 'LABEL2'],
    ]

    test_machine, res_program = process_labels(machine=empty_machine, program=test_program)
    assert test_machine.labels == {'LABEL1': 1}
    assert res_program == [
        ['INP'],
        ['DAT'],
        ['SUB', 'LABEL2']
    ]


def test_generate_opcodes(empty_machine):
    test_program = [
        ['ADD', '10'],
        ['SUB', 'TESTLABEL'],
        ['INP'],
        ['HLT'],
        ['DAT'],
        ['DAT', '23'],
    ]
    empty_machine.labels['TESTLABEL'] = 87

    opcodes = generate_opcodes(machine=empty_machine, program=test_program)

    assert list(opcodes) == [110, 287, 901, 0, 0, 23]


def test_generate_opcodes_arg_wrong_count(empty_machine):
    test_program = [
        ['ADD', '10', '20']
    ]

    with pytest.raises(SyntaxError):
        generate_opcodes(machine=empty_machine, program=test_program)


def test_generate_opcodes_arg_wrong_size(empty_machine):
    test_program = [
        ['ADD', '100']
    ]

    with pytest.raises(SyntaxError):
        generate_opcodes(machine=empty_machine, program=test_program)


def test_generate_opcodes_arg_wrong_argument(empty_machine):
    test_program = [
        ['ADD']
    ]

    with pytest.raises(SyntaxError):
        generate_opcodes(machine=empty_machine, program=test_program)


def test_opcode_to_func(empty_machine):
    opcode = '901'

    func = opcode_func_deconstruct(empty_machine, opcode)

    assert func.__name__ == "opc_inp"


def test_opcode_to_func_with_arg(empty_machine):
    opcode = '111'
    func = opcode_func_deconstruct(empty_machine, opcode)

    assert func.func.__name__ == "opc_add"
    assert func.keywords['value'] == 11


def test_opcode_to_func_with_arg_single_digit(empty_machine):
    opcode = '101'
    func = opcode_func_deconstruct(empty_machine, opcode)

    assert func.func.__name__ == "opc_add"
    assert func.keywords['value'] == 1


def test_opcode_to_func_invalid_opcode(empty_machine):
    opcode = '400'

    with pytest.raises(Exception):
        opcode_func_deconstruct(empty_machine, opcode)


def test_load_opcodes(empty_machine):
    opcodes = [111, 000, 901, 244]
    res_machine = load_opcodes(machine=empty_machine, opcodes=opcodes)

    assert res_machine.memory[0:4] == opcodes


def test_eval_opcode_memory(empty_machine):
    empty_machine.accumulator = 10
    test_opcode = 301

    res_machine = eval_opcode(machine=empty_machine, opcode=test_opcode)

    assert res_machine.memory[1] == 10


def test_eval_opcode_accumulator(empty_machine):
    empty_machine.accumulator = 10
    empty_machine.memory[1] = 5
    test_opcode = 201

    res_machine = eval_opcode(machine=empty_machine, opcode=test_opcode)

    assert res_machine.accumulator == 5


def test_minus_flag_set(empty_machine):
    empty_machine.memory[1] = 20
    empty_machine.accumulator = 15
    test_opcode = 201

    res_machine = eval_opcode(machine=empty_machine, opcode=test_opcode)

    assert res_machine.minus_flag == True
    assert res_machine.accumulator == 5


def test_minus_flag_unset(empty_machine):
    empty_machine.memory[1] = 10
    empty_machine.accumulator = 5
    empty_machine.minus_flag = True
    test_opcode = 101

    res_machine = eval_opcode(machine=empty_machine, opcode=test_opcode)

    assert res_machine.minus_flag == False
    assert res_machine.accumulator == 5




