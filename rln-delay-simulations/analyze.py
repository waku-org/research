import numpy as np
import sys
def load(file_name, field):
    latencies = []
    with open(file_name, "r") as file:
        for line in file.readlines():
            if field in line:
                # first message bias the latency due to tcp flow control
                if "seq=" in line:
                    seq = int(line.strip().split("seq=")[1].split(" ")[0])
                    if seq in [0]:
                        continue
                x = line.strip().split(field)[1].split(" ")[0]
                latencies.append(int(x))
    return np.array(latencies)


if __name__ == "__main__":
    file = sys.argv[1]
    field = sys.argv[2]
    array = load(file, field)

    print("Data file:", file, "field:", field)
    print(f"number_samples={array.size}")
    print(f"Percentiles. P75={np.percentile(array, 75)} P95={np.percentile(array, 95)}")
    print(f"Statistics. mean={np.mean(array)} max={array.max()} min={array.min()}")