import sys

from minidatabase.Tokenizer import Tokenizer
from minidatabase.Parser import  Parser
import argparse


def parse(query:str):
    t = Tokenizer()
    t.input = query
    t.scan()
    tokens = t.tokens
    p = Parser(tokens)
    ast = p.parse()
    return ast

def main():
    parser = argparse.ArgumentParser(prog="parser")

    sub = parser.add_subparsers(dest="command", required=True)
    generateAST = sub.add_parser("parse",help="supply sql query as an arugument to this command")
    parser.add_argument("query")
    args = parser.parse_args()
    print(parse(args.query));
    sys.exit()