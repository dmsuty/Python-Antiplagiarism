#!/usr/bin/python3
'''
my plans are:
    -add exception
    -add LCS realisation
    - #... comments problem
'''
import argparse
import ast
import numpy as np
import re


class CodeTransformer(ast.NodeTransformer):
    def visit_arg(self, node):
        return ast.arg(**{**node.__dict__, 'arg': 'a'})

    def visit_Name(self, node):
        return ast.Name(**{**node.__dict__, 'id': 'n'})

    def visit_Import(self, node):
        return None


class Code:
    def __init__(self, file_name):
        with open(file_name, 'r') as source:
            self.code = source.read()
        self.code = re.sub(r'"""[\s\S]*?"""', '', self.code)
        self.code = re.sub(r"'''[\s\S]*?'''", '', self.code)
        self.code = re.sub(r'#.*?\n', '\n', self.code)
        self.structure = ast.unparse(
            CodeTransformer().visit(ast.parse(self.code)))

    @staticmethod
    # type checking is not good enough at the moment ;(
    def levenshtein_distance(code1, code2) -> int:
        dp = np.zeros((len(code1.structure) + 1,
                      len(code2.structure) + 1), int)
        for i in range(len(code1.structure) + 1):
            for j in range(len(code2.structure) + 1):
                if i == 0 or j == 0:
                    dp[i][j] = max(i, j)
                else:
                    dp[i][j] = min(dp[i][j - 1], dp[i - 1][j]) + 1
                    if code1.structure[i - 1] == code2.structure[j - 1]:
                        dp[i][j] = min(dp[i][j], dp[i - 1][j - 1])
                    else:
                        dp[i][j] = min(dp[i][j], dp[i - 1][j - 1] + 1)
        return dp[-1][-1]

    @staticmethod
    def LCS(code1, code2) -> int:
        return 1

    @staticmethod
    def plagiarism_rate(code1, code2) -> float:
        return round(1 - Code.levenshtein_distance(code1, code2) /
                     max(len(code1.structure), len(code2.structure)), 2)


class Solver:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input')
        parser.add_argument('scores')
        self.args = parser.parse_args()

    def Run(self):
        with open(self.args.input, 'r') as fin:
            with open(self.args.scores, 'w') as fout:
                for line in fin:
                    try:
                        code1, code2 = map(Code, line.split())
                        rate = Code.plagiarism_rate(code1, code2)
                        fout.write(f'result is {int(rate * 100)}%\n')
                    except SyntaxError:
                        fout.write(
                            "one of these programs has incorrect syntax\n")


if __name__ == '__main__':
    Solver().Run()
