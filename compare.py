import argparse
import ast
import numpy as np


def levenshtein_distance(s1: str, s2: str) -> int:
    dp = np.zeros((len(s1) + 1, len(s2) + 1))
    for i in range(len(s1) + 1):
        for j in range(len(s2) + 1):
            if i == 0 or j == 0:
                dp[i][j] = max(i, j)
            else:
                dp[i][j] = min(dp[i][j - 1] + 1, dp[i - 1][j] + 1,
                               dp[i - 1][j - 1] + (1 if s1[i - 1] == s2[j - 1]
                               else 0))
    return dp[-1][-1]


class CodeTransformer(ast.NodeTransformer):
    def visit_arg(self, node):
        return ast.arg(**{**node.__dict__, 'arg': 'a'})

    def visit_Name(self, node):
        return ast.Name(**{**node.__dict__, 'id': 'n'})

    def visit_Import(self, node):
        return None


def plagiarism_rate(code1: str, code2: str) -> float:
    code1 = ast.unparse(CodeTransformer().visit(ast.parse(code1)))
    code2 = ast.unparse(CodeTransformer().visit(ast.parse(code2)))
    return round(1 - levenshtein_distance(code1, code2) / max(len(code1), len(code2)), 2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('scores')
    args = parser.parse_args()
    with open(args.input, 'r') as fin:
        with open(args.scores, 'w') as fout:
            for line in fin:
                check1, check2 = line.split()
                s1, s2 = '', ''
                with open(check1, 'r') as f1:
                    s1 = f1.read()
                with open(check2, 'r') as f2:
                    s2 = f2.read()
                fout.write(str(plagiarism_rate(s1, s2)) + '\n')
