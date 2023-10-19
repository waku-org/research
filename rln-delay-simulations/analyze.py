import numpy as np
import sys

file = sys.argv[1]
field = sys.argv[2]
print("Data file:", file, "field:", field)

latencies = []
with open(file, "r") as file:
    for line in file.readlines():
        if field in line:
            seq = int(line.strip().split("seq=")[1].split(" ")[0])
            # first message bias the latency due to tcp flow control
            if seq in [0]:
                continue
            seq = line.strip().split("seq=")[1].split(" ")[0]
            x = line.strip().split(field)[1].split(" ")[0]
            latencies.append(int(x))

array = np.array(latencies)
print(f"number_samples={array.size}")
print(f"Percentiles. P75={np.percentile(array, 75)} P95={np.percentile(array, 95)}")
print(f"Statistics. mean={np.mean(array)} max={array.max()} min={array.min()}")