from os import PathLike

import matplotlib.pyplot as plt
import numpy as np
import torch


def make_plots(
    original: torch.Tensor,
    reconstructed: torch.Tensor,
    shape: tuple[int, int],
    delta_e: np.ndarray,
    counts: np.ndarray,
    prototypes: torch.Tensor,
    path_prefix: str | PathLike[str],
    title: str,
    edges: list[tuple[int, int]] | None = None,
    seed: int = 13,
) -> None:
    """Save image comparisons, error summaries, and prototype plots."""
    original_array = original.cpu().numpy().reshape(*shape, 3)
    reconstructed_array = reconstructed.cpu().numpy().reshape(*shape, 3)
    output_prefix = str(path_prefix)

    figure, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].imshow(original_array)
    axes[0].set_title("Original")
    axes[1].imshow(reconstructed_array)
    axes[1].set_title(title)
    for axis in axes:
        axis.axis("off")
    figure.tight_layout()
    figure.savefig(f"{output_prefix}_comparison.png", dpi=150)
    plt.close(figure)

    figure, axis = plt.subplots()
    image = axis.imshow(delta_e, cmap="magma")
    axis.axis("off")
    axis.set_title("Mapa Delta E CIEDE2000")
    figure.colorbar(image, ax=axis)
    figure.savefig(f"{output_prefix}_deltae.png", dpi=150)
    plt.close(figure)

    rgb_difference = np.linalg.norm(
        original_array.reshape(-1, 3) - reconstructed_array.reshape(-1, 3),
        axis=1,
    )
    figure, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].hist(rgb_difference, bins=50)
    axes[0].set_title("Diferença RGB")
    axes[1].bar(range(len(counts)), counts)
    axes[1].set_title("Vitórias")
    figure.tight_layout()
    figure.savefig(f"{output_prefix}_hist.png", dpi=150)
    plt.close(figure)

    sampled_pixels = original.cpu().numpy()
    prototype_array = prototypes.cpu().numpy()
    random_generator = np.random.default_rng(seed)
    sampled_pixels = sampled_pixels[
        random_generator.choice(
            len(sampled_pixels),
            min(10000, len(sampled_pixels)),
            replace=False,
        )
    ]
    figure = plt.figure()
    axis = figure.add_subplot(111, projection="3d")
    axis.scatter(
        sampled_pixels[:, 0],
        sampled_pixels[:, 1],
        sampled_pixels[:, 2],
        c=sampled_pixels,
        s=2,
        alpha=0.12,
    )
    axis.scatter(
        prototype_array[:, 0],
        prototype_array[:, 1],
        prototype_array[:, 2],
        c=prototype_array,
        edgecolor="black",
        s=40,
    )

    if edges:
        for first_node, second_node in edges:
            axis.plot(
                prototype_array[[first_node, second_node], 0],
                prototype_array[[first_node, second_node], 1],
                prototype_array[[first_node, second_node], 2],
                color="black",
                lw=0.6,
            )

    axis.set_xlabel("R")
    axis.set_ylabel("G")
    axis.set_zlabel("B")
    figure.savefig(f"{output_prefix}_rgb.png", dpi=150)
    plt.close(figure)
