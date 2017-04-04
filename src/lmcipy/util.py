#! /usr/bin/env python

from functools import wraps
from copy import deepcopy


def copy_args(*args):
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
    return [remove_comments(tokenize(line)) for line in code]

def tokenize(line):
    return line.strip().split()

def remove_comments(tokens):
    try:
        return tokens[:tokens.index('//')]
    except ValueError:
        return tokens


