from shutil import copy2

import numpy as np
import pandas as pd
from tqdm import tqdm

from scripts.params import DATASET_DIR, DATASET_VAL_TEST_SPLIT, RAW_DATASET_DIR

#%% Create dirs if necessary
DATASET_DIR.mkdir(exist_ok=True)


#%% Parse image names in raw dir
dataset_df = pd.DataFrame([
    {
        "image_name": file.name,
        "label": file.parent.name,
        "raw_path": file,
        "raw_split": file.parents[1].name,
    }
    for file in RAW_DATASET_DIR.glob("**/*.jpg")
]).assign(
    split=lambda df: df.raw_split.map(lambda split: (
        "train" if split == "train"
        else np.random.choice(list(DATASET_VAL_TEST_SPLIT), p=list(DATASET_VAL_TEST_SPLIT.values()))
    ))
)

print(dataset_df.groupby(["split", "label"]).image_name.count())
(
    dataset_df
    .drop(columns=["raw_path", "raw_split"])
    .to_csv(DATASET_DIR / "dataset.csv", index=False)
)

#%% Copy images to split subdirs
for split in ["train", "val", "test"]:
    for label in set(dataset_df.label):
        (DATASET_DIR / split / label).mkdir(exist_ok=True, parents=True)

tqdm.pandas(desc="Copying images to split folder")
dataset_df.progress_apply(lambda row: copy2(
    src=row["raw_path"],
    dst=DATASET_DIR / row["split"] / row["label"] / row["image_name"],
), axis=1)
