# User Guide

This guide walks through what `bda-svc` does, how to run it locally, and how to control its behavior through environment variables and configuration files.

---

## What `bda-svc` does

`bda-svc` is an automated Battle Damage Assessment (BDA) service. Given post-strike imagery, it identifies doctrinally relevant targets, assesses the visible physical damage to each one, and produces a structured JSON report.

The system is designed to run locally, with no calls to external cloud services at inference time. All model inference happens against an OpenAI-compatible server (such as vLLM or Ollama) running on the same machine or local network.

### Pipeline at a glance

For each input image, the pipeline runs four stages:

1. **Detection** — A vision-language model (VLM) localizes targets that match doctrinal categories (e.g., buildings, military equipment) and produces a bounding box for each.
2. **Cropping** — Each detection is cropped from the source image with a configurable buffer for context.
3. **Per-target assessment** — A VLM evaluates damage on each target using both the cropped image and the full scene with the target outlined. Doctrinal definitions for the target's category are injected into the prompt.
4. **Scene summary** — A short scene-level summary is generated from the full image and the per-target assessments.

The detection and assessment models are configured independently. They can point at the same model or at different ones.

---

## Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** for environment and dependency management
- An **OpenAI-compatible model server** running locally or reachable on the network. Two common options:
    - [vLLM](https://docs.vllm.ai/en/latest/getting_started/installation/) (default port `8000`)
    - [Ollama](https://ollama.com/download) (default port `11434`)
- A directory of input images. Supported extensions: `.png`, `.jpg`, `.jpeg`, `.bmp`.

---

## Installation

```bash
git clone https://github.com/cmu-bda/bda-svc.git
cd bda-svc
uv sync
```

`uv sync` installs runtime dependencies into a local virtual environment. No global Python install is modified.

---

## Running the system

Start the model server first. Examples:

```bash
# vLLM
vllm serve Qwen/Qwen3-VL-8B-Instruct

# Ollama
ollama serve
ollama pull qwen3-vl:8b-instruct
```

Point `bda-svc` at the server (see [Environment variables](#environment-variables)) and run:

```bash
# Show help
uv run bda-svc -h

# Process the default input folder (./bda_input)
uv run bda-svc

# Process a single image
uv run bda-svc -i /path/to/image.jpg

# Process a folder of images (recursively)
uv run bda-svc -i /path/to/folder

# Specify an output folder
uv run bda-svc -i /path/to/folder -o /path/to/output
```

If `-i` is omitted, the input defaults to `./bda_input`. If `-o` is omitted, reports are written to `./bda_output`. Output filenames are timestamped, so repeat runs do not overwrite earlier reports.

---

## Environment variables

Four environment variables control runtime behavior. None are strictly required if you accept all defaults, but `OPENAI_BASE_URL` typically needs to be set to match your server.

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_BASE_URL` | `http://localhost:8000/v1` | URL of the OpenAI-compatible model server. |
| `OPENAI_API_KEY` | `no-auth` | API key, only required if your server enforces authentication. |
| `BDA_DETECTION_MODEL` | value from `config.yaml` | Override the detection model identifier. |
| `BDA_ASSESSMENT_MODEL` | value from `config.yaml` | Override the assessment model identifier. |

### `OPENAI_BASE_URL`

The URL the OpenAI client uses to reach your model server. The path must end in `/v1`.

```bash
export OPENAI_BASE_URL=http://localhost:8000/v1   # vLLM default
export OPENAI_BASE_URL=http://localhost:11434/v1  # Ollama default
```

### `OPENAI_API_KEY`

Most local servers don't enforce authentication, so the default `no-auth` placeholder works. Set this only if your server is configured to require a key.

### `BDA_DETECTION_MODEL` and `BDA_ASSESSMENT_MODEL`

These override the `model` field of `detection_vlm` and `assessment_vlm` in `config.yaml`. Useful when you want to swap models without editing the YAML — for example, when quickly testing a smaller model:

```bash
export BDA_DETECTION_MODEL=qwen3-vl:2b-instruct
export BDA_ASSESSMENT_MODEL=qwen3-vl:2b-instruct
uv run bda-svc -i ./bda_input
```

The model identifier format depends on your server. Ollama uses tags like `qwen3-vl:8b-instruct`; vLLM uses HuggingFace identifiers like `Qwen/Qwen3-VL-8B-Instruct`.

---

## Configuration: `config.yaml`

Pipeline behavior is controlled by [`src/bda_svc/pipeline/config.yaml`](https://github.com/cmu-bda/bda-svc/blob/main/src/bda_svc/pipeline/config.yaml). The file has three top-level blocks: `detection_vlm`, `assessment_vlm`, and `prompts`.

### `detection_vlm`

Configures the model and inference settings for the detection stage.

```yaml
detection_vlm:
  model: Qwen/Qwen3-VL-8B-Instruct
  bbox_convention: xyxy_1000
  temperature: 0.0
  max_image_size: 1024
  crop_buffer_ratio: 0.2
```

| Field | Description |
|---|---|
| `model` | Model identifier passed to the OpenAI server. Overridden by `BDA_DETECTION_MODEL`. |
| `bbox_convention` | The coordinate format the model returns. See [Bounding box conventions](#bounding-box-conventions) below. |
| `temperature` | Sampling temperature. `0.0` makes outputs deterministic — recommended for detection. |
| `max_image_size` | Largest side (px) the image is resized to before being sent to the model. Larger values increase quality but also increase inference time and memory. |
| `crop_buffer_ratio` | Padding ratio around each detection box when generating crops for assessment. `0.2` means 20% padding on each side. Larger values give the assessment stage more context but also more clutter. |

#### Bounding box conventions

VLMs differ in how they return bounding boxes. `bbox_convention` tells the pipeline how to interpret them. Two dimensions are encoded in the value:

- **Coordinate ordering**: `xyxy` (`xmin, ymin, xmax, ymax`) or `yxyx` (`ymin, xmin, ymax, xmax`).
- **Coordinate scale**: `_1` (normalized 0.0–1.0), `_1000` (normalized 0–1000), or `_pixels` (raw pixel values relative to the image sent to the model).

Valid values: `xyxy_1`, `yxyx_1`, `xyxy_1000`, `yxyx_1000`, `xyxy_pixels`, `yxyx_pixels`.

If you swap in a model that uses a different convention, change this field — otherwise detections will be silently dropped.

### `assessment_vlm`

Configures the model used for per-target damage assessment and scene summarization.

```yaml
assessment_vlm:
  model: Qwen/Qwen3-VL-8B-Instruct
  temperature: 0.0
  max_image_size: 1024
```

Fields are the same as `detection_vlm`, minus `bbox_convention` and `crop_buffer_ratio`. The assessment stage doesn't generate boxes, so those fields don't apply.

### `prompts`

Holds the four prompt templates used by the pipeline. Each is a multi-line string with placeholders that the pipeline fills in at runtime.

| Prompt | Used in | Placeholders |
|---|---|---|
| `system` | Every VLM call | none |
| `detect_objects` | Detection stage | `{categories}`, `{detection_guidance}`, `{bbox_format}`, `{bbox_scale}` |
| `assess_damage` | Per-target assessment | `{target_type}`, `{doctrine}` |
| `summarize_scene` | Scene summary | `{target_assessments}` |

The placeholders are substituted with values pulled from `doctrine.yaml`, the `bbox_convention` field, and prior pipeline output. For example, `{categories}` becomes a comma-separated list of all top-level keys in `doctrine.yaml`, and `{doctrine}` becomes the formatted physical-damage definitions for a single target's category.

You can edit the prompts directly to tune model behavior, but be careful — changing the schema instructions (e.g., the `OUTPUT SCHEMA` block) will break the JSON parsing downstream.

---

## Configuration: `doctrine.yaml`

[`src/bda_svc/pipeline/doctrine.yaml`](https://github.com/cmu-bda/bda-svc/blob/main/src/bda_svc/pipeline/doctrine.yaml) is the doctrinal grounding layer. It defines what targets the system looks for and how it categorizes damage.

The file is a top-level mapping from **target category** to a block of guidance:

```yaml
buildings:
  detection_guidance: |
    Detect only buildings that are central to the scene...
  physical_damage_definitions: |
    NO DAMAGE — 0 percent of the target element area damaged.
    LIGHT DAMAGE — Up to 15 percent of the target element area damaged.
    ...
  physical_damage_considerations: |
    Framed Buildings—Framed structures (e.g., military HQ, ...
```

Each category needs three fields:

| Field | Where it goes |
|---|---|
| `detection_guidance` | Injected into the detection prompt as `{detection_guidance}`. Tells the model what to look for under this category and what to skip. |
| `physical_damage_definitions` | Injected into the assessment prompt as part of `{doctrine}`. Defines the damage scale (e.g., `NO DAMAGE` → `DESTROYED`) for this category. |
| `physical_damage_considerations` | Also injected into `{doctrine}`. Provides extra context that helps the model interpret edge cases (e.g., differences between framed and load-bearing structures). |

### How categories drive the pipeline

The set of category keys (`buildings`, `military_equipment`) is the **set of doctrinal target types the system recognizes**. To add a new category:

1. Add a new top-level block to `doctrine.yaml` with all three fields.
2. The detection prompt automatically picks it up — no code changes needed.

The category names are also used as the `target_type` field in output reports, so keep them lowercase and underscore-separated.

### Why detection and assessment use different doctrine

Detection prompts get **all** category guidance at once, so the model can consider every possible target type when scanning a scene. Assessment prompts receive only the doctrine for the target's specific category, keeping the prompt focused and avoiding cross-category contamination of the damage scale.

---

## Output interpretation

Each input image produces one timestamped JSON report. Reports have three top-level fields:

```json
{
  "metadata": {
    "model_name": "detection=qwen3-vl:8b-instruct;assessment=qwen3-vl:8b-instruct",
    "image_filename": "example.jpg",
    "report_type": "PDA",
    "analyst": "bda-svc",
    "inference_time": "12.34"
  },
  "physical_damage": {
    "target_0": {
      "target_type": "military_equipment",
      "damage_category": "DESTROYED",
      "confidence_level": "PROBABLE",
      "brief_supporting_logic": "visible fire and heavy structural damage",
      "bounding_box": [73, 79, 113, 122]
    }
  },
  "summary": "One target assessed and reported as destroyed."
}
```

### `metadata`

Provenance information for the report — which models ran, on which file, when, and how long it took.

### `physical_damage`

A mapping from `target_<N>` to a per-target assessment. Each entry contains:

- **`target_type`** — the doctrinal category from `doctrine.yaml`.
- **`damage_category`** — one of the categories defined in that target type's `physical_damage_definitions`.
- **`confidence_level`** — `CONFIRMED`, `PROBABLE`, or `POSSIBLE`. The model is instructed to choose the lowest level consistent with visible evidence; high confidence should be rare.
- **`brief_supporting_logic`** — short factual observations supporting the assessment.
- **`bounding_box`** — `[xmin, ymin, xmax, ymax]` in pixel coordinates relative to the original input image.

If no targets are detected, `physical_damage` still contains a single entry with `target_type: "object_not_found"` and a zero bounding box, so downstream consumers always receive a structurally consistent report.

### `summary`

A short scene-level description generated after all per-target assessments. It enumerates the targets, summarizes the scene, and may briefly describe likely functional impact.

---

## Troubleshooting

### "Connection refused" or empty responses

Most often means `bda-svc` cannot reach the model server. Verify:

```bash
curl "$OPENAI_BASE_URL/models"
```

If that fails, check that the server is running, that the URL ends in `/v1`, and that any firewall rules permit traffic on the server's port.

### No detections in the output

If `physical_damage` consistently reports `object_not_found` even on images that clearly contain targets, two things to check:

1. **`bbox_convention` mismatch.** If the model's coordinate format doesn't match the configured value, every detection is silently dropped during validation. Try a different convention (e.g., switch from `xyxy_1000` to `xyxy_pixels`).
2. **Doctrine guidance too restrictive.** The `detection_guidance` field for each category may be filtering out valid targets. Loosen the language in `doctrine.yaml` and re-run.

### Slow inference

The dominant cost is image size and number of detections per scene. Tradeoffs:

- Lower `max_image_size` in both VLM blocks (2048 → 1024, for example).
- Use a smaller model via `BDA_DETECTION_MODEL` / `BDA_ASSESSMENT_MODEL`.
- Tighten `detection_guidance` so fewer targets are detected per scene.

### Invalid JSON from the model

The pipeline uses `json-repair` to recover from minor formatting issues, but persistent failures can indicate the prompt has been edited in a way that confuses the model's structured output. Revert to the default `prompts` block in `config.yaml` and re-introduce changes incrementally.
