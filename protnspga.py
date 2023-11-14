# 絶対制約条件のみを考慮した遺伝的アルゴリズム
import numpy
import re
import copy
import itertools
import time

NGEN = 10  # 世代数
NPOP = 100  # 個体数
NURSE = 24  # ナース数
TERM = 30  # 期間
STYPE = 5  # 勤務種類数
LEVELS = 5  # レベル数
SKILL_VALUE_WEIGHT = 1 / 20

numpy.set_printoptions(threshold=2 * 30 * 24 * 4)
rng = numpy.random.default_rng()

sklvalues = numpy.array(
    [
        50,
        50,
        50,
        30,
        30,
        30,
        30,
        10,
        10,
        10,
        10,
        10,
        10,
        10,
        10,
        8,
        8,
        8,
        8,
        8,
        5,
        5,
        5,
        5,
    ]
)

# pregenerate
ini_roster = numpy.full((TERM, NURSE, STYPE), False)
ini_fix = numpy.full((TERM, NURSE, LEVELS), True)
status_cur = numpy.full((NPOP, TERM, NURSE, LEVELS), True)
# 研修10 休み11 日勤11 準夜1 深夜2
ini_set = numpy.array([*[4] * 10, *[0] * 11, *[1] * 11, *[2] * 1, *[3] * 2])
n_rand = rng.choice(24, 35)
d_rand = rng.choice(30, 35)
lfix = []
for i in range(35):
    r = rng.integers(ini_set.size)
    ini_roster[d_rand[i]][n_rand[i]][ini_set[r]] = True
    ini_fix[d_rand[i]][n_rand[i]][0] = False
    ini_set = numpy.delete(ini_set, r)
    lfix.append([d_rand[i], n_rand[i]])
status_cur[:] = ini_fix
nfix = numpy.array(lfix)

gen_cur = numpy.full((NPOP, TERM, NURSE, STYPE), False)
gen_cur[:] = ini_roster
print(status_cur[0])


index_nurse_origin = numpy.arange(NURSE)
index_day_origin = numpy.arange(TERM)

s_night = set()
s_daytime = set()

for i in itertools.combinations(sklvalues, 3):
    if sum(i) >= 39:
        s_night.add(i)
for i in itertools.combinations(sklvalues, 10):
    if sum(i) >= 130:
        s_daytime.add(i)


def search(s_target, rv):
    result = set()
    for s in s_target:
        if rv in s:
            l = list(s)
            l.remove(rv)
            result.add(tuple(l))
    if not result:
        pass
    else:
        s_target.clear()
        s_target.update(result)
    return set(itertools.chain.from_iterable(result))


