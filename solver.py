import definition as df
import util as util
import exception as exception
import re
import copy
import view
import numpy as np
import itertools as it


# ソルバー
class Solver:
    def __init__(self, quest, threshold):
        # 解の個数の閾値
        self.threshold = threshold
        # 解の個数
        self.result_count = 0
        # 空盤面候補数
        self.values = dict((s, df.NUMERIC) for s in df.SQUARE)

        # 描画
        # self.v = view.View()

        # 問題のセット
        for s, d in zip(df.SQUARE, quest):
            if d in df.NUMERIC and not self.assign(self.values, s, d):
                raise exception.NonAnswerException

    # マスsに値dを割り当て
    def assign(self, values, s, d):
        if all(self.propagate(values, s, other) for other in values[s].replace(d, "")):
            return values
        return False

    # 伝播(マスsから候補値dを削除+マスsのペア内にsの候補値の一つが含まれない場合他の候補値を削除)
    def propagate(self, values, s, d):
        if d not in values[s]:
            # self.v.update(self.values)
            return values

        values[s] = values[s].replace(d, "")
        if len(values[s]) == 0:
            return False

        if len(values[s]) == 1:
            conf = values[s]
            # self.v.update(self.values)
            if not all(self.propagate(values, other, conf) for other in df.PEERS[s]):
                return False

        for u in df.UNITS[s]:
            other_d = [other for other in u if d in values[other]]
            if len(other_d) == 0:
                return False

            if len(other_d) == 1:
                if not self.assign(values, other_d[0], d):
                    return False
        return values

    # サブグループ除外
    def remove_by_subgroup(self, values):
        for i in range(54):
            sub = df.SUB_GROUP[i]
            sub_row_key, sub_col_key = df.SUB_GROUP_PEER[i]
            sub_row = df.SUB_GROUP[sub_row_key[0]] + df.SUB_GROUP[sub_row_key[1]]
            sub_col = df.SUB_GROUP[sub_col_key[0]] + df.SUB_GROUP[sub_col_key[1]]
            sub_cand = util.get_candidates(values, sub)
            sub_row_cand = util.get_candidates(values, sub_row)
            sub_col_cand = util.get_candidates(values, sub_col)

            target_row = [c for c in sub_cand if c not in sub_row_cand]
            target_col = [c for c in sub_cand if c not in sub_col_cand]

            if len(target_row) > 0:
                if not all(self.propagate(values, s, d) for s in sub_col for d in target_row):
                    raise exception.NonAnswerException

            if len(target_col) > 0:
                if not all(self.propagate(values, s, d) for s in sub_row for d in target_col):
                    raise exception.NonAnswerException

        return True

    def remove_by_n_association(self, values, n):
        def get_naked(s):
            cell = [t for t in s if 1 < len(values) <= n]
            if len(cell) < n:
                return True
            cells = it.combinations(cell, n)
            for c in cells:
                v = set()
                for t in c:
                    v |= set(values[t])
                if len(v) == n:
                    if not all(self.propagate(values, tg, d) for tg in s if tg in c for d in v):
                        return False
                elif len(v) < n:
                    return False
            return True

        def get_hidden(s):
            comb = util.get_combination(util.get_candidates(values, s), n)
            for c in comb:
                target = []
                for t in s:
                    if len(values[t]) > 1 and all(v in c for v in values[t]):
                        target.append(t)

                    if len(target) > n:
                        break
                else:
                    continue
                if len(target) == n:
                    for tg in target:
                        if not all(self.propagate(values, tg, o) for o in re.sub("[^{}]".format(c), "", values[tg])):
                            return False
            return True

        if not all(get_hidden(h) and get_naked(h) for h in df.HOUSES):
            raise exception.NonAnswerException

        return True

    def x_wings(self, values, n):
        rows = util.get_combination(df.ROWS, n)
        cols = util.get_combination(df.COLS, n)

        for row in rows:
            for col in cols:
                target = df.get_tetra(row, col)
                candidate = []
                for rs in df.get_tetra(row, df.COLS):
                    tv = "".join(set("".join([values[s] for s in rs if s in target])))
                    ntv = "".join(set("".join([values[s] for s in rs if s not in target])))
                    cand = set([ts for ts in tv if ts not in ntv])
                    candidate.append(cand)

                result = set(candidate[0])
                for i in range(1, len(candidate)):
                    result &= set(candidate[i])

                if len(result) >= 1:
                    for rst in result:
                        for cs in df.get_tetra(df.ROWS, col):
                            for c in cs:
                                if c not in target and rst in values[c]:
                                    if not self.remove_single(values, c, rst):
                                        raise exception.NonAnswerException

                candidate = []
                for cs in df.get_tetra(df.ROWS, col):
                    tv = "".join(set("".join([values[s] for s in cs if s in target])))
                    ntv = "".join(set("".join([values[s] for s in cs if s not in target])))
                    cand = set([ts for ts in tv if ts not in ntv])
                    candidate.append(cand)

                result = set(candidate[0])
                for i in range(1, len(candidate)):
                    result &= set(candidate[i])

                if len(result) >= 1:
                    for rst in result:
                        for rs in df.get_tetra(row, df.COLS):
                            for r in rs:
                                if r not in target and rst in values[r]:
                                    if not self.remove_single(values, r, rst):
                                        raise exception.NonAnswerException

    def brute_force(self, values):
        try:
            if values is False:
                return False

            if all(len(values[s]) == 1 for s in df.SQUARE):
                self.result_count += 1
                self.values = values
                if self.result_count == self.threshold:
                    # print("解が2個以上あります")
                    raise exception.MultipleAnswerException
                return True
            elif any(len(values[s]) == 0 for s in df.SQUARE):
                return False

            _, target = min((len(values[s]), s) for s in df.SQUARE if len(values[s]) > 1)
            result = [self.brute_force(self.assign(copy.deepcopy(values), target, d)) for d in values[target]]
            if any(result):
                return True
            else:
                return False
        except exception.MultipleAnswerException:
            raise exception.MultipleAnswerException

    def case_count(self):
        count = 1
        for s in df.SQUARE:
            count *= len(self.values[s])
        return round(np.log(float(count)) / np.log(9), 5)

    def dict_to_str(self):
        result = ""
        for s in df.SQUARE:
            result += self.values[s]

        return result


