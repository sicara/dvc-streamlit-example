import dvc.api
import pandas as pd
import streamlit as st

from scripts.params import EVALUATION_DIR
from st_scripts.st_utils import st_model_selectbox, MODELS_PARAMETERS, REPO


@st.cache
def load_predictions(model_rev: str) -> pd.DataFrame:
    with dvc.api.open(EVALUATION_DIR / "predictions.csv", rev=model_rev) as file:
        return pd.read_csv(file)


def st_evaluate_single_model():
    st.markdown("### Explore Performance on the Test Set")

    selected_model_rev = st_model_selectbox()
    threshold = st.sidebar.slider("Choose model threshold", 0.0, 1.0, value=0.5)

    model_parameters = MODELS_PARAMETERS[selected_model_rev]
    model_commit = REPO.commit(selected_model_rev)

    st.write("Commit information:", model_commit)
    st.json({
        "message": model_commit.message,
        "committed_datetime": str(model_commit.committed_datetime),
        "committer": str(model_commit.committer),
    })

    st.text("Model parameters:")
    st.json(model_parameters)

    st.markdown("## Metrics")
    predictions = (
        load_predictions(model_rev=selected_model_rev)
        .assign(predicted_label=lambda df: (
            pd.Series("cats", index=df.index).where(df.prediction < threshold, other="dogs")
        ))
    )

    accuracy = (predictions.true_label == predictions.predicted_label).mean()
    st.write("Accuracy (%):", round(100 * accuracy, 2))
