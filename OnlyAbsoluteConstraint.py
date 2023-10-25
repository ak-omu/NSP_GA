# 絶対制約条件のみを考慮した遺伝的アルゴリズム
import numpy
import re
import copy

NGEN = 10  # 世代数
NPOP = 10  # 個体数
NURSE = 24  # ナース数
TERM = 30  # 期間
STYPE = 4
SKILL_VALUE_WEIGHT = 1 / 20


gen_cur = []
gen_next = []

# generate
for i in range(NPOP):
    roster = []
    for n in range(NURSE):
        days = []
        for d in range(TERM):
            shift = []
            r = numpy.random.randint(0, 24)
            for s in range(STYPE):
                if r < 8:
                    ss = 0
                elif r < 18:
                    ss = 1
                elif r < 21:
                    ss = 2
                elif r < 24:
                    ss = 3

                if s == ss:
                    shift.append(True)
                else:
                    shift.append(False)
            days.append(shift)
        roster.append(days)
    gen_cur.append(roster)

gen_cur = numpy.array(gen_cur)


# evaluate
def evaluate(generation):
    evvalues = []
    # allnpms = []
    indvvsums = []
    forbidden_pattern = ["111111", "333", "21", "23", "203"]
    sklvalues = [
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

    for i in range(NPOP):
        npms = []
        vpm = 0  # 人数違反
        vs = 0  # スキル値違反
        vt = 0  # 回数違反
        vfp = 0  # 禁止パターン
        for d in range(TERM):
            mod_nurses = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            exskl = [0, 0, 0]
            for n in range(NURSE):
                for s in range(1, STYPE):
                    mod_nurses[n % 3][s - 1] += generation[i][n][d][s]
                    exskl[s - 1] += generation[i][n][d][s] * sklvalues[n]

            npms.append(mod_nurses)

            # モジュール人数制約
            for m in mod_nurses:
                if m[0] < 3:
                    vpm += abs(m[0] - 3)
                vpm += abs(m[1] - 1) + abs(m[1] - 1)

            # 日勤10人制約
            vpm += abs(numpy.sum(numpy.array(mod_nurses), axis=0)[0] - 10)

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
        cml = 0
        for n in range(NURSE):
            wline = ""
            for d in range(1, TERM):
                wline += str(numpy.where(generation[i][n][d] == True)[0][0])
            for p in forbidden_pattern:
                tml = re.findall(p, wline)
                cml += len(tml)

        evvalues.append([vpm, vs, vt, cml])
        indvvsums.append(vpm + int(vs * SKILL_VALUE_WEIGHT) + vt + cml)
        # allnpms.append(npms)
    result = [indvvsums, evvalues]
    return result


out = evaluate(copy.deepcopy(gen_cur))
print(out[0])
