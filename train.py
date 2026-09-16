# VisionAI — YOLOv8 Rigorous Training Pipeline
#
# Usage:
#   python train.py                    # full run with defaults
#   python train.py --epochs 100 --model yolov8s.pt
#   python train.py --dataset custom --data data/custom.yaml
#
# Outputs:
#   runs/train/<exp>/  — weights, metrics, confusion matrix, val curves
#   runs/val/<exp>/    — post-training evaluation results
#   trained_model.pt   — symlink/copy of best weights at repo root

import argparse
import os
import shutil
import sys
import time
from pathlib import Path

# ── Dependency guard ──────────────────────────────────────────────────────────
try:
    from ultralytics import YOLO
    import torch
    import yaml
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("Run:  pip install ultralytics torch torchvision")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULTS = {
    # Base model — nano for CPU, switch to yolov8s/m for GPU
    "model": "yolov8n.pt",

    # Dataset — "coco128" downloads automatically (good for proving the pipeline).
    # Replace with your custom data.yaml path for production training.
    "dataset": "coco128",

    # Training hyperparameters
    "epochs": 50,
    "imgsz": 640,
    "batch": 8,           # lower if OOM on CPU
    "workers": 4,
    "patience": 15,       # early stopping patience (epochs without mAP gain)

    # Optimizer
    "optimizer": "AdamW", # SGD | AdamW | Adam
    "lr0": 0.001,         # initial learning rate
    "lrf": 0.01,          # final lr = lr0 * lrf
    "momentum": 0.937,
    "weight_decay": 0.0005,
    "warmup_epochs": 3.0,
    "warmup_bias_lr": 0.1,

    # Augmentation (Albumentations-style in ultralytics)
    "hsv_h": 0.015,       # hue augmentation
    "hsv_s": 0.7,         # saturation augmentation
    "hsv_v": 0.4,         # value/brightness augmentation
    "degrees": 10.0,      # rotation ±degrees
    "translate": 0.1,     # translation fraction
    "scale": 0.5,         # scale ± gain
    "shear": 2.0,         # shear ±degrees
    "perspective": 0.0001,
    "flipud": 0.05,       # vertical flip probability
    "fliplr": 0.5,        # horizontal flip probability
    "mosaic": 1.0,        # mosaic augmentation probability
    "mixup": 0.1,         # mixup augmentation probability
    "copy_paste": 0.1,    # segment copy-paste probability

    # Loss weights
    "box": 7.5,
    "cls": 0.5,
    "dfl": 1.5,

    # Output
    "project": "runs/train",
    "name": "visionai_v1",
    "exist_ok": False,    # set True to resume / overwrite
    "save_period": 10,    # save checkpoint every N epochs

    # Device
    "device": "cuda" if torch.cuda.is_available() else "cpu",

    # Eval after training
    "run_val": True,
    "conf_threshold": 0.25,
    "iou_threshold": 0.6,
}


# ═══════════════════════════════════════════════════════════════════════════════
# Dataset YAML builder (for custom dataset)
# ═══════════════════════════════════════════════════════════════════════════════

def ensure_dataset_yaml(dataset_arg: str) -> str:
    """
    If dataset_arg is a built-in name (coco128, coco, VOC, etc.) return it as-is
    so Ultralytics downloads it. If it's a path to a .yaml, validate and return it.
    Otherwise raise.
    """
    builtin = {"coco128", "coco", "coco8", "voc", "objects365", "open-images-v7"}
    if dataset_arg.lower() in builtin:
        print(f"[Dataset] Using built-in Ultralytics dataset: {dataset_arg}")
        return dataset_arg

    p = Path(dataset_arg)
    if p.suffix in {".yaml", ".yml"} and p.exists():
        print(f"[Dataset] Using custom dataset YAML: {p}")
        return str(p)

    # Create a template yaml
    if not p.suffix:
        yaml_path = Path("data") / f"{dataset_arg}.yaml"
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        template = {
            "path": str(Path("data") / dataset_arg),
            "train": "images/train",
            "val": "images/val",
            "test": "images/test",
            "nc": 80,
            "names": {
                i: f"class_{i}" for i in range(80)
            }
        }
        yaml_path.write_text(yaml.dump(template, sort_keys=False), encoding="utf-8")
        print(f"[Dataset] Created template YAML at {yaml_path}")
        print("          Edit it to match your dataset before training.")
        return str(yaml_path)

    raise FileNotFoundError(f"Dataset not found: {dataset_arg}")


