#! /usr/bin/env python

import argparse
import sys
import os

try:
    import lmcipy
except:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
    import lmcipy


parser = argparse.ArgumentParser(description='Little Man Computer interpreter.')
parser.add_argument('file', type=argparse.FileType('r'))
parser.add_argument('--debug', dest='debug', action='store_true')
args = parser.parse_args()

program = lmcipy.util.load_program(args.file.readlines())
lmcipy.interpret(program=program, debug=True if args.debug else False)
