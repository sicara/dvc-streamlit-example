from pathlib import Path

import yaml


PARAMETERS_FILE = "params.yaml"


with open(PARAMETERS_FILE) as file:
    print(f"Parsing parameters from \"{PARAMETERS_FILE}\"")
    params = yaml.safe_load(file)


DATA_ROOT_DIR = Path(params["data"]["root_dir"])
RAW_DATASET_DIR = DATA_ROOT_DIR / params["data"]["download"]["subdir"]
DATASET_DIR = DATA_ROOT_DIR / params["data"]["dataset"]["subdir"]
DATASET_VAL_TEST_SPLIT = params["data"]["dataset"]["val_test_split"]
