# Improvise from 2 !
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


#%%
selected_commit_a = st.selectbox(
    "Choose your commit A",
    [commit for commit in MODELS_COMMITS],
    format_func=lambda commit: f"{commit.hexsha[:6]} - {commit.message} - {commit.committed_datetime}",
)

selected_commit_b = st.selectbox(
    "Choose your commit B",
    [commit for commit in MODELS_COMMITS],
    format_func=lambda commit: f"{commit.hexsha[:6]} - {commit.message} - {commit.committed_datetime}",
)



#%% Load predictions from a given commit
import dvc.api
import pandas as pd

@st.cache
def load_predictions(rev: str) -> pd.DataFrame:
    with dvc.api.open("data/evaluation/predictions.csv", rev=rev) as f:
        return pd.read_csv(f)


predictions_a = load_predictions(rev=selected_commit_a.hexsha)
predictions_b = load_predictions(rev=selected_commit_b.hexsha)

all_predictions = pd.merge(predictions_a, predictions_b, on=["image_path", "image_name", "true_label"], how="outer", suffixes=("_a", "_b"))
disagree_predictions = all_predictions.loc[lambda df: df.predicted_label_a != df.predicted_label_b]

st.dataframe(disagree_predictions)

#%% Show images wrongly classified
for _, row in disagree_predictions.iterrows():
    st.image(
        row["image_path"],
        caption=f"{row['image_name']}: predicted_a={row['prediction_a']}, predicted_b={row['prediction_b']}, true={row['true_label']})",
        width=150,
    )
