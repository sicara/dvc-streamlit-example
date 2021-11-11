import hashlib

import pandas as pd
import numpy as np

# 1. Inputs
from params import YOUR_NAME, N_DATA, HUGE_FILE_NAME

# 2. Generate the file
seed = int(hashlib.md5(YOUR_NAME.encode()).hexdigest(), 16) % 2**32
np.random.seed(seed)
data_df = pd.DataFrame({"col_a": range(N_DATA), "col_b": np.random.random(N_DATA)})

# 3. Write result
data_df.to_csv(HUGE_FILE_NAME)
