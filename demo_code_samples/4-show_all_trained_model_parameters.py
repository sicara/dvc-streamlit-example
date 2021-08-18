import streamlit as st

st.set_page_config(page_title="Dvc + Streamlit = ❤")
st.title("Dvc + Streamlit = ❤️")


#%% Fetch all commits modifying the dvc.lock file
import git
from pathlib import Path

ROOT_DIR = Path(".")
REPO = git.Repo(str(ROOT_DIR))
FIRST_COMMIT = list(REPO.iter_commits())[-1]
# First commit a full training pipeline was run
FIRST_PIPELINE_COMMIT = "6f96e3ffb98b0ba833937c510e93a6cdd3555f05"

MODELS_COMMITS = list(REPO.iter_commits(
    rev=f"...{FIRST_PIPELINE_COMMIT}",
    paths="dvc.lock",
))


#%% Utils to open file tracked by Git
from contextlib import contextmanager


@contextmanager
def git_open(path: str, rev: str):
    commit = REPO.commit(rev)
    # Hack to get the full blob data stream: compute diff with initial commit
    diff = commit.diff(FIRST_COMMIT, str(path))[0]
    yield diff.a_blob.data_stream


#%% Parse train parameters from dvc lock files
import json
import yaml
import pandas as pd


def get_model_info(rev: str) -> dict:
    with git_open("dvc.lock", rev=rev) as file:
        train_params = yaml.safe_load(file)["stages"]["train"]["params"]["params.yaml"]

    with git_open("data/evaluation/metrics.json", rev=rev) as file:
        metrics = json.load(file)

    return {
        "learning_rate": train_params["train"]["learning_rate"],
        "backbone": train_params.get("model", {}).get("backbone", "-").split(".")[-1],
        "accuracy": metrics["accuracy"],
        # Add whatever you want here
    }


models_info = pd.DataFrame([
    {
        "commit": commit.hexsha[:6],
        "name": commit.message,
        **get_model_info(rev=commit.hexsha),
    }
    for commit in MODELS_COMMITS
]).set_index("commit")

st.dataframe(models_info)

#%% Plot a graph
st.line_chart(models_info.accuracy)
