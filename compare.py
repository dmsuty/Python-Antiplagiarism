#!/usr/bin/python3
import argparse
import ast
import numpy as np
import re


class CodeTransformer1(ast.NodeTransformer):
    def visit_arg(self, node: ast.arg) -> ast.arg:
        '''renaming arguments in function declarations'''
        return ast.arg(**{**node.__dict__, 'arg': 'a'})

    def visit_Name(self, node: ast.Name) -> ast.Name:
        '''renaming names in code'''
        return ast.Name(**{**node.__dict__, 'id': 'n'})

    def visit_Import(self, node: ast.Import) -> None:
        '''removing all imports'''
        return None

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        '''removing all from ... imports'''
        return None


class CodeTransformer2(ast.NodeTransformer):
    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        '''renaming class definitions'''
        return ast.ClassDef(**{**node.__dict__, 'name': 'CName'})

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        '''renaming function definitions'''
        return ast.FunctionDef(**{**node.__dict__, 'name': 'FName'})


class Code:
    def __init__(self, file_name: str):
        '''Load data and converting the code into structure field'''
        with open(file_name, 'r') as source:
            self.code = source.read()
        self.code = re.sub(r'"""[\s\S]*?"""', '', self.code)
        self.code = re.sub(r"'''[\s\S]*?'''", '', self.code)
        self.structure = ast.unparse(
            CodeTransformer1().visit(ast.parse(self.code)))
        self.structure = ast.unparse(
            CodeTransformer2().visit(ast.parse(self.structure)))

    @staticmethod
    # type checking is not good enough at the moment ;(
    def levenshtein_distance(code1, code2) -> int:
        '''calculating the levenshtein distance'''
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
    # may be faster with hash-function
    def LCS(code1, code2) -> int:
        '''calculating the longest common substring length'''
        lcs_suff = np.zeros((len(code1.structure) + 1,
                             len(code2.structure) + 1), int)
        result = 0
        for i in range(1, len(code1.structure) + 1):
            for j in range(1, len(code2.structure) + 1):
                if code1.structure[i] == code2.structure[j]:
                    lcs_suff[i][j] = lcs_suff[i][j] + 1
                result = max(result, lcs_suff[i][j])
        return result

    @staticmethod
    def plagiarism_rate(code1, code2) -> float:
        '''calculationg the plagiarism rate'''
        lev_coef = Code.levenshtein_distance(
            code1, code2) / max(len(code1.structure), len(code2.structure))
        return round(1 - lev_coef, 2)


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
