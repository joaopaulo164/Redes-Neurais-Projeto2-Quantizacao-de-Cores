import csv
import re
from pathlib import Path

import numpy as np
from PIL import Image

INPUT_DIRECTORY = Path("outputs/reconstructed")

OUTPUT_FILE = Path("validation/validation_unique_colors.csv")


PATTERN = re.compile(
    r"^(?P<image>.+)_"
    r"(?P<model>som|gng|kmeans)_"
    r"(?P<capacity>16|64|256)_"
    r"s(?P<seed>\d+)$"
)


def main() -> None:
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = []

    for image_path in sorted(INPUT_DIRECTORY.glob("*.png")):
        match = PATTERN.match(image_path.stem)

        if match is None:
            print(
                "Nome não reconhecido:",
                image_path.name,
            )
            continue

        image = np.asarray(Image.open(image_path).convert("RGB"))

        colors = np.unique(
            image.reshape(-1, 3),
            axis=0,
        )

        capacity = int(match.group("capacity"))

        unique_colors = len(colors)

        rows.append(
            {
                "file_name": image_path.name,
                "image_name": match.group("image"),
                "model": match.group("model"),
                "capacity": capacity,
                "seed": int(match.group("seed")),
                "unique_colors": unique_colors,
                "valid": unique_colors <= capacity,
            }
        )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "file_name",
                "image_name",
                "model",
                "capacity",
                "seed",
                "unique_colors",
                "valid",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    invalid = [row for row in rows if not row["valid"]]

    print(
        "Reconstruções verificadas:",
        len(rows),
    )

    print(
        "Reconstruções válidas:",
        len(rows) - len(invalid),
    )

    print(
        "Reconstruções inválidas:",
        len(invalid),
    )

    print(
        "Arquivo gerado:",
        OUTPUT_FILE,
    )


if __name__ == "__main__":
    main()
