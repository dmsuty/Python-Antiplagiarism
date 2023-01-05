import argparse
import numpy as np
import re


def levenshtein_distance(s1: str, s2: str) -> int:
    s1, s2 = normalize(s1), normalize(s2)
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


def normalize(code: str) -> str:
    code = re.sub(r'"""[\s\S]*?"""', '', code)
    code = re.sub(r"'''[\s\S]*?'''", '', code)
    code = re.sub(r'#[\s\S]*?\n', '', code)
    code = re.sub(r' *\n', '\n', code)
    code = re.sub(r'(\n)*', '\n', code)
    return code


def plagiarism_rate(code1: str, code2: str) -> float:
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
