#! /usr/bin/env python

import pytest

from lmcipy.machine import *


@pytest.fixture
def empty_machine():
    return MachineState()



class TestOpcodeFunctions:

    def test_opc_add(self, empty_machine):
        empty_machine.accumulator = 10
        empty_machine.memory[1] = 5

        opc_add(empty_machine, 1)

        assert empty_machine.accumulator == 15


    def test_opc_add_with_flag(self, empty_machine):
        empty_machine.accumulator = 5
        empty_machine.memory[1] = 10
        empty_machine.minus_flag = True

        opc_add(empty_machine, 1)

        assert empty_machine.accumulator == 5
        assert empty_machine.minus_flag == False


    def test_opc_sub(self, empty_machine):
        empty_machine.accumulator = 10
        empty_machine.memory[1] = 5

        opc_sub(empty_machine, 1)

        assert empty_machine.accumulator == 5


    def test_opc_sub_with_flag(self, empty_machine):
        empty_machine.accumulator = 5
        empty_machine.memory[1] = 10
        empty_machine.minus_flag = True

        opc_sub(empty_machine, 1)

        assert empty_machine.accumulator == 15
        assert empty_machine.minus_flag == True


    def test_opc_sta(self, empty_machine):
        empty_machine.accumulator = 10

        opc_sta(empty_machine, 1)

        assert empty_machine.memory[1] == 10


    def test_opc_lda(self, empty_machine):
        empty_machine.memory[1] = 10

        opc_lda(empty_machine, 1)

        assert empty_machine.accumulator == 10


    def test_opc_bra(self, empty_machine):
        empty_machine.counter = 1

        opc_bra(empty_machine, 5)

        assert empty_machine.counter == 5


    def test_opc_brz(self, empty_machine):
        empty_machine.counter = 1
        empty_machine.accumulator = 0

        opc_brz(empty_machine, 5)

        assert empty_machine.counter == 5


    def test_opc_brz_not(self, empty_machine):
        empty_machine.counter = 1
        empty_machine.accumulator = 1

        opc_brz(empty_machine, 5)

        assert empty_machine.counter == 1


    def test_opc_brp(self, empty_machine):
        empty_machine.counter = 1
        empty_machine.accumulator = 1

        opc_brp(empty_machine, 5)

        assert empty_machine.counter == 5


    def test_opc_brp_not(self, empty_machine):
        empty_machine.counter = 1
        empty_machine.accumulator = 1
        empty_machine.minus_flag = True

        opc_brp(empty_machine, 5)

        assert empty_machine.counter == 1


class TestMachine:

    def test_restricted_attribute(self):
        class TestClass:
            x = RestrictedAttribute(lambda x: x > 1 and x < 5)

            def __init__(self):
                self.x = 4

        tc = TestClass()
        assert tc.x == 4


    def test_restricted_attribute_fails(self):
        class TestClass:
            x = RestrictedAttribute(lambda x: x > 1 and x < 5)

            def __init__(self):
                self.x = 5

        with pytest.raises(InvalidMachineOperationError):
            tc = TestClass()


    def test_machine_memory(self):
        test_memory = MachineMemory()
        test_memory[33] = 11

        assert test_memory[33] == 11


    def test_machine_memory_fails(self):
        test_memory = MachineMemory()

        with pytest.raises(InvalidMachineOperationError):
            test_memory[33] = 1011

        with pytest.raises(InvalidMachineOperationError):
            test_memory[33] = -17


    def test_machine_state_access(self):
        test_machine = MachineSatte()
        self.counter = 11

        assert self.counter == 11


    def test_machine_state_access(self):
        test_machine = MachineState()

        with pytest.raises(InvalidMachineOperationError):
            test_machine.test = 1





