import house as house
import util as util
import exception as exception
import re
import copy

h = house.House()


class Solver:
    def __init__(self):
        self.result_count = 0
        self.values = dict((s, house.NUM) for s in h.square)

    def set_quest(self, quest):
        for s, d in h.get_quest(quest).items():
            if d in house.NUM and not self.assign(self.values, s, d):
                raise exception.NonAnswerException
        return self.values

    def assign(self, values, s, d):
        if all(self.not_assign(values, s, other) for other in values[s].replace(d, "")):
            return values
        return False

    def not_assign(self, values, s, d):
        if not self.remove_single(values, s, d):
            return False
        if not self.get_single(values, s, d):
            return False
        return values

    def remove_single(self, values, s, d):
        if d not in values[s]:
            return values

        values[s] = values[s].replace(d, "")
        if len(values[s]) == 0:
            return False

        if len(values[s]) == 1:
            conf = values[s]
            if not all(self.not_assign(values, other, conf) for other in h.peers[s]):
                return False
        return values

    def get_single(self, values, s, d):
        for u in h.units[s]:
            other_d = [other for other in u if d in values[other]]
            if len(other_d) == 0:
                return False

            if len(other_d) == 1:
                if not self.assign(values, other_d[0], d):
                    return False

        return values

    def multiple_country(self, values, n):

        def get_country(target, check, counter):
            count = 0
            result = []
            flag = False
            for s in target:
                if len(values[s]) == 1:
                    continue
                ln = [cck for cck in check if cck in values[s]]
                if len(ln) > 0 and len(values[s]) > 1:
                    count += 1
                    result.append(s)
                    if len(ln) == counter:
                        flag = True

                if count > counter:
                    return
            if count < counter or not flag:
                return
            for s in target:
                if s in result:
                    if not all(self.not_assign(values, s, other) for other in re.sub('[{}]'.format(check), "", values[s])):
                        raise exception.NonAnswerException
                else:
                    if not all(self.not_assign(values, s, other) for other in re.sub('[^{}]'.format(check), "", values[s])):
                        raise exception.NonAnswerException
            return True

        for hl in h.house_list:
            cand = "".join(set("".join([values[s] for s in hl if len(values[s]) >= n])))
            checker = util.get_combination(cand, n)
            for c in checker:
                try:
                    get_country(hl, c, n)
                except exception.NonAnswerException:
                    return False
        return True

    def remove_multiple(self, values):
        for c in (house.NUM1, house.NUM2, house.NUM3):
            for r in (house.ALP1, house.ALP2, house.ALP3):
                for r_in in r:
                    focus = [r_in + fc for fc in c]
                    other = [r_in + fc for fc in house.NUM.replace(c, "")]
                    focus_cand = "".join(set("".join([values[s] for s in focus])))
                    other_cand = "".join(set("".join([values[s] for s in other])))
                    cand = [cn for cn in focus_cand if cn not in other_cand]
                    if len(cand) > 0:
                        target = [fr + fc for fr in r.replace(r_in, "") for fc in c]
                        for cn in cand:
                            for t in target:
                                if not self.not_assign(values, t, cn):
                                    raise exception.NonAnswerException

                    focus = [r_in + fc for fc in c]
                    other = [fr + fc for fr in r.replace(r_in, "") for fc in c]
                    focus_cand = "".join(set("".join([values[s] for s in focus])))
                    other_cand = "".join(set("".join([values[s] for s in other])))
                    cand = [cn for cn in focus_cand if cn not in other_cand]
                    if len(cand) > 0:
                        target = [r_in + fc for fc in house.NUM.replace(c, "")]
                        for cn in cand:
                            for t in target:
                                if not self.not_assign(values, t, cn):
                                    raise exception.NonAnswerException

        for r in (house.ALP1, house.ALP2, house.ALP3):
            for c in (house.NUM1, house.NUM2, house.NUM3):
                for c_in in c:
                    focus = [fr + c_in for fr in r]
                    other = [fr + c_in for fr in house.ROWS.replace(r, "")]
                    focus_cand = "".join(set("".join([values[s] for s in focus])))
                    other_cand = "".join(set("".join([values[s] for s in other])))
                    cand = [cn for cn in focus_cand if cn not in other_cand]
                    if len(cand) > 0:
                        target = [fr + fc for fr in r for fc in c.replace(c_in, "")]
                        for cn in cand:
                            for t in target:
                                if not self.not_assign(values, t, cn):
                                    raise exception.NonAnswerException

                    focus = [fr + c_in for fr in r]
                    other = [fr + fc for fr in r for fc in c.replace(c_in, "")]
                    focus_cand = "".join(set("".join([values[s] for s in focus])))
                    other_cand = "".join(set("".join([values[s] for s in other])))
                    cand = [cn for cn in focus_cand if cn not in other_cand]
                    if len(cand) > 0:
                        target = [fr + c_in for fr in house.ROWS.replace(r, "")]
                        for cn in cand:
                            for t in target:
                                if not self.not_assign(values, t, cn):
                                    raise exception.NonAnswerException

    def x_wings(self, values, n):
        rows = h.get_combination(house.ROWS, n)
        cols = h.get_combination(house.COLS, n)

        for row in rows:
            for col in cols:
                target = h.get_tetra(row, col)
                candidate = []
                for rs in h.get_rows(row):
                    tv = "".join(set("".join([values[s] for s in rs if s in target])))
                    ntv = "".join(set("".join([values[s] for s in rs if s not in target])))
                    cand = set([ts for ts in tv if ts not in ntv])
                    candidate.append(cand)

                result = set(candidate[0])
                for i in range(1, len(candidate)):
                    result &= set(candidate[i])

                if len(result) >= 1:
                    for rst in result:
                        for cs in h.get_cols(col):
                            for c in cs:
                                if c not in target and rst in values[c]:
                                    if not self.remove_single(values, c, rst):
                                        raise exception.NonAnswerException

                candidate = []
                for cs in h.get_cols(col):
                    tv = "".join(set("".join([values[s] for s in cs if s in target])))
                    ntv = "".join(set("".join([values[s] for s in cs if s not in target])))
                    cand = set([ts for ts in tv if ts not in ntv])
                    candidate.append(cand)

                result = set(candidate[0])
                for i in range(1, len(candidate)):
                    result &= set(candidate[i])

                if len(result) >= 1:
                    for rst in result:
                        for rs in h.get_rows(row):
                            for r in rs:
                                if r not in target and rst in values[r]:
                                    if not self.remove_single(values, r, rst):
                                        raise exception.NonAnswerException

    def brute_force(self, values):
        try:
            if values is False:
                return False

            if all(len(values[s]) == 1 for s in h.square):
                self.result_count += 1
                self.values = values
                if self.result_count == 2:
                    # print("解が2個以上あります")
                    raise exception.MultipleAnswerException
                return True

            _, target = min((len(values[s]), s) for s in h.square if len(values[s]) > 1)
            result = [self.brute_force(self.assign(copy.deepcopy(values), target, d)) for d in values[target]]
            if any(result):
                return True
            else:
                return False
        except exception.MultipleAnswerException:
            raise exception.MultipleAnswerException

    def case_count(self):
        count = 1
        for s in h.square:
            count *= len(self.values[s])

        return count

    def dict_to_str(self):
        result = ""
        for s in h.square:
            result += self.values[s]

        return result


