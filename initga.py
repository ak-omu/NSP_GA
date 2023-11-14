import numpy as np
import configparser
import itertools as it
import re
import copy
import time


class LoadSetting:
    def __init__(self, file_path="settings/command.ini") -> None:
        self.command = configparser.ConfigParser()
        self.command.optionxform = str
        self.command.read(file_path)

    def input_command(self):
        return self.command

    def input_skill_values(self):
        file_path = "settings/skill_values.txt"
        with open(file_path, "r") as f:
            skill_values = np.array([int(x) for x in f.readline().split()])
            return skill_values

    def input_shift_system(self):
        file_path = "settings/shift_systems.txt"
        with open(file_path, "r") as f:
            arr = [[int(x) for x in line.split()] for line in f]
            shift_system = np.array(arr)
            return shift_system

    def input_desire(self):
        p = self.command.getint("COMMAND", "PROBLEM")
        file_path = f"problems/desire{p}.txt"
        arr = [[0 for j in range(31)] for i in range(25)]
        with open(file_path, "r") as f:
            i = 0
            for line in f:
                data = [int(x) for x in line.split()]
                if i == 0:
                    data.insert(0, 0)
                for j in range(len(data)):
                    arr[i][j] = data[j]
                i += 1
        desire = np.array(arr)
        return desire

    def input_compatibility(self):
        p = self.command.getint("COMMAND", "PROBLEM")
        file_path = f"problems/compatibility{p}.txt"
        arr = [[0 for j in range(25)] for i in range(25)]
        with open(file_path, "r") as f:
            i = 0
            for line in f:
                data = [int(x) for x in line.split()]
                if i == 0:
                    data = [0 for x in range(25)]
                for j in range(len(data)):
                    arr[i][j] = data[j]
                i += 1
        # convert to symmetric matrix
        arr = np.array(arr)
        compatibility = arr + arr.T - np.diag(arr.diagonal())
        return compatibility

    def get_skill_set(self):
        skill_set_night = set()
        for i in it.combinations(self.input_skill_values(), 3):
            if sum(i) >= 39:
                skill_set_night.add(i)
        skill_set_day = set()
        for i in it.combinations(self.input_skill_values(), 10):
            if sum(i) >= 130:
                skill_set_day.add(i)
        return skill_set_night, skill_set_day