gsttime = time.perf_counter()
# generate
for i in range(NPOP):
    index_day_random = rng.permutation(index_day_origin)
    while index_day_random.size != 0:
        d = index_day_random[0]

        flag = True
        while flag:
            index_nurse_random = rng.permutation(index_nurse_origin)
            exshift = numpy.full((NURSE, STYPE), False)

            exc_nurse_index = numpy.where(d_rand == d)[0]
            exc_nl_day = numpy.empty(0, dtype=numpy.int64)
            exc_nl_pnight = numpy.empty(0, dtype=numpy.int64)
            exc_nl_mnight = numpy.empty(0, dtype=numpy.int64)
            for eni in exc_nurse_index:
                if 1 in numpy.where(ini_roster[d][n_rand[eni]] == True)[0]:
                    exc_nl_day = numpy.append(exc_nl_day, n_rand[eni])
                elif 2 in numpy.where(ini_roster[d][n_rand[eni]] == True)[0]:
                    exc_nl_pnight = numpy.append(exc_nl_pnight, n_rand[eni])
                elif 3 in numpy.where(ini_roster[d][n_rand[eni]] == True)[0]:
                    exc_nl_mnight = numpy.append(exc_nl_mnight, n_rand[eni])
                elif 0 in numpy.where(ini_roster[d][n_rand[eni]] == True)[0]:
                    exshift[n_rand[eni]][0] = True
                elif 4 in numpy.where(ini_roster[d][n_rand[eni]] == True)[0]:
                    exshift[n_rand[eni]][4] = True
                index_nurse_random = numpy.delete(
                    index_nurse_random, numpy.where(index_nurse_random == n_rand[eni])
                )

            count, limit = 0, 0
            while count < 3:
                n = index_nurse_random[limit]
                if count == 0:
                    temp = numpy.empty(0, dtype=numpy.int64)
                    inst_s_night = copy.deepcopy(s_night)
                    remaining_set = set(itertools.chain.from_iterable(inst_s_night))
                    mods = numpy.arange(3)
                    for enl in exc_nl_pnight:
                        remaining_set = search(inst_s_night, sklvalues[enl])
                        mods = numpy.setdiff1d(mods, enl % 3)
                        temp = numpy.append(temp, enl)
                        count += 1

                if sklvalues[n] in remaining_set and n % 3 in mods:
                    temp = numpy.append(temp, n)
                    remaining_set = search(inst_s_night, sklvalues[n])
                    index_nurse_random = numpy.delete(
                        index_nurse_random, numpy.where(index_nurse_random == n)
                    )
                    mods = numpy.setdiff1d(mods, n % 3)
                    limit = 0
                    count += 1
                    if count == 3:
                        for tn in temp:
                            exshift[tn][2] = True
                else:
                    limit += 1
                    if index_nurse_random.size == limit:
                        index_nurse_random = numpy.append(index_nurse_random, temp)
                        count, limit = 0, 0

            count, limit = 0, 0
            while count < 3:
                n = index_nurse_random[limit]
                if count == 0:
                    temp = numpy.empty(0, dtype=numpy.int64)
                    inst_s_night = copy.deepcopy(s_night)
                    remaining_set = set(itertools.chain.from_iterable(inst_s_night))
                    mods = numpy.arange(3)
                    for enl in exc_nl_mnight:
                        remaining_set = search(inst_s_night, sklvalues[enl])
                        mods = numpy.setdiff1d(mods, enl % 3)
                        temp = numpy.append(temp, enl)
                        count += 1
                if sklvalues[n] in remaining_set and n % 3 in mods:
                    temp = numpy.append(temp, n)
                    remaining_set = search(inst_s_night, sklvalues[n])
                    index_nurse_random = numpy.delete(
                        index_nurse_random, numpy.where(index_nurse_random == n)
                    )
                    mods = numpy.setdiff1d(mods, n % 3)
                    limit = 0
                    count += 1
                    if count == 3:
                        for tn in temp:
                            exshift[tn][3] = True
                else:
                    limit += 1
                    if index_nurse_random.size == limit:
                        index_nurse_random = numpy.append(index_nurse_random, temp)
                        count, limit = 0, 0

            count, limit, loops = 0, 0, 0
            while count < 10 and loops < 10:
                n = index_nurse_random[limit]
                if count == 0:
                    temp = numpy.empty(0, dtype=numpy.int64)
                    inst_s_daytime = copy.deepcopy(s_daytime)
                    remaining_set = set(itertools.chain.from_iterable(inst_s_daytime))
                    lmods = numpy.array([0, 1, 2] * 3)
                    for enl in exc_nl_day:
                        remaining_set = search(inst_s_daytime, sklvalues[enl])
                        lmods = numpy.delete(lmods, numpy.where(lmods == enl % 3)[0][0])
                        temp = numpy.append(temp, enl)
                        count += 1
                    loops += 1
                if sklvalues[n] in remaining_set and (n % 3 in lmods or count == 9):
                    temp = numpy.append(temp, n)
                    remaining_set = search(inst_s_daytime, sklvalues[n])
                    index_nurse_random = numpy.delete(
                        index_nurse_random, numpy.where(index_nurse_random == n)
                    )
                    count += 1
                    if count != 10:
                        lmods = numpy.delete(lmods, numpy.where(lmods == n % 3)[0][0])
                        limit = 0
                    else:
                        for tn in temp:
                            exshift[tn][1] = True
                        flag = False
                else:
                    limit += 1
                    if index_nurse_random.size == limit:
                        index_nurse_random = numpy.append(index_nurse_random, temp)
                        index_nurse_random = rng.permutation(index_nurse_random)
                        count, limit = 0, 0

        while index_nurse_random.size != 0:
            n = index_nurse_random[0]
            exshift[n][0] = True
            index_nurse_random = numpy.delete(
                index_nurse_random, numpy.where(index_nurse_random == n)
            )

        gen_cur[i][d] = exshift

        index_day_random = numpy.delete(
            index_day_random, numpy.where(index_day_random == d)
        )

