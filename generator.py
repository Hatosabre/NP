import house as house
import solver as st
import random

h = house.House()


class Generator:
    def __init__(self):
        self.quest = dict()
        self.count = 0
        self.num = []
        self.rank = dict()
        self.next = 0
        rank = list(range(81))
        for s in h.square:
            i = random.choice(rank)
            self.rank[i] = s
            rank.remove(i)
            self.quest[s] = "0"

    def fill(self):
        for i in range(81):
            if not self.update(i):
                return False
            else:
                if self.count >= 17 and len(self.num) >= 8:
                    return True

    def update(self, now):
        self.next = now + 1
        s = self.rank[now]
        not_cand = "".join(set("".join(self.quest[o] for o in h.peers[s])))
        cand = [n for n in house.NUM if n not in not_cand]
        if len(cand) == 0:
            return False
        i = random.choice(cand)
        if i not in self.num:
            self.num.append(i)
        self.count += 1
        self.quest[s] = i
        return True

    def get_str(self):
        result = "".join(self.quest[s] for s in h.square)
        return result


ans = list()
while True:
    g = Generator()
    g.fill()
    while True:
        strategy = st.Solver()
        if not strategy.set_quest(g.get_str()):
            break
        for c in range(2, 5):
            strategy.multiple_country(strategy.values, c)

        try:
            if not strategy.brute_force(strategy.values):
                # print("解なし")
                break
            else:
                ans.append(g.get_str())
                print(g.get_str())
                break
        except Exception:
            g.update(g.next)
            continue

    if len(ans) == 1000000:
        break

with open("./question/ans.csv", "w") as f:
    f.write("\n".join(ans))
