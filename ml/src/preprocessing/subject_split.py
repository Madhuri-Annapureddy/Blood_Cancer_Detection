"""
Subject-disjoint train/val/test split for the C-NMC 2019 ALL Challenge dataset.

WHY THIS EXISTS:
Most public code for C-NMC does a random image-level split, which leaks the same
patient's cells into both train and test — this inflates reported accuracy and is
not a fair evaluation. This script splits by SUBJECT (patient), so a patient's
images only ever appear in one of train/val/test.

EXPECTED INPUT STRUCTURE (adjust ROOT_DIR / folder names to match your download):
    ml/data/raw/C-NMC_training_data/
        fold_0/
            all/   *.bmp
            hem/   *.bmp
        fold_1/
            all/   *.bmp
            hem/   *.bmp
        fold_2/
            all/   *.bmp
            hem/   *.bmp

C-NMC filenames encode the patient/subject ID, e.g.:
    UID_9_11_1_all.bmp        -> ALL patient, subject id "9"
    UID_H21_19_3_hem.bmp      -> Healthy patient, subject id "H21"

If your downloaded copy has different filenames, check a few examples first and
adjust `extract_subject_id()` below accordingly — this is the single most
important function in this script, since a wrong subject id defeats the whole
point of a leakage-free split.

OUTPUT:
    ml/data/splits/subject_disjoint_split.csv
    columns: filepath, label, subject_id, split   (split = train / val / test)
"""

import re
import random
from pathlib import Path
import pandas as pd

# ---- CONFIG: adjust these two paths to match your local setup ----
ROOT_DIR = Path("ml/data/raw/archive")
OUTPUT_CSV = Path("ml/data/splits/subject_disjoint_split.csv")

# Split proportions are by SUBJECT, not by image
TRAIN_FRAC = 0.70
VAL_FRAC = 0.15
TEST_FRAC = 0.15  # (kept implicit — whatever's left after train/val)

RANDOM_SEED = 42


def extract_subject_id(filename: str) -> str:
    """
    Extracts the patient/subject id from a C-NMC filename.
    Example: 'UID_9_11_1_all.bmp' -> '9'
             'UID_H21_19_3_hem.bmp' -> 'H21'
             'UID_h3_10_1_hem.bmp' -> 'H3'  (normalized to uppercase)

    Case-insensitive on the 'H' prefix, since this dataset mirror mixes
    uppercase and lowercase 'h' for healthy-patient ids.
    """
    match = re.match(r"UID_([Hh]?\d+)_", filename)
    if match:
        # Normalize to uppercase so 'h3' and 'H3' are treated as the same subject
        return match.group(1).upper()
    raise ValueError(
        f"Could not extract subject id from filename: '{filename}'. "
        "Check the actual naming convention in your dataset and update "
        "extract_subject_id() accordingly."
    )


def collect_all_images(root_dir: Path) -> pd.DataFrame:
    """Recursively finds every 'all' and 'hem' folder anywhere under root_dir
    and collects their images. This handles inconsistent nesting between
    dataset mirrors (e.g. some have fold_0/all/, others have fold_0/fold_0/all/)
    without needing to hardcode the exact folder depth."""
    records = []
    label_map = {"all": "ALL", "hem": "HEM"}

    for label_folder_name, label_value in label_map.items():
        # rglob finds folders named 'all' or 'hem' at ANY depth under root_dir
        for label_dir in root_dir.rglob(label_folder_name):
            if not label_dir.is_dir():
                continue
            for img_path in label_dir.glob("*.bmp"):
                subject_id = extract_subject_id(img_path.name)
                records.append(
                    {
                        "filepath": str(img_path),
                        "label": label_value,
                        "subject_id": subject_id,
                    }
                )

    df = pd.DataFrame(records)
    if df.empty:
        raise RuntimeError(
            f"No images found under {root_dir}. Check ROOT_DIR points to the "
            "right extracted folder (the one containing fold_0, fold_1, fold_2)."
        )
    return df


def split_subjects(df: pd.DataFrame) -> pd.DataFrame:
    """Splits unique subjects (not images) into train/val/test, STRATIFIED by
    each subject's majority label (ALL or HEM), so the proportion of ALL vs
    HEM subjects is kept roughly balanced across all three splits instead of
    being left to chance. With only ~73 total subjects, a pure random shuffle
    can easily produce a skewed test set (e.g. 90% ALL) just by luck — this
    stratification prevents that."""
    random.seed(RANDOM_SEED)

    # Determine each subject's majority label (a subject might have a handful
    # of images of only one label in this dataset, but this handles mixed
    # cases safely too)
    subject_majority_label = (
        df.groupby("subject_id")["label"]
        .agg(lambda x: x.value_counts().idxmax())
    )

    all_subjects = subject_majority_label[subject_majority_label == "ALL"].index.tolist()
    hem_subjects = subject_majority_label[subject_majority_label == "HEM"].index.tolist()

    random.shuffle(all_subjects)
    random.shuffle(hem_subjects)

    def split_group(subjects: list) -> tuple[list, list, list]:
        n = len(subjects)
        n_train = int(n * TRAIN_FRAC)
        n_val = int(n * VAL_FRAC)
        return (
            subjects[:n_train],
            subjects[n_train:n_train + n_val],
            subjects[n_train + n_val:],
        )

    all_train, all_val, all_test = split_group(all_subjects)
    hem_train, hem_val, hem_test = split_group(hem_subjects)

    train_subjects = set(all_train + hem_train)
    val_subjects = set(all_val + hem_val)
    test_subjects = set(all_test + hem_test)

    def assign_split(subject_id: str) -> str:
        if subject_id in train_subjects:
            return "train"
        elif subject_id in val_subjects:
            return "val"
        else:
            return "test"

    df = df.copy()
    df["split"] = df["subject_id"].apply(assign_split)
    return df


def print_summary(df: pd.DataFrame) -> None:
    print("\n--- Split summary (by SUBJECT, confirms no leakage) ---")
    for split_name in ["train", "val", "test"]:
        split_df = df[df["split"] == split_name]
        n_subjects = split_df["subject_id"].nunique()
        n_images = len(split_df)
        label_counts = split_df["label"].value_counts().to_dict()
        print(
            f"{split_name:5s}: {n_subjects:3d} subjects, "
            f"{n_images:5d} images, labels={label_counts}"
        )

    # Sanity check: no subject should appear in more than one split
    subject_to_splits = df.groupby("subject_id")["split"].nunique()
    leaking_subjects = subject_to_splits[subject_to_splits > 1]
    if len(leaking_subjects) > 0:
        raise RuntimeError(
            f"LEAKAGE DETECTED: {len(leaking_subjects)} subjects appear in "
            "more than one split. Do not proceed to training until this is fixed."
        )
    print("\n✅ No subject appears in more than one split — safe to train on.")


if __name__ == "__main__":
    print(f"Scanning images under: {ROOT_DIR.resolve()}")
    df = collect_all_images(ROOT_DIR)
    print(f"Found {len(df)} images across {df['subject_id'].nunique()} subjects.")

    df = split_subjects(df)
    print_summary(df)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved split to: {OUTPUT_CSV.resolve()}")