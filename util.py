def get_candidates(values, sites):
    return "".join(set("".join(values[s] for s in sites if len(values[s]) > 1)))


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


def get_empty_cell_combination(values, sites, threshold=2):
    import itertools as it
    return it.combinations([s for s in sites if len(values[s]) >= threshold], threshold)


def get_links(values):
    pass


def to_csv(vals, typ=float):
    if typ is str:
        return "'{}'".format(vals)
    if typ is float:
        return str(vals)
