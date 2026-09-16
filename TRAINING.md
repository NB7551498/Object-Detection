# VisionAI — Training Guide

This document covers every step needed to train YOLOv8 rigorously on your own dataset using [`train.py`](train.py).

---

## 1. Quick start (prove the pipeline works in minutes)

```bash
# Uses COCO128 — downloads automatically (~7 MB), trains 50 epochs
python train.py
```

Outputs land in `runs/train/visionai_v1/`.

---

## 2. Common recipes

### Fine-tune on COCO128 — quick smoke test
```bash
python train.py --epochs 50 --batch 8 --model yolov8n.pt
```

### Production run on GPU (when available)
```bash
python train.py \
  --model yolov8s.pt \
  --dataset coco128 \
  --epochs 200 \
  --batch 32 \
  --imgsz 640 \
  --optimizer AdamW \
  --lr0 0.001 \
  --patience 20 \
  --name visionai_prod
```

### Train on your own dataset
```bash
python train.py \
  --dataset data/my_dataset.yaml \
  --epochs 150 \
  --model yolov8m.pt \
  --name my_custom_v1
```

---

## 3. Custom dataset setup

### Folder structure

```
data/
  my_dataset/
    images/
      train/   ← JPG/PNG training images
      val/     ← JPG/PNG validation images
      test/    ← JPG/PNG test images (optional)
    labels/
      train/   ← YOLO .txt annotation files
      val/
      test/
```

### Annotation format (one `.txt` per image)

```
<class_id> <x_center> <y_center> <width> <height>
```
All values normalised 0–1. Example:
```
0 0.512 0.348 0.234 0.416
2 0.744 0.621 0.108 0.192
```

### `data/my_dataset.yaml`

```yaml
path: data/my_dataset
train: images/train
val:   images/val
test:  images/test   # optional

nc: 3                # number of classes
names:
  0: person
  1: car
  2: bicycle
```

---

## 4. Model size guide

| Model | Params | mAP50-95 | Speed (CPU) | Use when |
|---|---|---|---|---|
| `yolov8n.pt` | 3.2M | 37.3 | Fastest | Demo / CPU-only |
| `yolov8s.pt` | 11.2M | 44.9 | Fast | Balanced accuracy |
| `yolov8m.pt` | 25.9M | 50.2 | Medium | Best on GPU |
| `yolov8l.pt` | 43.7M | 52.9 | Slow | High-accuracy GPU |
| `yolov8x.pt` | 68.2M | 53.9 | Slowest | Max accuracy |

---

## 5. Key hyperparameters explained

| Flag | Default | What it controls |
|---|---|---|
| `--lr0` | 0.001 | Initial learning rate. Lower for fine-tuning. |
| `--lrf` | 0.01 | Final LR = `lr0 × lrf`. Cosine decay target. |
| `--patience` | 15 | Early stopping: stops if mAP doesn't improve for N epochs. |
| `--batch` | 8 | Images per step. Double if you have more RAM. |
| `--imgsz` | 640 | Input resolution. 416 is faster; 1280 is more accurate. |
| `--mosaic` | 1.0 | Mosaic augmentation — critical for small objects. |
| `--mixup` | 0.1 | MixUp augmentation — helps generalisation. |
| `--close_mosaic` | 10 | Disables mosaic last N epochs for stable convergence. |
| `--cos_lr` | True | Cosine LR scheduler — almost always better than step. |

---

## 6. Interpreting results

After training, check `runs/train/visionai_v1/`:

```
weights/
  best.pt    ← use this
  last.pt    ← last epoch checkpoint

results.csv          ← per-epoch metrics (open in Excel/pandas)
confusion_matrix.png ← which classes get confused
F1_curve.png
PR_curve.png
labels.jpg           ← dataset label distribution
val_batch*.jpg       ← visual validation predictions
```

**Key metrics to watch:**
- `mAP50 > 0.70` — good
- `mAP50-95 > 0.50` — excellent
- Precision & Recall both above 0.65 — well-balanced

---

## 7. Use trained weights with the API

After training completes, `trained_model.pt` is copied to the repo root automatically.

Update [`app/config.py`](app/config.py):
```python
MODEL_NAME = os.getenv("MODEL_NAME", "trained_model.pt")
```

Or set the env variable before starting the server:
```bash
set MODEL_NAME=trained_model.pt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## 8. Tips for rigorous training

1. **Always validate your dataset first** — bad labels destroy training. Check `labels.jpg` in the results folder.
2. **Use at least 300 images per class** — less leads to overfitting.
3. **Match `--imgsz` to your deployment resolution** — training at 640, deploying at 640.
4. **Start with `yolov8n.pt`** to prove the pipeline, then scale up.
5. **Monitor `mAP50` not loss** — loss going down doesn't always mean mAP improving.
6. **Avoid very high LR on fine-tuning** — `lr0=0.0001` is safer when starting from a pre-trained checkpoint.
7. **`--patience 20`** is the minimum for real training; use 50 for production runs.
