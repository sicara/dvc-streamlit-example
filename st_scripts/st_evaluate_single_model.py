import json

import dvc.api
import pandas as pd
import streamlit as st

from scripts.params import EVALUATION_DIR
from st_scripts.st_utils import st_model_selectbox, MODELS_PARAMETERS, REPO


with open("./st_scripts/vega_graphs/confusion_matrix.json") as file:
    VEGA_CONFUSION_MATRIX = json.load(file)


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

    st.vega_lite_chart(predictions, VEGA_CONFUSION_MATRIX["spec"])

    st.markdown("## Images")

    images_selector_columns = st.columns(5)
    with images_selector_columns[2]:
        st.write("True label")
        st.write("Predicted label")
    with images_selector_columns[3]:
        show_true_cats_images = st.checkbox(label="cats", key="true_cats_images", value=False)
        show_predicted_cats_images = st.checkbox(label="cats", key="predicted_cats_images", value=True)
    with images_selector_columns[4]:
        show_true_dogs_images = st.checkbox(label="dogs", key="true_dogs_images", value=True)
        show_predicted_dogs_images = st.checkbox(label="dogs", key="predicted_cats_images", value=False)

    selected_true_labels = []
    if show_true_cats_images: selected_true_labels.append("cats")
    if show_true_dogs_images: selected_true_labels.append("dogs")

    selected_predicted_labels = []
    if show_predicted_cats_images: selected_predicted_labels.append("cats")
    if show_predicted_dogs_images: selected_predicted_labels.append("dogs")

    selected_predictions = predictions.loc[
        lambda df: df.true_label.isin(selected_true_labels)
    ].loc[
        lambda df: df.predicted_label.isin(selected_predicted_labels)
    ]

    with images_selector_columns[0]:
        st.write("Selected images:", len(selected_predictions))

    images_columns = st.columns(4)

    for idx, (_, row) in enumerate(selected_predictions.iterrows()):
        images_columns[idx % 4].image(
            row["image_path"],
            caption=f"true={row['true_label']}, predicted={row['predicted_label']}, pred={row['prediction']:.3f}",
        )
