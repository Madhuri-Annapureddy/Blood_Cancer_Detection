"""
Train EfficientNet-B0 (transfer learning) on the C-NMC ALL classification task,
using the subject-disjoint split produced by subject_split.py.

Run subject_split.py FIRST — this script will fail loudly if the split CSV
doesn't exist, since training on a non-disjoint split defeats the whole point.

Metrics reported: accuracy, sensitivity (recall on ALL — the clinically
critical number, since missing a cancer case is worse than a false alarm),
specificity, and AUROC — not just accuracy alone.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
from sklearn.metrics import roc_auc_score, confusion_matrix, classification_report

# ---- CONFIG ----
SPLIT_CSV = Path("ml/data/splits/subject_disjoint_split.csv")
MODEL_OUTPUT_DIR = Path("ml/saved_models")
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15          # real training run — pipeline already confirmed working
FINE_TUNE_EPOCHS = 10  # phase 2: fine-tuning top layers, usually needs fewer epochs
LEARNING_RATE = 1e-4

LABEL_TO_INT = {"HEM": 0, "ALL": 1}  # HEM=healthy=0, ALL=cancer=1


def load_split() -> pd.DataFrame:
    if not SPLIT_CSV.exists():
        raise FileNotFoundError(
            f"{SPLIT_CSV} not found. Run subject_split.py first to generate "
            "the subject-disjoint split before training."
        )
    df = pd.read_csv(SPLIT_CSV)
    df["label_int"] = df["label"].map(LABEL_TO_INT)
    return df


def make_dataset(df: pd.DataFrame, split_name: str, shuffle: bool, augment: bool = False) -> tf.data.Dataset:
    subset = df[df["split"] == split_name]
    paths = subset["filepath"].values
    labels = subset["label_int"].values

    def _load_and_preprocess(path, label):
        img = tf.io.read_file(path)
        img = tf.image.decode_bmp(img, channels=3)
        img = tf.image.resize(img, IMG_SIZE)
        if augment:
            # Basic augmentation to improve generalization to new patients —
            # random flips/rotation/brightness simulate the kind of
            # orientation and staining variation seen across different
            # patients/scanners, which is exactly what your held-out test
            # subjects differ on.
            img = tf.image.random_flip_left_right(img)
            img = tf.image.random_flip_up_down(img)
            img = tf.image.rot90(img, k=tf.random.uniform([], 0, 4, dtype=tf.int32))
            img = tf.image.random_brightness(img, max_delta=0.15)
            img = tf.image.random_contrast(img, lower=0.85, upper=1.15)
            img = tf.clip_by_value(img, 0.0, 255.0)
        img = tf.keras.applications.efficientnet.preprocess_input(img)
        return img, label

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))

    # IMPORTANT: shuffle BEFORE loading/preprocessing images, not after.
    # Shuffling here only reorders lightweight file path strings — shuffling
    # after .map() would require holding thousands of fully decoded, resized
    # images in memory at once (several GB), which can crash on a typical
    # laptop. A smaller, fixed buffer size also caps memory use regardless
    # of dataset size.
    if shuffle:
        buffer_size = min(len(paths), 1000)
        ds = ds.shuffle(buffer_size=buffer_size, seed=42)

    ds = ds.map(_load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds


def build_model() -> tuple:
    base_model = EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=(*IMG_SIZE, 3),
        pooling="avg",
    )
    base_model.trainable = False  # frozen for phase 1 (train head only)

    inputs = layers.Input(shape=(*IMG_SIZE, 3))
    x = base_model(inputs, training=False)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)

    model = models.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model, base_model


def fine_tune_model(model, base_model, unfreeze_last_n_layers: int = 20) -> None:
    """
    Phase 2: unfreeze the top N layers of the base model and continue
    training at a much lower learning rate. This lets the model adapt its
    visual features to blood cell morphology specifically, instead of
    staying stuck on generic ImageNet features — this is usually where the
    biggest generalization improvement comes from in transfer learning,
    since a frozen base only ever learns a linear cutoff on features that
    were never trained on microscopy images.

    A low learning rate here is important: fine-tuning with too high a
    learning rate can destroy the useful pretrained features instead of
    gently adapting them.
    """
    base_model.trainable = True

    # Keep all but the last N layers frozen — fine-tuning the whole base at
    # once, especially with a small dataset like this, risks overfitting.
    for layer in base_model.layers[:-unfreeze_last_n_layers]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE / 10),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )


def evaluate_with_clinical_metrics(model, test_ds, df_test: pd.DataFrame) -> None:
    y_true = df_test["label_int"].values
    y_pred_proba = model.predict(test_ds).flatten()
    y_pred = (y_pred_proba > 0.5).astype(int)

    print("\n--- Test set results (subject-disjoint) ---")
    print(classification_report(y_true, y_pred, target_names=["HEM", "ALL"]))

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    sensitivity = tp / (tp + fn)  # recall on ALL — most clinically important
    specificity = tn / (tn + fp)
    auroc = roc_auc_score(y_true, y_pred_proba)

    print(f"Sensitivity (recall on ALL): {sensitivity:.3f}")
    print(f"Specificity (recall on HEM): {specificity:.3f}")
    print(f"AUROC: {auroc:.3f}")
    print(
        "\nNote: compare these numbers against a naive-random-split run of the "
        "same model — that comparison is your leakage-aware benchmark table."
    )


if __name__ == "__main__":
    df = load_split()

    train_ds = make_dataset(df, "train", shuffle=True, augment=True)
    val_ds = make_dataset(df, "val", shuffle=False, augment=False)
    test_ds = make_dataset(df, "test", shuffle=False, augment=False)

    # Compute class weights from the TRAINING set only, to counteract the
    # ALL/HEM imbalance — without this, the model tends to just lean toward
    # predicting the majority class (ALL) since that minimizes loss on paper.
    train_df = df[df["split"] == "train"]
    n_all = (train_df["label_int"] == 1).sum()
    n_hem = (train_df["label_int"] == 0).sum()
    total = n_all + n_hem
    class_weight = {
        0: total / (2 * n_hem),  # HEM
        1: total / (2 * n_all),  # ALL
    }
    print(f"Class weights (to counter train imbalance): {class_weight}")

    model, base_model = build_model()
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_auc", mode="max", patience=3, restore_best_weights=True
        ),
    ]

    print("\n=== PHASE 1: training classifier head only (base frozen) ===")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=callbacks,
        class_weight=class_weight,
    )

    print("\n=== PHASE 2: fine-tuning top layers of the base model ===")
    fine_tune_model(model, base_model, unfreeze_last_n_layers=20)
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=FINE_TUNE_EPOCHS,
        callbacks=callbacks,
        class_weight=class_weight,
    )

    df_test = df[df["split"] == "test"]
    evaluate_with_clinical_metrics(model, test_ds, df_test)

    MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_OUTPUT_DIR / "efficientnet_b0_cnmc.keras")
    print(f"\nModel saved to {MODEL_OUTPUT_DIR / 'efficientnet_b0_cnmc.keras'}")