# Original code from: https://www.tensorflow.org/tutorials/images/transfer_learning
import dvclive
import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory

from scripts.params import (
    BATCH_SIZE,
    DATASET_DIR,
    EPOCHS_FROZEN,
    EPOCHS_UNFROZEN,
    FINE_TUNE_AT,
    IMG_SIZE,
    LEARNING_RATE,
    TRAIN_DIR,
)

#%% Load dataset
train_dataset = image_dataset_from_directory(
    DATASET_DIR / "train",
    shuffle=True,
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
).prefetch(buffer_size=tf.data.experimental.AUTOTUNE)

validation_dataset = image_dataset_from_directory(
    DATASET_DIR / "val",
    shuffle=True,
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
).prefetch(buffer_size=tf.data.experimental.AUTOTUNE)


#%% Define model
data_augmentation = tf.keras.Sequential([
  tf.keras.layers.experimental.preprocessing.RandomFlip('horizontal'),
  tf.keras.layers.experimental.preprocessing.RandomRotation(0.2),
])

preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input

# Create the base model from the pre-trained model MobileNet V2
IMG_SHAPE = IMG_SIZE + (3,)
base_model = tf.keras.applications.MobileNetV2(
    input_shape=IMG_SHAPE,
    include_top=False,
    weights='imagenet',
)

inputs = tf.keras.Input(shape=(160, 160, 3))
x = data_augmentation(inputs)
x = preprocess_input(x)
x = base_model(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.2)(x)
outputs = tf.keras.layers.Dense(1)(x)

model = tf.keras.Model(inputs, outputs)


#%% Define dvclive callback
# See https://dvc.org/doc/dvclive/dvclive-with-dvc
class MetricsCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch: int, logs: dict = None):
        logs = logs or {}
        for metric, value in logs.items():
            dvclive.log(metric, value)
        dvclive.next_step()


callbacks = [MetricsCallback()]


#%% Freeze the base model and train 10 epochs
base_model.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(lr=LEARNING_RATE),
    loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
    metrics=["accuracy"],
)
model.summary()

history = model.fit(
    train_dataset,
    epochs=EPOCHS_FROZEN,
    validation_data=validation_dataset,
    callbacks=callbacks,
)


#%% Unfreeze the base model
base_model.trainable = True

# Let's take a look to see how many layers are in the base model
print("Number of layers in the base model: ", len(base_model.layers))

# Freeze all the layers before the `FINE_TUNE_AT` layer
for layer in base_model.layers[:FINE_TUNE_AT]:
    layer.trainable = False

model.compile(
    loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
    optimizer=tf.keras.optimizers.RMSprop(lr=LEARNING_RATE/10),
    metrics=["accuracy"],
)
model.summary()

history_fine = model.fit(
    train_dataset,
    epochs=EPOCHS_FROZEN + EPOCHS_UNFROZEN,
    initial_epoch=EPOCHS_FROZEN,
    validation_data=validation_dataset,
    callbacks=callbacks,
)


#%%
tf.saved_model.save(model, str(TRAIN_DIR / "model"))
