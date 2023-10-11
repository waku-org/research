from scipy import stats as st
import numpy as np
import sys

file = sys.argv[1]
field = sys.argv[2]
print("Config: file:", file, "field:", field)

latencies = []
with open(file, "r") as file:
    for line in file.readlines():
        if field in line:
            x = line.strip().split(field)[1].split(" ")[0]
            latencies.append(int(x))

array = np.array(latencies)
print(f"number_samples={array.size}")
print(f"Percentiles. P75={np.percentile(array, 75)} P95={np.percentile(array, 95)}")
print(f"Statistics. mode_value={st.mode(array).mode} mode_count={st.mode(array).count} mean={np.mean(array)} max={array.max()} min={array.min()}")