if __name__ == '__main__':
    import datetime as dt

    ans = list()
    with open("./question/ans.csv", "r") as f:
        k = f.read()
    pr = k.split("\n")
    # pr = ["002030000390658000700001000000070893500100020020000000050000480000710036000080205"]
    for kk in pr:
        answer = list()
        answer.append(util.to_csv(kk))
        answer.append(util.to_csv(str(9 ** (kk.count("0")))))
        start = dt.datetime.now()
        strategy = Solver()
        try:
            strategy.set_quest(kk)
            answer.append(util.to_csv(str(strategy.case_count())))
            strategy.remove_multiple(strategy.values)
            answer.append(util.to_csv(str(strategy.case_count())))
            # for ii in range(2, 7):
            #     strategy.x_wings(strategy.values, ii)
            # answer.append(util.to_csv(str(strategy.case_count())))
            for ii in range(2, 5):
                strategy.multiple_country(strategy.values, ii)
            answer.append(util.to_csv(str(strategy.case_count())))
            if strategy.brute_force(strategy.values):
                a = dt.datetime.now() - start
                print(a)
                answer.append(util.to_csv(strategy.dict_to_str()))
                answer.append(util.to_csv(str(a.microseconds)))
                ans.append(answer)
            else:
                raise exception.NonAnswerException
        except exception.MultipleAnswerException as e:
            print("複数解あります")
        except exception.NonAnswerException as e:
            print("解がありません")
    print(ans)
    with open("./answer_log/ans_log.csv", "w") as f:
        for a in ans:
            f.write(",".join(a))
            f.write("\n")
