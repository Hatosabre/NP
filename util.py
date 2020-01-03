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


def to_csv(vals):
    return "'{}'".format(vals)
