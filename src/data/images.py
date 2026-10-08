"""Image loading, sampling, and saving helpers."""

from os import PathLike
from pathlib import Path

import numpy as np
import torch
from PIL import Image

EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def list_images(folder: str | PathLike[str]) -> list[Path]:
    """List supported image files in a directory.

    Args:
        folder: Directory to search.

    Returns:
        Supported image paths sorted by their path strings.
    """
    return sorted(
        path for path in Path(folder).iterdir() if path.suffix.lower() in EXT
    )


def load_image(
    path: str | PathLike[str],
    device: str = "cpu",
) -> tuple[torch.Tensor, tuple[int, int]]:
    """Load an RGB image as normalized PyTorch pixels.

    Args:
        path: Image file to load.
        device: Device on which to place the pixel tensor.

    Returns:
        A tuple of flattened RGB pixels in [0, 1] and the original height and
        width.
    """
    image_array = (
        np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    )
    height, width, _ = image_array.shape
    pixel_tensor = torch.from_numpy(image_array.reshape(-1, 3)).to(device)
    return pixel_tensor, (height, width)


def sample_pixels(
    pixels: torch.Tensor,
    sample_count: int,
    seed: int,
) -> torch.Tensor:
    """Select a reproducible random subset of pixels when needed.

    Args:
        pixels: Input pixel tensor.
        sample_count: Maximum number of pixels to return.
        seed: Seed for the device-local random generator.

    Returns:
        A clone of all pixels when they fit the limit, otherwise a randomly
        sampled subset.
    """
    if len(pixels) <= sample_count:
        return pixels.clone()

    generator = torch.Generator(device=pixels.device).manual_seed(seed)
    random_indices = torch.randperm(
        len(pixels),
        generator=generator,
        device=pixels.device,
    )[:sample_count]
    return pixels[random_indices]


def save_image(
    pixels: torch.Tensor,
    shape: tuple[int, int],
    path: str | PathLike[str],
) -> None:
    """Convert normalized RGB pixels to an image file.

    Args:
        pixels: Flattened RGB values to save.
        shape: Original image height and width.
        path: Destination image file.
    """
    image_array = pixels.detach().cpu().clamp(0, 1).reshape(*shape, 3).numpy()
    image = Image.fromarray((image_array * 255).round().astype("uint8"))
    image.save(path)
