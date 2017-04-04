#! /usr/bin/env python

import pytest

from lmcipy.util import copy_args


def test_copy_args_args():

    orig_dict = {1: 1, 2: 2, 3: 3}

    @copy_args()
    def test_func(dict_arg):
        dict_arg[4] = 4
        return dict_arg

    cloned_dict = test_func(orig_dict)


    assert orig_dict == {1: 1, 2: 2, 3: 3}
    assert cloned_dict == {1: 1, 2: 2, 3: 3, 4: 4}


def test_copy_args_kwargs():

    orig_dict = {1: 1, 2: 2, 3: 3}

    @copy_args()
    def test_func(dict_arg):
        dict_arg[4] = 4
        return dict_arg

    cloned_dict = test_func(dict_arg=orig_dict)


    assert orig_dict == {1: 1, 2: 2, 3: 3}
    assert cloned_dict == {1: 1, 2: 2, 3: 3, 4: 4}


def test_copy_args_with_decorator_args():

    orig_dict = {1: 1, 2: 2, 3: 3}
    orig_dict2 = {1: 1, 2: 2, 3: 3}

    @copy_args("dict_arg")
    def test_func(dict_arg, dict_arg2):
        dict_arg[4], dict_arg2[4] = 4, 4
        return dict_arg, dict_arg2

    cloned_dict, cloned_dict2 = test_func(
        dict_arg=orig_dict,
        dict_arg2=orig_dict2
    )


    assert orig_dict == {1: 1, 2: 2, 3: 3}
    assert cloned_dict == {1: 1, 2: 2, 3: 3, 4: 4}
    assert orig_dict2 == {1: 1, 2: 2, 3: 3, 4: 4}
    assert cloned_dict2 == {1: 1, 2: 2, 3: 3, 4: 4}


def test_copy_args_with_decorator_no_kwargs_fail():

    orig_dict = {1: 1, 2: 2, 3: 3}
    orig_dict2 = {1: 1, 2: 2, 3: 3}

    @copy_args("dict_arg")
    def test_func(dict_arg, dict_arg2):
        dict_arg[4], dict_arg2[4] = 4, 4
        return dict_arg, dict_arg2

    with pytest.raises(TypeError):
        cloned_dict, cloned_dict2 = test_func(orig_dict, dict_arg2=orig_dict2)
