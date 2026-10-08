import math
from typing import Any

import torch
from skimage.color import deltaE_ciede2000, rgb2lab


def evaluate(
    original: torch.Tensor,
    reconstructed: torch.Tensor,
    shape: tuple[int, int],
) -> dict[str, Any]:
    """Calculate RGB reconstruction and CIEDE2000 color error metrics."""
    difference = original - reconstructed
    mean_squared_error = float((difference * difference).mean())
    original_array = original.detach().cpu().numpy().reshape(*shape, 3)
    reconstructed_array = (
        reconstructed.detach().cpu().numpy().reshape(*shape, 3)
    )
    delta_e = deltaE_ciede2000(
        rgb2lab(original_array),
        rgb2lab(reconstructed_array),
    )

    return {
        "quantization_error": float(torch.norm(difference, dim=1).mean()),
        "mae_rgb": float(difference.abs().mean()),
        "mse_rgb": mean_squared_error,
        "rmse_rgb": math.sqrt(mean_squared_error),
        "psnr": (
            float("inf")
            if mean_squared_error == 0
            else 10 * math.log10(1 / mean_squared_error)
        ),
        "mean_delta_e": float(delta_e.mean()),
        "std_delta_e": float(delta_e.std()),
        "max_delta_e": float(delta_e.max()),
        "delta_e_map": delta_e,
    }


def usage(assignments: torch.Tensor, prototype_count: int) -> dict[str, Any]:
    """Summarize prototype activation counts and assignment entropy."""
    counts = torch.bincount(
        assignments.cpu(),
        minlength=prototype_count,
    )
    probabilities = counts.float() / counts.sum()
    nonzero_probabilities = probabilities > 0

    return {
        "active_neurons": int((counts > 0).sum()),
        "inactive_neurons": int((counts == 0).sum()),
        "usage_entropy": float(
            -(
                probabilities[nonzero_probabilities]
                * probabilities[nonzero_probabilities].log2()
            ).sum()
        ),
        "counts": counts.numpy(),
    }


def topology(
    model: Any,
    image_pixels: torch.Tensor,
    model_kind: str,
    batch_size: int = 65536,
) -> float:
    """Calculate topographic error for SOM/GNG, or NaN for k-means."""
    if model_kind == "kmeans":
        return float("nan")

    best_matches = model.two_best(image_pixels, batch_size).cpu()
    if model_kind == "som":
        first_bmu = best_matches[:, 0]
        second_bmu = best_matches[:, 1]
        first_row = first_bmu // model.cols
        first_column = first_bmu % model.cols
        second_row = second_bmu // model.cols
        second_column = second_bmu % model.cols
        grid_distance = (first_row - second_row).abs() + (
            first_column - second_column
        ).abs()
        return float((grid_distance != 1).float().mean())

    graph_edges = set(model.edges)
    return sum(
        (
            min(int(first_node), int(second_node)),
            max(int(first_node), int(second_node)),
        )
        not in graph_edges
        for first_node, second_node in best_matches.numpy()
    ) / len(best_matches)
