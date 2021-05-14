from contextlib import contextmanager
from pathlib import Path
from typing import Union, Optional
import os

import git
import streamlit as st
import yaml


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


#%% Utils for model parameters
def _read_train_params(rev: str) -> dict:
    with git_open(ROOT_DIR / "dvc.lock", rev=rev) as file:
        dvc_lock = yaml.safe_load(file)
        return dvc_lock["stages"]["train"]["params"]["params.yaml"]


MODELS_PARAMETERS = {
    commit.hexsha: _read_train_params(rev=commit.hexsha)
    for commit in REPO.iter_commits(
        rev=f"...{FIRST_PIPELINE_COMMIT}",
        paths="dvc.lock",
    )
}


def get_model_backbone(model_rev: str) -> Optional[str]:
    model_parameters = MODELS_PARAMETERS[model_rev]
    try:
        return model_parameters["model"]["backbone"].split(".")[-1]
    except KeyError:
        pass


def _display_model(hexsha: str) -> str:
    commit = REPO.commit(hexsha)
    backbone = get_model_backbone(hexsha) or "-"

    return f"{commit.message} / {backbone} / {commit.committed_datetime} / {hexsha}"


def st_model_multiselect():
    return st.multiselect(
        "1. Choose your model(s)",
        list(MODELS_PARAMETERS),
        format_func=_display_model,
    )