class CreateConfig:
    def __init__(self) -> None:
        self.ls = LoadSetting()
        self.command = self.ls.input_command()

    def create_config(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        s = self.command.getint("COMMAND", "SHIFT_SYSTEM")
        p = self.command.getint("COMMAND", "PROBLEM")
        file_path = f"configs/config{s}-{p}.ini"

        arr_desire = self.ls.input_desire()
        arr_compatibility = self.ls.input_compatibility()
        arr_skill = self.ls.input_skill_values()
        arr_shift = self.ls.input_shift_system()

        for n in range(self.command.getint("COMMAND", "NURSE")):
            config["NURSE" + str(n + 1)] = {
                "NAME": "nurse " + str(n + 1),
                "SKILL": str(arr_skill[n]),
                "2nd SHIFT": str(arr_shift[s][n] == 2),
            }
            for i in self.command["COMPATIBILITY"]:
                config.set(
                    "NURSE" + str(n + 1),
                    self.command.get("COMPATIBILITY", i),
                    str(
                        np.array(
                            [
                                j
                                for j, c in enumerate(arr_compatibility[n + 1])
                                if c == int(i) and j != 0
                            ]
                        )
                    ),
                )

            for c in self.command["DESIRE"]:
                index = np.where(arr_desire[n + 1] == int(c))[0]
                config.set(
                    "NURSE" + str(n + 1),
                    self.command.get("DESIRE", c),
                    str(index),
                )

        with open(file_path, "w") as config_file:
            config.write(config_file)


class GenInitSols:
    def __init__(self) -> None:
        self.ls = LoadSetting()
        self.skill_set_night, self.skill_set_day = self.ls.get_skill_set()
        self.rng = np.random.default_rng()

    def search_set(self, target_set: set, value: int) -> set:
        result = set()
        for t in target_set:
            if value in t:
                l = list(t)
                l.remove(value)
                result.add(tuple(l))
        if not result:
            pass
        else:
            target_set.clear()
            target_set.update(result)
        return set(it.chain.from_iterable(result))

    def generate_solution(self):
        command = self.ls.input_command()
        N = command.getint("COMMAND", "NURSE")
        T = command.getint("COMMAND", "TERM")
        P = command.getint("COMMAND", "POPULATION")
        generation = np.full((P, T, N), 0)
        arr_skill = self.ls.input_skill_values()
        nurse_index = np.arange(1, N + 1)
        day_index = np.arange(1, T + 1)
        desire = self.ls.input_desire().T
        loops = 0
        start_time = time.perf_counter()
        for p in range(P):
            s = np.delete(desire, 0, 1)
            s = np.delete(s, 0, 0)
            g = np.where((s >= 0) & (s <= 4), s, 0)
            generation[p] += g
            random_day_index = self.rng.permutation(day_index)
            while random_day_index.size > 0:
                d = random_day_index[0]
                flag = True
                while flag:
                    b = np.where((desire[d] >= 0) & (desire[d] < 10))[0] - 1
                    b = b[b >= 0]
                    a = np.delete(
                        nurse_index,
                        b,
                    )
                    random_nurse_index = self.rng.permutation(a)
                    ex_shift = np.full(N, 0)

                    count, limit = 0, 0
                    while count < 3:
                        n = random_nurse_index[limit]
                        if count == 0:
                            temp = np.empty(0, dtype=np.int32)
                            temp_night_set = copy.deepcopy(self.skill_set_night)
                            remaining_set = set(it.chain.from_iterable(temp_night_set))
                            allocated = np.where(desire[d] == 2)[0] - 1
                            allocated = allocated[allocated >= 0]
                            mods = np.arange(3)
                            for an in allocated:
                                remaining_set = self.search_set(
                                    temp_night_set, arr_skill[an]
                                )
                                mods = np.delete(mods, np.where(mods == an % 3)[0][0])
                                count += 1

                        if arr_skill[n - 1] in remaining_set and (n - 1) % 3 in mods:
                            temp = np.append(temp, n)
                            remaining_set = self.search_set(
                                temp_night_set, arr_skill[n - 1]
                            )
                            random_nurse_index = np.delete(
                                random_nurse_index, np.where(random_nurse_index == n)
                            )
                            mods = np.setdiff1d(mods, (n - 1) % 3)
                            count += 1
                            limit = 0
                            if count == 3:
                                for t in temp:
                                    ex_shift[t - 1] = 2
                        else:
                            limit += 1
                            if random_nurse_index.size == limit:
                                random_nurse_index = np.append(random_nurse_index, temp)
                                count, limit = 0, 0

                    count, limit = 0, 0
                    while count < 3:
                        n = random_nurse_index[limit]
                        if count == 0:
                            temp = np.empty(0, dtype=np.int32)
                            temp_night_set = copy.deepcopy(self.skill_set_night)
                            remaining_set = set(it.chain.from_iterable(temp_night_set))
                            allocated = np.where(desire[d] == 3)[0] - 1
                            allocated = allocated[allocated >= 0]
                            mods = np.arange(3)
                            for an in allocated:
                                remaining_set = self.search_set(
                                    temp_night_set, arr_skill[an]
                                )
                                mods = np.delete(mods, np.where(mods == an % 3)[0][0])
                                count += 1

                        if arr_skill[n - 1] in remaining_set and (n - 1) % 3 in mods:
                            temp = np.append(temp, n)
                            remaining_set = self.search_set(
                                temp_night_set, arr_skill[n - 1]
                            )
                            random_nurse_index = np.delete(
                                random_nurse_index, np.where(random_nurse_index == n)
                            )
                            mods = np.setdiff1d(mods, (n - 1) % 3)
                            count += 1
                            limit = 0
                            if count == 3:
                                for t in temp:
                                    ex_shift[t - 1] = 3
                        else:
                            limit += 1
                            if random_nurse_index.size == limit:
                                random_nurse_index = np.append(random_nurse_index, temp)
                                count, limit = 0, 0

                    count, limit, loop = 0, 0, 0
                    while count < 10 and loop < 10:
                        n = random_nurse_index[limit]
                        ts = arr_skill[n - 1]
                        if count == 0:
                            temp = np.empty(0, dtype=np.int32)
                            temp_day_set = copy.deepcopy(self.skill_set_day)
                            remaining_set = set(it.chain.from_iterable(temp_day_set))
                            allocated = np.where(desire[d] == 1)[0] - 1
                            allocated = allocated[allocated >= 0]
                            mods = np.array([0, 1, 2] * 3)
                            for an in allocated:
                                remaining_set = self.search_set(
                                    temp_day_set, arr_skill[an]
                                )
                                mods = np.delete(mods, np.where(mods == an % 3)[0][0])
                                count += 1
                            loop += 1

                        if arr_skill[n - 1] in remaining_set and (
                            (n - 1) % 3 in mods or mods.size == 0
                        ):
                            temp = np.append(temp, n)
                            remaining_set = self.search_set(
                                temp_day_set, arr_skill[n - 1]
                            )
                            random_nurse_index = np.delete(
                                random_nurse_index, np.where(random_nurse_index == n)
                            )
                            count += 1
                            limit = 0
                            if count == 10:
                                for t in temp:
                                    ex_shift[t - 1] = 1
                                flag = False
                            else:
                                mods = np.delete(
                                    mods, np.where(mods == (n - 1) % 3)[0][0]
                                )
                                limit = 0
                        else:
                            limit += 1
                            if random_nurse_index.size == limit:
                                random_nurse_index = np.append(random_nurse_index, temp)
                                random_nurse_index = self.rng.permutation(
                                    random_nurse_index
                                )
                                count, limit = 0, 0
                                loops += 1

                generation[p][d - 1] += ex_shift
                random_day_index = np.delete(
                    random_day_index, np.where(random_day_index == d)
                )
        end_time = time.perf_counter()

        np.set_printoptions(threshold=np.inf)
        # print(generation[9])

        evvalues = []
        # allnpms = []
        indvvsums = []
        forbidden_3pattern = ["111111", "333", "21", "23", "203"]
        forbidden_2pattern = ["11111", "32", "31", "22", "21", "23", "20"]
        deb = []
        for i in range(P):
            npms = []
            vpm = 0  # 人数違反
            vs = 0  # スキル値違反
            vt = 0  # 回数違反
            vfp = 0  # 禁止パターン
            for d in range(T):
                mod_nurses = np.zeros((3, 3), dtype=np.int64)
                exskl = np.zeros(3, dtype=np.int64)
                for n in range(N):
                    for s in range(3):
                        mod_nurses[n % 3][s] += generation[i][d][n] == s + 1
                        exskl[s] += (generation[i][d][n] == s + 1) * arr_skill[n]

                npms.append(mod_nurses)

                # モジュール人数制約
                for m in mod_nurses:
                    if m[0] < 3:
                        vpm += abs(m[0] - 3)
                        deb.append(1 + abs(m[0] - 3) * 10 + (d + 1) * 100)

                    if m[1] < 1:
                        vpm += abs(m[1] - 1)
                        deb.append(2)
                    if m[2] < 1:
                        vpm += abs(m[2] - 1)
                        deb.append(3)

                # 日勤10人制約
                exdaysum = np.sum(mod_nurses, axis=0)[0]
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
            worktimes = np.sum(generation[i] != 0, axis=0)
            # 3交代

            wd = np.sum(generation[i] == 1, axis=0)
            for x in wd:
                if x < 5:
                    vt += abs(x - 5)
                elif x > 15:
                    vt += abs(x - 15)
            sumnw = 0
            wsn = np.sum(generation[i] == 2, axis=0)
            for x in wsn:
                if x < 2:
                    vt += abs(x - 2)
                elif x > 7:
                    vt += abs(x - 7)
                sumnw += x

            wmn = np.sum(generation[i] == 3, axis=0)
            for x in wmn:
                if x < 2:
                    vt += abs(x - 2)
                elif x > 7:
                    vt += abs(x - 7)
                sumnw += x
            if sumnw < 5:
                vt += abs(sumnw - 5)
            elif sumnw > 9:
                vt += abs(sumnw - 9)

            # 禁止勤務パターン制約
            for n in range(N):
                wline = ""
                for d in range(T):
                    wline += str(generation[i][d][n])
                for p in forbidden_3pattern:
                    tml = re.findall(p, wline)
                    vfp += len(tml)

            evvalues.append([vpm, vs, vt, vfp])
            indvvsums.append(vpm + int(vs * (1 / 20)) + vt + vfp)
            # allnpms.append(npms)
        result = [indvvsums, evvalues]
        # print(np.array(result[0]))
        # print(np.array(result[1]))
        print(np.sum(np.array(result[1]), axis=0))
        # print(loops)
        # print(deb)
        # print(npms)
        print(end_time - start_time)


if __name__ == "__main__":
    np.set_printoptions(linewidth=100)
    # cc = CreateConfig()
    # cc.create_config()

    gs = GenInitSols()
    gs.generate_solution()
