import yaml

with open("params.yaml") as params_file:
    params = yaml.safe_load(params_file)

YOUR_NAME = params["your_name"]
N_DATA = params["n_data"]
HUGE_FILE_NAME = params["huge_file_name"]
METRICS_FILE_NAME = params["metrics_file_name"]
