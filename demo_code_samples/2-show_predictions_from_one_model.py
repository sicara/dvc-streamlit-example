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

st.write([commit.message for commit in MODELS_COMMITS])

#%%
selected_commit = st.selectbox(
    "Choose your commit",
    [commit for commit in MODELS_COMMITS],
    format_func=lambda commit: f"{commit.hexsha[:6]} - {commit.message} - {commit.committed_datetime}",
)

st.write("Selected Commit", selected_commit)


#%% Load predictions from a given commit
import dvc.api
import pandas as pd

@st.cache
def load_predictions(rev: str) -> pd.DataFrame:
    with dvc.api.open("data/evaluation/predictions.csv", rev=rev) as f:
        return pd.read_csv(f)


predictions = load_predictions(rev=selected_commit.hexsha)

st.dataframe(predictions)

#%% Show images wrongly classified
wrong_predictions = predictions.loc[lambda df: df.true_label != df.predicted_label]

for _, row in wrong_predictions.iterrows():
    st.image(
        row["image_path"],
        caption=f"{row['image_name']}: predicted={row['predicted_label']}, true={row['true_label']})",
        width=150,
    )
