from contextlib import contextmanager
from pathlib import Path
from typing import Union, Optional
import os
import json

import git
import streamlit as st
import yaml

from scripts.params import EVALUATION_DIR


ROOT_DIR = Path(os.path.dirname(os.path.realpath(__file__))).parent
REPO = git.Repo(str(ROOT_DIR))
FIRST_COMMIT = list(REPO.iter_commits())[-1]
# First commit a full training pipeline was run
FIRST_PIPELINE_COMMIT = "6f96e3ffb98b0ba833937c510e93a6cdd3555f05"


#%% Utils for git, dvc, streamlit
@contextmanager
def git_open(path: Union[str, Path], rev: str):
    commit = REPO.commit(rev)
    # Hack to get the full blob data stream: compute diff with initial commit
    diff = commit.diff(FIRST_COMMIT, str(path))[0]
    yield diff.a_blob.data_stream


#%% Retrive commits for trained model
MODELS_COMMITS = list(REPO.iter_commits(
    rev=f"...{FIRST_PIPELINE_COMMIT}",
    paths="dvc.lock",
))


#%% Utils for model parameters
def _read_train_params(rev: str) -> dict:
    with git_open(ROOT_DIR / "dvc.lock", rev=rev) as file:
        dvc_lock = yaml.safe_load(file)
        return dvc_lock["stages"]["train"]["params"]["params.yaml"]


MODELS_PARAMETERS = {
    commit.hexsha: _read_train_params(rev=commit.hexsha)
    for commit in MODELS_COMMITS
}


#%%
def _read_model_evaluation_metrics(model_rev: str) -> dict:
    with git_open(EVALUATION_DIR / "metrics.json", rev=model_rev) as file:
        return json.load(file)


MODELS_EVALUATION_METRICS = {
    commit.hexsha: _read_model_evaluation_metrics(model_rev=commit.hexsha)
    for commit in MODELS_COMMITS
}


#%%
def get_model_backbone(model_rev: str) -> Optional[str]:
    model_parameters = MODELS_PARAMETERS[model_rev]
    try:
        return model_parameters["model"]["backbone"].split(".")[-1]
    except KeyError:
        pass


def _display_model(hexsha: str) -> str:
    commit = REPO.commit(hexsha)
    backbone = get_model_backbone(hexsha) or "-"

    return f"{commit.message} / {backbone} / {commit.committed_datetime}"


def st_model_multiselect():
    return st.sidebar.multiselect(
        "Choose your model(s)",
        [commit.hexsha for commit in MODELS_COMMITS],
        format_func=_display_model,
    )


def st_model_selectbox():
    return st.sidebar.selectbox(
        "Choose your model",
        [commit.hexsha for commit in MODELS_COMMITS],
        format_func=_display_model,
    )
