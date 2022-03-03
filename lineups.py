import itertools


def unique_subsets(subsets):
    cleaned_subsets = []
    for combination in subsets:
        if combination not in cleaned_subsets:
            cleaned_subsets.append(combination)
    return cleaned_subsets


def calc_lineups(players, max_total):
    subsets = []
    for L in range(0, len(players) + 1):
        for subset in itertools.combinations(players, 5):
            subset = sorted(list(subset), reverse=True)
            if sum(subset) == max_total:
                subsets.append(subset)
    cleaned_subsets = unique_subsets(subsets)
    return cleaned_subsets


def main():
    skill_levels = [6, 3, 3, 4, 5, 5, 6, 2]
    max_skill_level_totals = range(23, 0, -1)
    for skill_total in max_skill_level_totals:
        lineups = calc_lineups(skill_levels, skill_total)
        if len(lineups) > 0:
            print("Combinations of", skill_total)
            for lineup in lineups:
                print(lineup)


if __name__ == '__main__':
    main()
