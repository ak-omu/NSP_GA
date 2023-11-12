import numpy as np
import configparser
import itertools as it


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
            skill_set_night.add(i)
        skill_set_day = set()
        for i in it.combinations(self.input_skill_values(), 10):
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
        print(self.skill_set_night, self.skill_set_day)

    def search_set(self, target_set, value):
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


if __name__ == "__main__":
    np.set_printoptions(linewidth=100)
    cc = CreateConfig()
    cc.create_config()

    gs = GenInitSols()
