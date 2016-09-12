# coding=utf-8


from invoke import Program
from tasks import ns
import sys


if __name__ == '__main__':
    program = Program(namespace=ns, version='0.1.0')
    program.run(sys.argv)
