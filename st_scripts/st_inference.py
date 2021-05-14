from PIL import Image
# Warning: this is private internal dvc api, it may change for future dvc versions
from dvc.repo.get import get
import numpy as np
import pandas as pd
import streamlit as st
import tensorflow as tf

from scripts.params import TRAIN_DIR, IMG_SIZE
from st_scripts.st_utils import REPO, ROOT_DIR, get_model_backbone, st_model_multiselect


@st.cache
def load_model(rev: str):
    model_cache_dir = ROOT_DIR / ".model_cache"
    model_cache_dir.mkdir(exist_ok=True)

    print(f"Loading model for revision {rev}")
    # 1. Download model to MODEL_CACHE dir using `dvc get`
    # See https://dvc.org/doc/command-reference/get
    out_model_dir = str(model_cache_dir / rev)
    # Try to load the model directly (if it is in cache dir)
    try:
        return tf.keras.models.load_model(out_model_dir)
    except OSError:
        print(f"Could not find model {rev} in cache")
    except Exception as e:
        print(f"Could not load model {rev} from cache")

    get(url=".", path=str(TRAIN_DIR / "model"), out=out_model_dir, rev=rev)
    print(f"Model downloaded to {out_model_dir}")

    # 2. Load the model with tf.keras.models.load_model
    return tf.keras.models.load_model(out_model_dir)


def st_inference():
    st.markdown("### ModelsInference")

    selected_models = st_model_multiselect()

    models = {
        model_rev: load_model(rev=model_rev)
        for model_rev in selected_models
    }

    uploaded_file = st.file_uploader("2. Upload an image")

    if uploaded_file:
        image = Image.open(uploaded_file)
        image_name = uploaded_file.name
        resized_image = image.resize(IMG_SIZE)

        beta_column_0, beta_column_1, beta_column_2 = st.beta_columns(3)

        with beta_column_0:
            st.write(f"Image name: {image_name}")
            st.write(f"Image width: {image.size[0]}")
            st.write(f"Image height: {image.size[1]}")

        with beta_column_1:
            st.image(image, caption="Original image")

        with beta_column_2:
            st.image(resized_image, caption=f"Input resized image : {IMG_SIZE}")

        input = np.expand_dims(tf.keras.preprocessing.image.img_to_array(resized_image), axis=0)

        if st.button(f"Run {len(models)} model(s)"):
            predictions = []

            for model_rev, model in models.items():
                prediction = tf.nn.sigmoid(model.predict(input).flatten()).numpy()[0]

                predictions.append({
                    "backbone": get_model_backbone(model_rev),
                    "commit_hash": model_rev,
                    "commit_message": REPO.commit(model_rev).message,
                    "cat": 1 - prediction,
                    "dog": prediction,
                })

            st.dataframe(pd.DataFrame(predictions))
