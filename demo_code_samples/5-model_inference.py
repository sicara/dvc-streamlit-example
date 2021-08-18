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
selected_commit = st.selectbox(
    "Choose your commit",
    [commit for commit in MODELS_COMMITS],
    format_func=lambda commit: f"{commit.hexsha[:6]} - {commit.message} - {commit.committed_datetime}",
)


#%% Function to load a model from a given commit
# - tf.keras.models.load_model() only supports str or Path like object
# - Model is saved in a folder (see tree data/train/model)
# - See the cache structure: tree .model_cache -L 2
import tensorflow as tf
# Warning: this is private internal dvc api, it may change with future version
import dvc.repo.get

ROOT_MODEL_CACHE_DIR = Path(".model_cache")
ROOT_MODEL_CACHE_DIR.mkdir(exist_ok=True)

@st.cache
def load_model(rev: str):

    print(f"Loading model for revision {rev}")

    # 1. Download model to model cache dir using `dvc get`
    # See https://dvc.org/doc/command-reference/get

    model_cache_dir = str(ROOT_MODEL_CACHE_DIR / rev)

    # Try to load the model directly (if it is in cache dir)
    try:
        return tf.keras.models.load_model(model_cache_dir)
    except OSError:
        print(f"Could not find model {rev} in cache")
    except Exception as e:
        print(f"Could not load model {rev} from cache")

    dvc.repo.get.get(
        url=".",
        path="data/train/model",
        out=model_cache_dir,
        rev=rev
    )
    print(f"Model downloaded to {model_cache_dir}")

    # 2. Load the model with tf.keras.models.load_model
    return tf.keras.models.load_model(model_cache_dir)

#%%
model = load_model(selected_commit.hexsha)

#%%
uploaded_file = st.file_uploader("Upload an image")


#%% Run the loaded model on the uploaded image
from PIL import Image
from scripts.params import IMG_SIZE
import numpy as np


if uploaded_file:
    image = Image.open(uploaded_file)
    image_name = uploaded_file.name
    resized_image = image.resize(IMG_SIZE)

    input = np.expand_dims(tf.keras.preprocessing.image.img_to_array(resized_image), axis=0)
    prediction = tf.nn.sigmoid(model.predict(input).flatten()).numpy()[0]

    col1, col2 = st.beta_columns(2)

    col2.image(image)
    col2.image(resized_image)

    col1.write({
        "prediction": "cat" if prediction > 0.5 else "dog",
        "score": float(prediction),
    })

