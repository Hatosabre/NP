import house as house
from house import House as H
import solver as st
import exception
import random

h = H()


class Generator:
    def __init__(self):

        # 問題(Dict型)
        self.quest = dict()

        # 埋まっているマスの個数
        self.next = 0
        # 埋まっている数字の種類数
        self.num = []

        # 問題を作成する上での、埋めるマスの順番
        self.rank = dict()

        # ランダムに各マスに順位付けを行う
        rank = list(range(81))
        for s in h.square:
            i = random.choice(rank)
            self.rank[i] = s
            rank.remove(i)
            self.quest[s] = "0"

    # ランダムに決めたランク通りに数字を埋めていく
    def fill(self):
        for i in range(81):

            # マスを埋める
            if not self.update():
                # 埋められるものがなくなった場合リセット
                return False
            else:
                # 最低基準が満たされた場合解が1つか確かめる
                if self.next >= 17 and len(self.num) >= 8:
                    return True

    # 解が一つより多かった場合追加でマスを埋める
    def update(self):
        # 次の順位のマスを取得
        s = self.rank[self.next]

        # 埋められない数字を取得
        not_cand = "".join(set("".join(self.quest[o] for o in h.peers[s])))

        # 埋められる数字を取得
        cand = [n for n in house.NUM if n not in not_cand]

        # 埋められる数字がなければ、リセットする
        if len(cand) == 0:
            return False

        # 埋められる数字の中で、ランダムで取得
        i = random.choice(cand)

        # 既に埋まっている数字の種類に入っていなければ追加
        if i not in self.num:
            self.num.append(i)

        # マスに数字を埋める
        self.quest[s] = i

        # 次の順位に進める
        self.next += 1
        return True

    # 81マス形式にする
    def get_str(self):
        result = "".join(self.quest[s] for s in h.square)
        return result


# 問題の生成
def main(c, n, o):
    """:parameter c 解の個数の閾値
       :parameter n 問題の個数
       :parameter o 出力先パス
    """
    # 問題をリスト
    ans = list()
    while True:
        # 問題生成クラス
        g = Generator()

        # 最低基準まで入力
        if not g.fill():
            continue

        while True:
            try:
                # ソルバークラス
                s = st.Solver(c)

                # 生成された問題をセット
                s.set_quest(g.get_str())
                for c in range(2, 5):
                    # N国同盟
                    s.multiple_country(s.values, c)

                # 探索
                if not s.brute_force(s.values):
                    raise exception.NonAnswerException
                else:
                    ans.append(g.get_str())
                    print(g.get_str())
                    break
            except exception.NonAnswerException:
                break
            except exception.MultipleAnswerException:
                # 解が複数ある場合は追加で埋める
                if g.update():
                    continue
                else:
                    break

        if len(ans) == n:
            break
    print(ans)
    with open("./question/{}.csv".format(o), "a") as f:
        f.write("\n".join(ans))


if __name__ == '__main__':
    main(4, 20000, "ans")
