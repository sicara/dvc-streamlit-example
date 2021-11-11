import json
import pandas as pd

# 1. Inputs
HUGE_FILE_NAME = "huge_csv_file.csv"
METRICS_FILE_NAME = "metrics.json"

# 2. Open input files
data_df = pd.read_csv(HUGE_FILE_NAME)

# 3. Process the data
huge_metrics = 10e3 * (0.5 - data_df.col_b.mean())

# 4. Write result
with open(METRICS_FILE_NAME, "w") as metrics_file:
    json.dump({"metrics": huge_metrics}, metrics_file)
