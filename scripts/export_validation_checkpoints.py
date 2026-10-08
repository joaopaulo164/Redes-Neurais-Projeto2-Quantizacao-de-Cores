import argparse
import csv
import json
from pathlib import Path
from typing import Any

import torch


def tensor_information(value: Any) -> dict[str, Any] | None:
    """Return shape, dtype, size, and numeric summary for a tensor."""
    if not isinstance(value, torch.Tensor):
        return None

    tensor = value.detach().cpu()

    information = {
        "shape": list(tensor.shape),
        "dtype": str(tensor.dtype),
        "numel": tensor.numel(),
    }

    if tensor.numel() > 0:
        tensor_float = tensor.float()

        information.update(
            {
                "minimum": float(tensor_float.min().item()),
                "maximum": float(tensor_float.max().item()),
                "mean": float(tensor_float.mean().item()),
            }
        )

    return information


def load_checkpoint(path: Path) -> Any:
    """Load a checkpoint on CPU, supporting older PyTorch releases."""
    try:
        return torch.load(
            path,
            map_location="cpu",
            weights_only=True,
        )
    except TypeError:
        return torch.load(
            path,
            map_location="cpu",
        )


def export_history(
    history: list[dict[str, Any]],
    output_path: Path,
) -> bool:
    """Write checkpoint history records to CSV when history is available."""
    if not history:
        return False

    all_fields = []

    for record in history:
        for field in record:
            if field not in all_fields:
                all_fields.append(field)

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=all_fields,
        )

        writer.writeheader()

        for record in history:
            writer.writerow(record)

    return True


def export_edges(edges: Any, output_path: Path) -> bool:
    """Write graph edge endpoints and ages to CSV."""
    if not edges:
        return False

    rows = []

    if isinstance(edges, dict):
        for edge, age in edges.items():
            first_node, second_node = edge

            rows.append(
                {
                    "node_a": int(first_node),
                    "node_b": int(second_node),
                    "age": int(age),
                }
            )

    elif isinstance(edges, (list, tuple)):
        for edge in edges:
            if len(edge) == 2:
                first_node, second_node = edge
                age = ""

            elif len(edge) >= 3:
                first_node, second_node, age = edge[:3]

            else:
                continue

            rows.append(
                {
                    "node_a": int(first_node),
                    "node_b": int(second_node),
                    "age": age,
                }
            )

    if not rows:
        return False

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "node_a",
                "node_b",
                "age",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    return True


def export_checkpoint(
    checkpoint_path: Path,
    output_directory: Path,
) -> dict[str, Any]:
    """Export one checkpoint into a summary and optional CSV artifacts."""
    state = load_checkpoint(checkpoint_path)

    if not isinstance(state, dict):
        raise TypeError("O checkpoint não contém um dicionário.")

    model = state.get(
        "model",
        "unknown",
    )

    stem = checkpoint_path.stem
    checkpoint_output = output_directory / stem

    checkpoint_output.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = {
        "checkpoint": checkpoint_path.name,
        "model": model,
        "keys": list(state.keys()),
    }

    history = state.get(
        "history",
        [],
    )

    history_path = checkpoint_output / "history.csv"

    summary["history_exported"] = export_history(
        history,
        history_path,
    )

    summary["history_records"] = len(history)

    for key, value in state.items():
        information = tensor_information(value)

        if information is not None:
            summary[key] = information

    if model == "som":
        summary["rows"] = state.get("rows")
        summary["cols"] = state.get("cols")

        weights = state.get("weights")

        if isinstance(weights, torch.Tensor):
            summary["number_of_prototypes"] = int(weights.shape[0])

    elif model == "gng":
        weights = state.get("weights")
        edges = state.get("edges", {})

        if isinstance(weights, torch.Tensor):
            summary["number_of_nodes"] = int(weights.shape[0])

        summary["number_of_edges"] = len(edges)

        edges_path = checkpoint_output / "edges.csv"

        summary["edges_exported"] = export_edges(
            edges,
            edges_path,
        )

    elif model == "kmeans":
        centroids = state.get("centroids")

        if isinstance(
            centroids,
            torch.Tensor,
        ):
            summary["number_of_centroids"] = int(centroids.shape[0])

    summary_path = checkpoint_output / "summary.json"

    with summary_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return summary


def main() -> None:
    """Export all checkpoints from the configured input directory."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--checkpoints",
        default="outputs/checkpoints",
    )

    parser.add_argument(
        "--output",
        default="validation/checkpoints",
    )

    args = parser.parse_args()

    checkpoints_directory = Path(args.checkpoints)

    output_directory = Path(args.output)

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    checkpoint_paths = sorted(checkpoints_directory.glob("*.pt"))

    if not checkpoint_paths:
        raise FileNotFoundError(
            f"Nenhum arquivo .pt encontrado em {checkpoints_directory}"
        )

    index: list[dict[str, str]] = []

    for checkpoint_path in checkpoint_paths:
        print(
            "Exportando:",
            checkpoint_path.name,
        )

        try:
            summary = export_checkpoint(
                checkpoint_path,
                output_directory,
            )

            index.append(
                {
                    "checkpoint": checkpoint_path.name,
                    "model": summary["model"],
                    "status": "success",
                    "error": "",
                }
            )

        except Exception as error:
            index.append(
                {
                    "checkpoint": checkpoint_path.name,
                    "model": "",
                    "status": "error",
                    "error": str(error),
                }
            )

            print(
                "Erro:",
                checkpoint_path.name,
                error,
            )

    index_path = output_directory / "checkpoint_index.csv"

    with index_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "checkpoint",
                "model",
                "status",
                "error",
            ],
        )

        writer.writeheader()
        writer.writerows(index)

    print()
    print(
        "Exportação concluída em:",
        output_directory,
    )

    successful = sum(row["status"] == "success" for row in index)

    print(
        "Checkpoints exportados:",
        successful,
    )

    print(
        "Falhas:",
        len(index) - successful,
    )


if __name__ == "__main__":
    main()
