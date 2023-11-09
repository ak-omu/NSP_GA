import numpy as np


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

    def input_compatible(self, file_path="problems/compatible1.txt"):
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


class GenInitSol:
    def __init__(self) -> None:
        pass

    def gen_init_sol(self, arr_desire, arr_compatible):
        pass


if __name__ == "__main__":
    np.set_printoptions(linewidth=100)
    lp = LoadProblem()
    arr_desire = lp.input_desire()
    arr_compatible = lp.input_compatible()
    print(arr_desire)
    print(arr_compatible)
    # print(np.array_equal(arr_compatible, arr_compatible.T))
    ls = LoadSetting()
    skill_values = ls.input_skill_values()
    print(skill_values)