gtime = time.perf_counter() - gsttime
print(numpy.sum(numpy.sum(numpy.array(gen_cur[:][:]), axis=0)))


# evaluate
def evaluate(generation):
    evvalues = []
    # allnpms = []
    indvvsums = []
    forbidden_3pattern = ["111111", "333", "21", "23", "203"]
    forbidden_2pattern = ["11111", "32", "31", "22", "21", "23", "20"]

    for i in range(NPOP):
        npms = []
        vpm = 0  # 人数違反
        vs = 0  # スキル値違反
        vt = 0  # 回数違反
        vfp = 0  # 禁止パターン
        for d in range(TERM):
            mod_nurses = numpy.zeros((3, STYPE - 1), dtype=numpy.int64)
            exskl = numpy.zeros(STYPE - 1, dtype=numpy.int64)
            for n in range(NURSE):
                for s in range(1, STYPE):
                    mod_nurses[n % 3][s - 1] += generation[i][d][n][s]
                    exskl[s - 1] += generation[i][d][n][s] * sklvalues[n]

            npms.append(mod_nurses)

            # モジュール人数制約
            for m in mod_nurses:
                if m[0] < 3:
                    vpm += abs(m[0] - 3)
                vpm += abs(m[1] - 1) + abs(m[1] - 1)

            # 日勤10人制約
            exdaysum = numpy.sum(mod_nurses, axis=0)[0]
            if exdaysum < 10:
                vpm += abs(exdaysum - 10)

            # スキル値制約
            if exskl[0] < 130:
                vs += abs(exskl[0] - 130)
            if exskl[1] < 39:
                vs += abs(exskl[0] - 39)
            if exskl[2] < 39:
                vs += abs(exskl[0] - 39)

        # 勤務回数制約
        worktimes = numpy.sum(generation[i], axis=1)
        # 3交代
        for wt in worktimes:
            if wt[1] < 5:
                vt += abs(wt[1] - 5)
            elif wt[1] > 15:
                vt += wt[1] - 15
            sumnwt = 0
            for nw in range(2, 4):
                if wt[nw] < 2:
                    vt += abs(wt[nw] - 2)
                elif wt[nw] > 7:
                    vt += wt[nw] - 7
                sumnwt += wt[nw]
            if sumnwt < 5:
                vt += abs(sumnwt - 5)
            elif sumnwt > 9:
                vt += sumnwt - 9

        # 禁止勤務パターン制約
        for n in range(NURSE):
            wline = ""
            for d in range(1, TERM):
                wline += str(numpy.where(generation[i][d][n] == True)[0][0])
            for p in forbidden_3pattern:
                tml = re.findall(p, wline)
                vfp += len(tml)

        evvalues.append([vpm, vs, vt, vfp])
        indvvsums.append(vpm + int(vs * SKILL_VALUE_WEIGHT) + vt + vfp)
        # allnpms.append(npms)
    result = [indvvsums, evvalues]
    return result


# crossover
# def crossover(generation):


out = evaluate(copy.deepcopy(gen_cur))
print(numpy.array(out[0]))
# print(numpy.array(out[1]))
print(numpy.sum(numpy.array(out[1]), axis=0))
print(gtime)