# ═══════════════════════════════════════════════════════════════════════════════
# Training
# ═══════════════════════════════════════════════════════════════════════════════

def train(cfg: dict) -> Path:
    print("\n" + "═" * 60)
    print("  VisionAI — YOLOv8 Rigorous Training Pipeline")
    print("═" * 60)
    print(f"  Model    : {cfg['model']}")
    print(f"  Dataset  : {cfg['dataset']}")
    print(f"  Epochs   : {cfg['epochs']}  (patience={cfg['patience']})")
    print(f"  Image sz : {cfg['imgsz']}")
    print(f"  Batch    : {cfg['batch']}")
    print(f"  Device   : {cfg['device'].upper()}")
    print(f"  Optimizer: {cfg['optimizer']}  lr0={cfg['lr0']}  lrf={cfg['lrf']}")
    print("═" * 60 + "\n")

    # Load model
    model = YOLO(cfg["model"])

    dataset = ensure_dataset_yaml(cfg["dataset"])

    t0 = time.time()
    results = model.train(
        data=dataset,
        epochs=cfg["epochs"],
        imgsz=cfg["imgsz"],
        batch=cfg["batch"],
        workers=cfg["workers"],
        patience=cfg["patience"],

        optimizer=cfg["optimizer"],
        lr0=cfg["lr0"],
        lrf=cfg["lrf"],
        momentum=cfg["momentum"],
        weight_decay=cfg["weight_decay"],
        warmup_epochs=cfg["warmup_epochs"],
        warmup_bias_lr=cfg["warmup_bias_lr"],

        # Augmentation
        hsv_h=cfg["hsv_h"],
        hsv_s=cfg["hsv_s"],
        hsv_v=cfg["hsv_v"],
        degrees=cfg["degrees"],
        translate=cfg["translate"],
        scale=cfg["scale"],
        shear=cfg["shear"],
        perspective=cfg["perspective"],
        flipud=cfg["flipud"],
        fliplr=cfg["fliplr"],
        mosaic=cfg["mosaic"],
        mixup=cfg["mixup"],
        copy_paste=cfg["copy_paste"],

        # Loss weights
        box=cfg["box"],
        cls=cfg["cls"],
        dfl=cfg["dfl"],

        # I/O
        project=cfg["project"],
        name=cfg["name"],
        exist_ok=cfg["exist_ok"],
        save_period=cfg["save_period"],
        device=cfg["device"],

        # Extras
        plots=True,        # save training curves, confusion matrix
        save=True,         # save best + last weights
        cache=False,       # set True if RAM permits (speeds up epochs)
        rect=False,        # rectangular training (slightly faster, disables mosaic)
        cos_lr=True,       # cosine LR scheduler
        close_mosaic=10,   # disable mosaic last N epochs for stability
        amp=torch.cuda.is_available(),  # AMP only on GPU
        label_smoothing=0.0,
        nms=False,
    )
    elapsed = time.time() - t0

    # Locate best weights
    run_dir = Path(cfg["project"]) / cfg["name"]
    best_pt = run_dir / "weights" / "best.pt"
    if not best_pt.exists():
        # ultralytics may append a number suffix
        candidates = sorted(Path(cfg["project"]).glob(f"{cfg['name']}*/weights/best.pt"))
        if candidates:
            best_pt = candidates[-1]
            run_dir = best_pt.parent.parent

    print(f"\n[Train] Finished in {elapsed/60:.1f} min")
    print(f"[Train] Best weights : {best_pt}")

    return best_pt, run_dir


