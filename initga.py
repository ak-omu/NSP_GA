import numpy as np
import configparser


class LoadProblem:
    def __init__(self) -> None:
        pass

    def input_desire(self, file_path="problems/desire1.txt"):
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
        arr = np.array(arr)
        return arr

    def input_compatibility(self, file_path="problems/compatibility1.txt"):
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
        arr = arr + arr.T - np.diag(arr.diagonal())
        return arr


class LoadSetting:
    def __init__(self) -> None:
        pass

    def input_skill_values(self, file_path="settings/skill_values.txt"):
        with open(file_path, "r") as f:
            skill_values = np.array([int(x) for x in f.readline().split()])
            return skill_values

    def input_shift_system(self, file_path="settings/shift_system1.txt"):
        with open(file_path, "r") as f:
            shift_system = np.array([int(x) == 2 for x in f.readline().split()])
            return shift_system


class CreateConfig:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.command = configparser.ConfigParser()
        self.command.read("settings/command.ini")
        self.lp = LoadProblem()
        self.ls = LoadSetting()

    def create_config(self, file_path="configs/config1-1.ini"):
        PROBLEM_NUMBER = self.command.getint("COMMAND", "PROBLEM")
        SHIFT_SYSTEM_NUMBER = self.command.getint("COMMAND", "SHIFT_SYSTEM")
        if PROBLEM_NUMBER == None:
            PROBLEM_NUMBER = 1
        elif SHIFT_SYSTEM_NUMBER == None:
            SHIFT_SYSTEM_NUMBER = 1
        file_path = f"configs/config{SHIFT_SYSTEM_NUMBER}-{PROBLEM_NUMBER}.ini"

        arr_desire = self.lp.input_desire(f"problems/desire{PROBLEM_NUMBER}.txt")
        arr_compatibility = self.lp.input_compatibility(
            f"problems/compatibility{PROBLEM_NUMBER}.txt"
        )
        arr_skill = self.ls.input_skill_values(f"settings/skill_values.txt")
        arr_shift = self.ls.input_shift_system(
            f"settings/shift_system{SHIFT_SYSTEM_NUMBER}.txt"
        )

        for n in range(self.command.getint("COMMAND", "NURSE")):
            self.config["NURSE" + str(n + 1)] = {
                "name": "nurse " + str(n + 1),
                "skill": str(arr_skill[n]),
                "2nd shift": str(arr_shift[n]),
                "bad": str(
                    np.array(
                        [
                            i
                            for i, c in enumerate(arr_compatibility[n + 1])
                            if c == 1 and i != 0
                        ]
                    )
                ),
                "normal": str(
                    np.array(
                        [
                            i
                            for i, c in enumerate(arr_compatibility[n + 1])
                            if c == 2 and i != 0
                        ]
                    )
                ),
                "good": str(
                    np.array(
                        [
                            i
                            for i, c in enumerate(arr_compatibility[n + 1])
                            if c == 3 and i != 0
                        ]
                    )
                ),
                "education": str(
                    np.array(
                        [
                            i
                            for i, c in enumerate(arr_compatibility[n + 1])
                            if c == 4 and i != 0
                        ]
                    )
                ),
            }
            for d in range(self.command.getint("COMMAND", "TERM")):
                if arr_desire[n + 1][d + 1] >= 10:
                    self.config.set(
                        "NURSE" + str(n + 1),
                        "day " + str(d + 1),
                        "2_"
                        + str(
                            self.command["DESIRE"].get(
                                str(arr_desire[n + 1][d + 1] - 10)
                            )
                        ),
                    )
                elif arr_desire[n + 1][d + 1] >= 0:
                    self.config.set(
                        "NURSE" + str(n + 1),
                        "day " + str(d + 1),
                        "1_"
                        + str(
                            self.command["DESIRE"].get(str(arr_desire[n + 1][d + 1]))
                        ),
                    )

        with open(file_path, "w") as config_file:
            self.config.write(config_file)


class GenInitSols:
    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    np.set_printoptions(linewidth=100)
#    cc = CreateConfig()
#    cc.create_config()
