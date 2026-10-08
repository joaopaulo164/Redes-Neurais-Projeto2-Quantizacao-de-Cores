import torch

from src.models import GNG, SOM, TorchKMeans

PIXELS = torch.rand(120, 3)


def test_som() -> None:
    model = SOM(2, 2, epochs=1, batch_size=32).fit(PIXELS)
    reconstructed, _ = model.quantize(PIXELS)
    assert reconstructed.shape == PIXELS.shape


def test_kmeans() -> None:
    model = TorchKMeans(4, max_iter=3).fit(PIXELS)
    reconstructed, _ = model.quantize(PIXELS)
    assert reconstructed.shape == PIXELS.shape


def test_gng() -> None:
    model = GNG(4, steps=50, insertion_interval=10).fit(PIXELS)
    reconstructed, _ = model.quantize(PIXELS)
    assert reconstructed.shape == PIXELS.shape
    assert len(model.prototypes()) <= 4