# ═══════════════════════════════════════════════════════════════════════════════
# Validation / Evaluation
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate(best_pt: Path, cfg: dict):
    print("\n" + "─" * 60)
    print("  Post-training Evaluation")
    print("─" * 60)

    dataset = ensure_dataset_yaml(cfg["dataset"])
    model = YOLO(str(best_pt))

    metrics = model.val(
        data=dataset,
        imgsz=cfg["imgsz"],
        batch=cfg["batch"],
        conf=cfg["conf_threshold"],
        iou=cfg["iou_threshold"],
        device=cfg["device"],
        plots=True,
        project="runs/val",
        name=cfg["name"],
        exist_ok=True,
    )

    print("\n  ── Key Metrics ──────────────────────────────")
    try:
        print(f"  mAP50       : {metrics.box.map50:.4f}")
        print(f"  mAP50-95    : {metrics.box.map:.4f}")
        print(f"  Precision   : {metrics.box.mp:.4f}")
        print(f"  Recall      : {metrics.box.mr:.4f}")
    except Exception:
        print(f"  Raw results : {metrics}")
    print("─" * 60)

    return metrics


# ═══════════════════════════════════════════════════════════════════════════════
# Export best weights to repo root for the API to pick up
# ═══════════════════════════════════════════════════════════════════════════════

def export_weights(best_pt: Path, out_name: str = "trained_model.pt"):
    dest = Path(out_name)
    shutil.copy2(best_pt, dest)
    print(f"\n[Export] Saved best weights -> {dest.resolve()}")
    print(f"[Export] Set MODEL_NAME={out_name} env var or update app/config.py to use it.")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="VisionAI — Rigorous YOLOv8 training pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--model",    default=DEFAULTS["model"],   help="Base YOLO weights (yolov8n.pt / yolov8s.pt / yolov8m.pt)")
    p.add_argument("--dataset",  default=DEFAULTS["dataset"], help="Built-in name (coco128) or path to data.yaml")
    p.add_argument("--epochs",   type=int,   default=DEFAULTS["epochs"])
    p.add_argument("--imgsz",    type=int,   default=DEFAULTS["imgsz"])
    p.add_argument("--batch",    type=int,   default=DEFAULTS["batch"])
    p.add_argument("--workers",  type=int,   default=DEFAULTS["workers"])
    p.add_argument("--patience", type=int,   default=DEFAULTS["patience"])
    p.add_argument("--optimizer",            default=DEFAULTS["optimizer"], choices=["SGD","Adam","AdamW"])
    p.add_argument("--lr0",      type=float, default=DEFAULTS["lr0"])
    p.add_argument("--lrf",      type=float, default=DEFAULTS["lrf"])
    p.add_argument("--device",               default=DEFAULTS["device"])
    p.add_argument("--name",                 default=DEFAULTS["name"], help="Experiment name")
    p.add_argument("--project",              default=DEFAULTS["project"])
    p.add_argument("--exist-ok", action="store_true", default=DEFAULTS["exist_ok"])
    p.add_argument("--no-val",   action="store_true", help="Skip post-training evaluation")
    p.add_argument("--export",               default="trained_model.pt", help="Output filename at repo root")
    return p.parse_args()


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    args = parse_args()
    cfg = dict(DEFAULTS)
    cfg.update(vars(args))
    cfg["run_val"] = not args.no_val
    cfg["exist_ok"] = args.exist_ok

    best_pt, run_dir = train(cfg)

    if cfg["run_val"] and best_pt.exists():
        evaluate(best_pt, cfg)

    if best_pt.exists():
        export_weights(best_pt, cfg["export"])

    print(f"\n[Done] Training artefacts in: {run_dir.resolve()}")
    print("       To use the new model with the API:")
    print(f"       set MODEL_NAME={cfg['export']} and restart the server.")
