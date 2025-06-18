---
slug: finetuning-models
title: Finetuning Models
authors: [alan-insam]
---

# Finetuning Transformer Models for Custom PII Detection

:::warning
This guide is **conceptual** read it carefully before preparing any data and make sure that you understand what needs to be changed. First try on a small dataset first. But this is a very good starting point for your finetuning proccess.
:::


Guard utilizes the transformer model [`yonigo/distilbert-base-multilingual-cased-pii`](https://huggingface.co/yonigo/distilbert-base-multilingual-cased-pii), originally finetuned in the [yonigottesman/pii-model](https://github.com/yonigottesman/pii-model) repository and based on the [Ai-4-Privacy Dataset](https://huggingface.co/datasets/ai4privacy/pii-masking-300k). This dataset supports **27 PII classes** and over **220,000 examples**.  
If you want to further adapt the model to Austrian-specific data, such as documents in German, dialects, or unique local PII types (e.g., Austrian ID number), you can finetune the model on your own dataset.

<!-- truncate -->

## Why Finetune?

- **Improve accuracy** for domain- or region-specific data (e.g., Austrian contracts, forms, or legal texts).
- **Add Austrian-specific PII types** (like `AUT_ID_NUMBER`).
- **Adapt to dialects, regional language, or document formats.**

---

## Overview of Finetuning GUARDs transformer model

The simplest approach for finetuning GUARD is to adapt GUARDs basemodel: [`yonigo/distilbert-base-multilingual-cased-pii`](https://huggingface.co/yonigo/distilbert-base-multilingual-cased-pii). For that head over to the [model's repository](https://github.com/yonigottesman/pii-model) and clone it:

```bash
git clone https://github.com/yonigottesman/pii-model && pip install -r requirements.txt
```

Then head over to the `train.py` script, which containings the training script for finetuning a pretrained model, in this case `distilbert-base-cased`, which supports `English` by default, you can swap it with any pretrained token classifier, such as `distilbert-base-multilingual-cased` which supports over **104** languages. This base model was used in our transformer.

---

## Step By Step Guide on Finetuning

### 1. Understand the Data that you need to prepare

You need to create a `JSON` file or `CSV` file with your data that follows the format detailled below. The example detaills a `JSONL` sample record. As you can see your dataset **must** contain objects of samples with the key-value pairs `source_text`, which is the original text and a `privacy_mask` key-value pair that details the corresponding detected PII entites with their character spans and labels. Furthermore, make sure that each sample contains an associated `language`. You may prepare a dataset consisting of multiple language samples. If not, e.g. when constructing only in German drop the `language` pair, depending on this you may further need to adjust `train.py`.

```json
{
  "source_text": "Das ist ein Beispieltext. Herr Max Mustermann wohnt in Wien und seine Ausweisnummer ist L1234567A.",
  "privacy_mask": [
    {"start": 31, "end": 45, "label": "PERSON"}, 
    {"start": 55, "end": 59, "label": "CITY"},
    {"start": 88, "end": 97, "label": "AUSTRIAN_ID_CARD"}
  ],
  "language": "de"
}
```

Create a dataset for training `austrian_train.jsonl` and `austrian_validation.jsonl` for validation. This step is the most crucial steps, annotating these datasets should happen automatically if possible! Note that you can use an existing dataset, such as [AI 4 Privacy](https://huggingface.co/datasets/ai4privacy/pii-masking-300k) and just *add new records for new entities*! Ensure a representative number of examples for any new PII entities you add.

---

### 2. Adjust the `train.py` script

You need to modify several sections. Note that this guide is **not** complete, but conceptual, you may need modify more pieces or it may not fully work out of the box!

#### 2.1. Adjust the `lables`

In the `train()` function there is a list containing all the labels that are found in the dataset. If you chose to augment [AI 4 Privacy](https://huggingface.co/datasets/ai4privacy/pii-masking-300k) dataset you can keep these and add your `entities` e.g. `AUT_ID_CARD` that are present in the dataset.

```python
core_labels = [
    # Inside your train() function, replace labels
    "BOD", "BUILDING", "CARDISSUER", "CITY", "COUNTRY", "DATE",
    "DRIVERLICENSE", "EMAIL", "GEOCOORD", "GIVENNAME1", "GIVENNAME2",
    "IDCARD", # General ID, consider if needed alongside specific Austrian IDs
    "AUSTRIAN_ID_CARD", # Your new Austrian ID Card entity
    # Add other existing PII types you want to keep detecting e.g.:
    "IP", "LASTNAME1", "LASTNAME2", "LASTNAME3", "PASS", "PASSPORT",
    "POSTCODE", "SECADDRESS", "SEX", "SOCIALNUMBER", # Consider "AUSTRIAN_SVNR"
    "STATE", "STREET", "TEL", "TIME", "TITLE", "USERNAME",
    # Add any other Austrian-specific PII types
    # "AUSTRIAN_TAX_ID", "AUSTRIAN_PASSPORT" (if distinct), etc.
]
```

Ensure the label strings in your `privacy_mask` (Step 1) exactly match the names in this `core_labels` list.

#### 2.2. Adjust the pretrained transfomer

Change the `pretrained_name` variable to a model suitable for German or multilingual text. For Austrian data, `distilbert-base-multilingual-cased` is a good starting point, as GUARD's current PII model is based on it.

#### 2.3. Adjust the dataset loading logic

```python
# Inside the train() function in train.py

# ds = load_dataset("ai4privacy/pii-masking-300k") # Original line
# Load your local Austrian dataset files
ds = load_dataset("json", data_files={
    "train": "path/to/your/austrian_train.jsonl",
    "validation": "path/to/your/austrian_validation.jsonl"
    # "test": "path/to/your/austrian_test.jsonl" # Optional test set
})

# This may need to be adjusted depending on your dataset (Augmented or new dataset)
# When your dataset contains samples for only one language, consider chosing a pretrained model that *only* supports
# that langauge. Otherwise, stick to the multilingual model and adjust the supported_langs variable

supported_langs = {"de"} # Add it, en or others if your dataset contains these.
ds["train"] = ds["train"].filter(lambda x: x["language"] in supported_langs)
ds["validation"] = ds["validation"].filter(lambda x: x["language"] in supported_langs)
```

#### 2.4. Adjust data processing if needed

After loading the data, the `train.py` script processes the data. For each sample the `tokenize` function is called, which takes the `source_text` and `privacy_mask` contents of the sample and tokenizes them. Then the function returns a new dictionary that includes things like `input_ids`, `attention_mask`, and `labels`.

Then the map calls `remove_columns` to reduce the dataset size, and removes elements that are **not** needed anymore after tokenization.

```python
# Inside the train() function, after loading 'ds'

# The .map call applies the tokenize function.
# Make sure 'labels2int' (label2id in our case) is correctly passed.
# The 'remove_columns' list might need adjustment based on your JSONL structure.
# If your JSONL only has 'source_text' and 'privacy_mask',
# those are already handled by the tokenize function and typically removed.
# Any extra columns you might have added (e.g., 'doc_id') should be listed here if not needed.
processed_ds = ds.map(
    partial(tokenize, labels2int=label2id, tokenizer=tokenizer, iob=True, ignore_subwords=True), # Ensure 'tokenize' and its args are correctly defined/passed
    batched=False, # The example tokenize function processes single examples
    remove_columns=[
        # Original columns from your dataset that are processed and can be removed:
        "source_text",
        "privacy_mask",
        # Add any other original columns from your austrian_*.jsonl files
        # that are not features for the model e.g. "document_id", "annotator_name"
    ],
    # num_proc can be increased based on your CPU cores
).remove_columns(["offset_mapping"]) # offset_mapping is returned by the tokenizer to track character positions; it’s no longer needed after labels are aligned
```

#### 2.5. Adjust the training parameters

Adjust the TrainingArguments to set the output directory, training duration, batch sizes, etc. You may keep the original setttings, or change them for testing, e.g. less epochs ...

```python
# Inside the train() function in train.py

training_arguments = TrainingArguments(
    output_dir="./austrian_pii_model_finetuned", # Define your model output path
    # num_train_epochs=3, # A common starting point
    max_steps=10000, # Alternative to epochs, adjust based on dataset size & batch size
    per_device_train_batch_size=16, # Adjust based on GPU memory
    per_device_eval_batch_size=32,  # Adjust based on GPU memory
    learning_rate=3e-5, # Common learning rate for fine-tuning
    weight_decay=0.01,
    warmup_ratio=0.1, # Or warmup_steps
    evaluation_strategy="steps", # Evaluate during training
    eval_steps=500,             # How often to evaluate
    save_strategy="steps",
    save_steps=500,             # How often to save checkpoints
    load_best_model_at_end=True,
    metric_for_best_model="f1", # Ensure your compute_metrics returns this
    greater_is_better=True,
    # report_to="wandb", # Set to "none" or remove if not using Weights & Biases
    report_to="none",
    # push_to_hub=True, # Set to False if not pushing to Hugging Face Hub
    push_to_hub=False,
    # hub_model_id="your_username/austrian_pii_model", # If pushing to hub
    overwrite_output_dir=True,
    # ... other arguments as needed ...
)

```
---

### 3. Train the model

Training the model will output the results in the specified `output_dir` set in the `training_arguments` e.g.  ./austrian_pii_model_finetuned.

```python
python train.py
```
---

### 4. Use the model

After training completes, the best version of your fine-tuned model will be saved in the directory specified by `output_dir` in TrainingArguments.
This directory will contain the model weights (pytorch_model.bin or model.safetensors), tokenizer configuration (tokenizer_config.json, vocab.txt or tokenizer.json), and model configuration (config.json).

You can then load this model for inference in your GUARD application. Simplest approach is to push the model to the `Huggingface Hub` and refer to them in your `guard/processing/config/full_analyzer_config.yaml` file under:

```yaml
nlp_configuration:
  models:
  - lang_code: en
    model_name:
      spacy: en_core_web_lg
      transformers: <path_to_HF_model>
  - lang_code: de
    model_name:
      spacy: de_core_news_lg
      transformers: <path_to_HF_model>
  - lang_code: it
    model_name:
      spacy: it_core_news_lg
      transformers: <path_to_HF_model>
```

You may also need to adjust in:

```yaml
model_to_presidio_entity_mapping:
    AUSTRIAN_ID_CARD: AUSTRIAN_ID_CARD
    AUT_TAX_ID: AUT_TAX_ID
```