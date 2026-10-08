"""Run the configured experiment matrix."""

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and normalize experiment configuration paths."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {config_path}"
        )

    with open(config_path, encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file) or {}

    config.setdefault("data_dir", "data/raw")
    config.setdefault("output_dir", "outputs")

    for key in ["data_dir", "output_dir"]:
        value = config[key]
        if not Path(value).is_absolute():
            config[key] = str(ROOT / value)

    required_keys = [
        "data_dir",
        "output_dir",
        "seeds",
        "capacities",
        "models",
    ]
    missing = [key for key in required_keys if key not in config]
    if missing:
        raise KeyError(
            f"Config inválido '{config_path}': faltam chaves obrigatórias: {missing}. "
            "Use config/experiments.yaml ou inclua data_dir/output_dir no arquivo."
        )

    return config


def main(argv: Sequence[str] | None = None) -> None:
    """Load experiment configuration and run every matrix combination."""
    from src.data.images import list_images
    from src.experiments.runner import aggregate, run

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/experiments.yaml")
    arguments = parser.parse_args(argv)

    config = load_config(arguments.config)
    images = list_images(config["data_dir"])
    print(f"{len(images)} imagens encontradas")

    for image_path in images:
        for model_name in config["models"]:
            for capacity in config["capacities"]:
                for seed in config["seeds"]:
                    print(image_path.name, model_name, capacity, seed)
                    run(image_path, model_name, capacity, seed, config)

    aggregate(config["output_dir"])


if __name__ == "__main__":
    main()
