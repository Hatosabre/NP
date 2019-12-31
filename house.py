NUM1, NUM2, NUM3 = ("123", "456", "789")
NUM = NUM1 + NUM2 + NUM3
COLS = NUM
ALP1, ALP2, ALP3 = ("ABC", "DEF", "GHI")
ROWS = ALP1 + ALP2 + ALP3


class House:
    def __init__(self):
        self.square = self.get_tetra(ROWS, COLS)
        self.rows_house = self.get_rows(ROWS)
        self.cols_house = self.get_cols(COLS)
        self.boxes_house = self.get_boxes((ALP1, ALP2, ALP3), (NUM1, NUM2, NUM3))
        self.house_list = self.rows_house + self.cols_house + self.boxes_house
        self.units = dict((s, [u for u in self.house_list if s in u]) for s in self.square)
        self.peers = dict((s, set(sum(self.units[s], [])) - {s}) for s in self.square)

    @staticmethod
    def get_tetra(vertical, side):
        return [v + s for v in vertical for s in side]

    def get_rows(self, vertical):
        return [self.get_tetra(r, COLS) for r in vertical]

    def get_cols(self, side):
        return [self.get_tetra(ROWS, c) for c in side]

    def get_boxes(self, vertical, side):
        return [self.get_tetra(br, bc) for br in vertical for bc in side]

    def get_quest(self, quest):
        return dict(zip(self.square, quest))

    @staticmethod
    def get_combination(string, n):
        values = []

        def for_combination(m, back_index=-1, value=""):
            if m <= 0:
                values.append(value)
                return

            for j in range(back_index + 1, len(string) - (m - 1)):
                value += string[j]
                for_combination(m - 1, j, value)
                value = value.replace(string[j], "")

        for_combination(n)

        return values




