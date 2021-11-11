import hashlib

import pandas as pd
import numpy as np

# 1. Inputs
YOUR_NAME = "antoinet"  # Should be unique in the audience
N = int(1e6)
HUGE_FILE_NAME = "huge_csv_file.csv"

# 2. Generate the file
seed = int(hashlib.md5(YOUR_NAME.encode()).hexdigest(), 16) % 2**32
np.random.seed(seed)
data_df = pd.DataFrame({"col_a": range(N), "col_b": np.random.random(N)})

# 3. Write result
data_df.to_csv(HUGE_FILE_NAME)