def main(q, qp, o):
    import datetime as dt
    ans = list()
    if q is not None and qp is None:
        pr = [q]
    elif qp is not None:

        with open(qp, "r") as f:
            k = f.read()
        pr = k.split("\n")
    else:
        raise Exception

    for kk in pr:
        answer = list()
        answer.append(util.to_csv(kk, str))
        answer.append(util.to_csv(kk.count("0")))
        start = dt.datetime.now()
        strategy = Solver(kk, 2)
        try:
            answer.append(util.to_csv(strategy.case_count()))
            strategy.remove_by_subgroup(strategy.values)
            answer.append(util.to_csv(strategy.case_count()))
            # for ii in range(2, 7):
            #     strategy.x_wings(strategy.values, ii)
            # answer.append(util.to_csv(str(strategy.case_count())))
            for ii in range(2, 5):
                strategy.remove_by_n_association(strategy.values, ii)
            answer.append(util.to_csv(strategy.case_count()))
            if strategy.brute_force(strategy.values):
                a = dt.datetime.now() - start
                print(a)
                print(strategy.dict_to_str())
                answer.append(util.to_csv(strategy.dict_to_str(), str))
                answer.append(util.to_csv(strategy.result_count, str))
                print(strategy.result_count)
                answer.append(util.to_csv(a.microseconds))
                ans.append(answer)

                # strategy.v.show()
            else:
                raise exception.NonAnswerException
        except exception.MultipleAnswerException:
            print("複数解あります")
        except exception.NonAnswerException:
            print("解がありません")

    with open(o + "ans_log_ans_1.csv", "w") as f:
        for a in ans:
            f.write(",".join(a))
            f.write("\n")


if __name__ == '__main__':
    main(None, "./question/ans.csv", "./answer_log/")
    # questions = "004000035010300000002000004036001409000800007070009000000000000008400350090200060"
    # main(questions, None, "./answer_log/")
