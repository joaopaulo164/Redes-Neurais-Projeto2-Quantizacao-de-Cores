"""Run one configured color-quantization experiment."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main(argv: Sequence[str] | None = None) -> None:
    """Parse CLI arguments and execute the requested experiment."""
    from src.experiments.runner import run

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument(
        "--model",
        choices=["som", "gng", "kmeans"],
        required=True,
    )
    parser.add_argument(
        "--capacity",
        type=int,
        choices=[16, 64, 256],
        required=True,
    )
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--config", default="config/experiments.yaml")
    arguments = parser.parse_args(argv)

    with open(arguments.config, encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    print(
        run(
            arguments.image,
            arguments.model,
            arguments.capacity,
            arguments.seed,
            config,
        )
    )


if __name__ == "__main__":
    main()
