#!/usr/bin/env python3
import collections
import dataclasses
import itertools
import random
import sys
from pprint import pprint

from beautifultable import BeautifulTable

DIE_FACES = 10

BOTCH = "BOTCH"
EXACT = "EXACT"
FAIL = 0
Max_Pool = 7
min_difficulty = 3
max_difficulty = DIE_FACES
difficulty_band = list(range(min_difficulty, max_difficulty))


def reverse_cumulative_sum(seq):
    return reversed(
        list(
            itertools.accumulate(
                reversed(seq)
            )))


def eval_roll(dice, difficulty):
    ones = dice.count(1)
    above_diff = len([die for die in dice if die >= difficulty])
    if ones > 0 and above_diff == 0:
        return BOTCH
    success = max(above_diff - ones, 0)
    return success


def eval_for_all_difficulties(rolled_pool):
    return {difficulty: eval_roll(rolled_pool, difficulty)
            for difficulty
            in difficulty_band}


def pool_generator(pool_size, n):
    if n == EXACT:
        return all_pools_generator(pool_size)
    else:
        return random_pool_generator(pool_size, n)


def random_pool_generator(pool_size, n):
    """
    yields n dice pool results, of size p, evaluated for all difficulties
    """
    def roll(pool_size):
        """
        Generates a single roll of a pool of D10s
        """
        dice = [random.randint(1, DIE_FACES) for _ in range(pool_size)]
        reroll10s(dice)
        return dice

    def reroll10s(dice):
        tens = dice.count(DIE_FACES)
        if (tens):
            dice.extend([d for d in roll(tens) if d > 1])

    for x in range(n):
        yield eval_for_all_difficulties(roll(pool_size))


def all_pools_generator(pool_size):
    """
    yield all dice pool results, of size p, evaluated for all difficulys
    """
    for roll in itertools.product(range(1, DIE_FACES + 1), repeat=pool_size):
        yield eval_for_all_difficulties(roll)


@dataclasses.dataclass
class QuickStats:
    pool: int = 0
    difficulty_target: int = 3
    expected_successes: float = 0.0
    fail_chance: float = 0.0
    botch_chance: float = 0.0

    quicktable = {p: {d: None for d in difficulty_band} for p in range(1, Max_Pool + 1)}

    def __post_init__(self):
        self.quicktable[self.pool][self.difficulty_target] = self

    def __str__(self):
        return f"S#:{self.expected_successes:>5.2F}\nS%:{100 - self.fail_chance:>5.2F}\nB%:{self.botch_chance:>5.2F}"


@dataclasses.dataclass
class PoolStats:
    difficulty_target: int
    result_counter: collections.Counter = dataclasses.field(default_factory=collections.Counter)
    botch_count = 0

    def add_result(self, result):
        if result == BOTCH:
            self.botch_count += 1
            result = 0
        self.result_counter[result] += 1

    def calculate(self):
        total = self.result_counter.total()
        max_result = max(self.result_counter.keys())
        average = sum(result * count for result, count in self.result_counter.items()) / total
        factor = (100.0 / total)
        chance_per_num_success = [self.result_counter[result] * factor for result in range(1, max_result + 1)]
        botch_percent = self.botch_count * factor
        fail_percent = self.result_counter[FAIL] * factor
        cumulative_chance = reverse_cumulative_sum(chance_per_num_success)
        return average, chance_per_num_success, cumulative_chance, botch_percent, fail_percent, max_result


def munch(evaled_pool_iter):
    chance_per_num_success_dif = {diff: PoolStats(diff) for diff in difficulty_band}
    for evaled_pool in evaled_pool_iter:
        for diff, result in evaled_pool.items():
            chance_per_num_success_dif[diff].add_result(result)
    return chance_per_num_success_dif.values()


def print_pool_stats(pool_stats, pool_size):
    average, chance_per_num_success, cumulative_chance, botch_percent, fail_percent, max_result = pool_stats.calculate()
    QuickStats(pool_size, pool_stats.difficulty_target, average, fail_percent, botch_percent)

    print(f"Pool : {pool_size:>2d}    Difficulty : {pool_stats.difficulty_target:>2d}")
    print(f"successes  :{''.join(f'{i:>7d}' for i in range(1, max_result + 1))}")
    print(f"chance    %:{''.join(f'{x:>7.2F}' for x in chance_per_num_success)}")
    print(f"cum chance%:{''.join(f'{x:>7.2F}' for x in cumulative_chance)}")
    print(f"Fail: {fail_percent:>5.2F}\tBotch: {botch_percent:>5.2F}\tavg: {average:>5.2F}")
    print('\n')


def print_pool(pool_stats_generator, pool_size):
    for pool_stats in pool_stats_generator:
        print_pool_stats(pool_stats, pool_size)
        sys.stdout.flush()


def print_all(highpool, n):
    for pool_size in range(1, highpool + 1):
        pool_stats_generator = munch(pool_generator(pool_size, EXACT))
        print_pool(pool_stats_generator, pool_size)
        print("++++++++++++++++++++++++++++++++++++++++")


def print_summary(quicktable):
    print("QuickTable:")
    table = BeautifulTable(maxwidth=100, default_alignment=BeautifulTable.ALIGN_LEFT)
    table.set_style(BeautifulTable.STYLE_DEFAULT)
    for p, row in quicktable.items():
        table.rows.append(list(row.values()), header=f"Pool {p}")
    table.columns.header = [f"diff {d}" for d in difficulty_band]
    print(table)


if __name__ == '__main__':
    print_all(Max_Pool, BOTCH)
    print_summary(QuickStats.quicktable)
