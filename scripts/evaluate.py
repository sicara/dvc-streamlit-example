import json

import pandas as pd
import tensorflow as tf

from scripts.params import (
    BATCH_SIZE,
    DATASET_DIR,
    IMG_SIZE,
    TRAIN_DIR,
    EVALUATION_DIR,
)


#%% Create evaluation dir if necessary
EVALUATION_DIR.mkdir(exist_ok=True)


#%% Load test dataset
test_dataset = tf.keras.preprocessing.image_dataset_from_directory(
    DATASET_DIR / "test",
    shuffle=False,
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
)


#%% Load model
model = tf.keras.models.load_model(TRAIN_DIR / "model")


#%%
predictions = tf.nn.sigmoid(model.predict(test_dataset).flatten()).numpy()


#%%
predictions_df = pd.DataFrame({
    "image_path": test_dataset.file_paths,
    "prediction": predictions,
}).assign(
    image_name=lambda df: df.image_path.str.split("/").map(lambda parts: parts[-1]),
    true_label=lambda df: df.image_path.str.split("/").map(lambda parts: parts[-2]),
    predicted_label=lambda df: (
        (df.prediction > 0.5)
        .astype(int)
        .map({idx: classname for idx, classname in enumerate(test_dataset.class_names)})
    ),
)

predictions_df.to_csv(EVALUATION_DIR / "predictions.csv", index=False)


#%%
metrics = {
    "test_set_length": len(predictions_df),
    "accuracy": (predictions_df.true_label == predictions_df.predicted_label).mean(),
}

with open(EVALUATION_DIR / "metrics.json", "w") as file:
    json.dump(metrics, file)
