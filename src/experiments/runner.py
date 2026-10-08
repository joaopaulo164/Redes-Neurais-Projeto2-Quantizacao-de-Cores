from os import PathLike
from pathlib import Path
from time import perf_counter
from typing import Any

import pandas as pd
import torch

from src.data.images import load_image, sample_pixels, save_image
from src.metrics.evaluation import evaluate, topology, usage
from src.models import GNG, SOM, TorchKMeans
from src.visualization.plots import make_plots


def build(
    model_name: str,
    capacity: int,
    config: dict[str, Any],
    device: str,
    seed: int,
) -> Any:
    """Construct a quantizer using its model-specific configuration."""
    if model_name == "som":
        grid_size = int(capacity**0.5)
        return SOM(
            grid_size,
            grid_size,
            device=device,
            seed=seed,
            **config["som"],
        )
    if model_name == "gng":
        return GNG(capacity, device=device, seed=seed, **config["gng"])
    return TorchKMeans(
        capacity,
        device=device,
        seed=seed,
        **config["kmeans"],
    )


def run(
    image: str | PathLike[str],
    model_name: str,
    capacity: int,
    seed: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Run, evaluate, and persist one image quantization experiment."""
    device = config.get("device", "cpu")
    if device.startswith("cuda") and not torch.cuda.is_available():
        device = "cpu"

    output_dir = Path(config["output_dir"])
    output_subdirectories = [
        "checkpoints",
        "reconstructed",
        "figures",
        "metrics",
        "tables",
    ]
    for subdirectory in output_subdirectories:
        (output_dir / subdirectory).mkdir(parents=True, exist_ok=True)

    torch.manual_seed(seed)
    image_pixels, image_shape = load_image(image, device)
    training_pixels = sample_pixels(
        image_pixels,
        config["max_train_pixels"],
        seed,
    )
    model = build(model_name, capacity, config, device, seed)
    run_key = f"{Path(image).stem}_{model_name}_{capacity}_s{seed}"

    start_time = perf_counter()
    model.fit(training_pixels)
    training_time = perf_counter() - start_time

    start_time = perf_counter()
    reconstructed_pixels, assignments = model.quantize(
        image_pixels,
        config["inference_batch_size"],
    )
    inference_time = perf_counter() - start_time

    evaluation = evaluate(image_pixels, reconstructed_pixels, image_shape)
    neuron_usage = usage(assignments, len(model.prototypes()))
    topographic_error = topology(
        model,
        image_pixels,
        model_name,
        config["inference_batch_size"],
    )
    delta_e_map = evaluation.pop("delta_e_map")

    save_image(
        reconstructed_pixels,
        image_shape,
        output_dir / "reconstructed" / f"{run_key}.png",
    )
    make_plots(
        image_pixels,
        reconstructed_pixels,
        image_shape,
        delta_e_map,
        neuron_usage["counts"],
        model.prototypes(),
        output_dir / "figures" / run_key,
        f"{model_name.upper()} {capacity}",
        list(model.edges) if model_name == "gng" else None,
        seed,
    )
    model.save(output_dir / "checkpoints" / f"{run_key}.pt")

    result = {
        "run_id": run_key,
        "image_name": Path(image).name,
        "model": model_name,
        "capacity_requested": capacity,
        "capacity_actual": len(model.prototypes()),
        "seed": seed,
        "train_pixels": len(training_pixels),
        "total_pixels": len(image_pixels),
        **evaluation,
        "topographic_error": topographic_error,
        "active_neurons": neuron_usage["active_neurons"],
        "inactive_neurons": neuron_usage["inactive_neurons"],
        "usage_entropy": neuron_usage["usage_entropy"],
        "training_time_s": training_time,
        "inference_time_s": inference_time,
        "device": device,
    }

    metrics_path = output_dir / "metrics" / "runs.csv"
    pd.DataFrame([result]).to_csv(
        metrics_path,
        mode="a",
        header=not metrics_path.exists(),
        index=False,
    )
    return result


def aggregate(output_dir: str | PathLike[str] = "outputs") -> pd.DataFrame:
    """Aggregate experiment metrics by image, model, and capacity."""
    output_path = Path(output_dir)
    runs = pd.read_csv(output_path / "metrics" / "runs.csv")
    metric_columns = [
        "quantization_error",
        "topographic_error",
        "mae_rgb",
        "mse_rgb",
        "rmse_rgb",
        "psnr",
        "mean_delta_e",
        "std_delta_e",
        "max_delta_e",
        "active_neurons",
        "inactive_neurons",
        "usage_entropy",
        "training_time_s",
        "inference_time_s",
    ]
    summary = (
        runs.groupby(["image_name", "model", "capacity_requested"])[
            metric_columns
        ]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary.columns = [
        "_".join(str(column_part) for column_part in column if column_part)
        for column in summary.columns
    ]
    summary.to_csv(output_path / "tables" / "summary.csv", index=False)
    return summary
