#! /usr/bin/env python

from functools import wraps
from copy import deepcopy


def copy_args(*args):
    """
    Forces function to use deepcopies of all arguments, partially imitating pass-by-value.
    """
    top_decorator_args = args

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not top_decorator_args:
                    return func(*deepcopy(args), **deepcopy(kwargs))

            kwargs = {key: (deepcopy(value) if key in top_decorator_args else value)
                      for key, value in kwargs.items()}

            return func(**kwargs)

        return wrapper

    return decorator


def load_program(code):
    """
    Remove comments and split lines into tokens.

    Args:
        code (list): List of strings representing loaded program.

    Returns:
        list: List of lists of string tokens.
    """
    return [remove_comments(tokenize(line)) for line in code]


def tokenize(line):
    return line.strip().split()


def remove_comments(tokens):
    try:
        return tokens[:tokens.index('//')]
    except ValueError:
        return tokens


