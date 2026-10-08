"""
checkpoint_exporter.py

Módulo para exportar checkpoints (.pt) em múltiplos formatos auditáveis.

Suporta três tipos de quantizadores:
  - SOM (Self-Organizing Map): grid topológico com histórico por época
  - GNG (Growing Neural Gas): grafo adaptativo com histórico por passo
  - k-means: centróides com histórico por iteração

Exporta para: TXT (estrutural), CSV (resumo/histórico/protótipos/arestas),
JSON (manifesto), com validação cruzada contra runs.csv.
"""

import hashlib
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import torch

logger = logging.getLogger(__name__)


class CheckpointExporter:
    """Exporta checkpoints de quantizadores para formatos auditáveis."""

    FILENAME_PATTERN = re.compile(
        r"^(?P<image>.+)_(?P<model>som|gng|kmeans)_(?P<capacity>\d+)_s(?P<seed>\d+)$"
    )
    MODELS = {"som", "gng", "kmeans"}

    SUMMARY_COLUMNS = [
        "checkpoint",
        "image",
        "model",
        "capacity",
        "seed",
        "checkpoint_model_type",
        "history_state",
        "history_length",
        "som_rows",
        "som_cols",
        "som_num_neurons",
        "gng_num_nodes",
        "gng_num_edges",
        "num_centroids",
        "kmeans_inertia",
        "weights_shape",
        "weights_dtype",
        "centroids_shape",
        "centroids_dtype",
        "input_file_size_bytes",
        "input_sha256",
    ]

    HISTORY_COLUMNS = [
        "checkpoint",
        "image",
        "model",
        "capacity",
        "seed",
        "history_mode",
        "history_state",
        "history_index",
        "history_point",
        "epoch",
        "step",
        "iteration",
        "qe",
        "lr",
        "sigma",
        "nodes",
        "edges",
        "shift",
    ]

    PROTOTYPE_COLUMNS = [
        "checkpoint",
        "image",
        "model",
        "capacity",
        "seed",
        "unit_type",
        "unit_id",
        "r",
        "g",
        "b",
    ]

    EDGE_COLUMNS = [
        "checkpoint",
        "image",
        "model",
        "capacity",
        "seed",
        "node1",
        "node2",
        "age",
    ]

    CONSISTENCY_COLUMNS = [
        "checkpoint",
        "image",
        "model",
        "capacity",
        "seed",
        "checkpoint_key",
        "runs_csv_row_found",
        "validation_ok",
        "errors",
        "warnings",
    ]

    def __init__(
        self,
        checkpoint_dir: Path,
        output_dir: Path,
        runs_csv_path: Optional[Path] = None,
        trusted_checkpoints: bool = False,
        strict_mode: bool = False,
        logger_obj: Optional[logging.Logger] = None,
    ) -> None:
        self.checkpoint_dir = Path(checkpoint_dir)
        self.output_dir = Path(output_dir)
        self.runs_csv_path = Path(runs_csv_path) if runs_csv_path else None
        self.trusted_checkpoints = trusted_checkpoints
        self.strict_mode = strict_mode
        self.logger = logger_obj or logger

        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.checkpoint_dir.exists():
            msg = f"checkpoint_dir não existe: {self.checkpoint_dir}"
            if self.strict_mode:
                raise FileNotFoundError(msg)
            self.logger.warning(msg)

        self.runs_df = None
        if self.runs_csv_path and self.runs_csv_path.exists():
            try:
                self.runs_df = pd.read_csv(self.runs_csv_path)
                self.logger.info(
                    f"Carregado runs.csv com {len(self.runs_df)} linhas"
                )
            except Exception as error:
                msg = f"Erro ao carregar runs.csv: {error}"
                if strict_mode:
                    raise
                self.logger.warning(msg)

        self.exported_checkpoints: List[Dict[str, Any]] = []
        self._input_file_hashes: Dict[str, Dict[str, Any]] = {}
        self._runs_key_set: set[str] = self._build_runs_key_set()
        self.cross_validation_summary: Dict[str, Any] = {
            "runs_csv_available": self.runs_df is not None,
            "runs_csv_total_rows": int(len(self.runs_df))
            if self.runs_df is not None
            else 0,
            "runs_csv_unique_keys": int(len(self._runs_key_set)),
            "checkpoint_total": 0,
            "checkpoint_keys_found_in_runs": 0,
            "checkpoint_keys_missing_in_runs": 0,
            "runs_keys_missing_in_checkpoints": 0,
            "missing_in_runs": [],
            "missing_in_checkpoints": [],
        }

    @staticmethod
    def _sha256_file(path: Path) -> str:
        hash_object = hashlib.sha256()
        with path.open("rb") as checkpoint_file:
            for file_chunk in iter(
                lambda: checkpoint_file.read(1024 * 1024),
                b"",
            ):
                hash_object.update(file_chunk)
        return hash_object.hexdigest()

    @staticmethod
    def _safe_shape(value: Any) -> Optional[str]:
        if value is None:
            return None
        if hasattr(value, "shape"):
            return str(tuple(value.shape))
        return None

    def _checkpoint_key(
        self, image: str, model: str, capacity: int, seed: int
    ) -> str:
        return f"{image}_{model}_{capacity}_s{seed}"

    def _parse_run_id(
        self, run_id: str
    ) -> Optional[Tuple[str, str, int, int]]:
        if not isinstance(run_id, str):
            return None
        match = self.FILENAME_PATTERN.match(run_id.strip())
        if not match:
            return None
        parsed_values = match.groupdict()
        return (
            parsed_values["image"],
            parsed_values["model"],
            int(parsed_values["capacity"]),
            int(parsed_values["seed"]),
        )

    def _build_runs_key_set(self) -> set[str]:
        if self.runs_df is None or self.runs_df.empty:
            return set()

        keys = set()
        cols = set(self.runs_df.columns)

        if "run_id" in cols:
            for run_id in self.runs_df["run_id"].dropna().astype(str):
                parsed = self._parse_run_id(run_id)
                if parsed:
                    image, model, capacity, seed = parsed
                    keys.add(
                        self._checkpoint_key(image, model, capacity, seed)
                    )

        image_col = (
            "image"
            if "image" in cols
            else "image_name"
            if "image_name" in cols
            else None
        )
        model_col = "model" if "model" in cols else None
        cap_col = (
            "capacity"
            if "capacity" in cols
            else "capacity_requested"
            if "capacity_requested" in cols
            else None
        )
        seed_col = "seed" if "seed" in cols else None

        if image_col and model_col and cap_col and seed_col:
            for _, row in self.runs_df.iterrows():
                image_raw = row.get(image_col)
                if pd.isna(image_raw):
                    continue
                image_val = str(image_raw)
                if image_col == "image_name":
                    image_val = Path(image_val).stem
                if pd.isna(row.get(cap_col)) or pd.isna(row.get(seed_col)):
                    continue
                keys.add(
                    self._checkpoint_key(
                        image_val,
                        str(row.get(model_col)),
                        int(row.get(cap_col)),
                        int(row.get(seed_col)),
                    )
                )

        return keys

    def _history_state_and_length(
        self,
        checkpoint: Dict[str, Any],
    ) -> Tuple[str, Optional[int], List[Dict[str, Any]]]:
        if "history" not in checkpoint or checkpoint.get("history") is None:
            return "absent", None, []
        history = checkpoint.get("history")
        if not isinstance(history, list):
            return "invalid", None, []
        if len(history) == 0:
            return "empty", 0, []
        return "present", len(history), history

    def load_checkpoint(
        self, checkpoint_path: Path, trusted: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        trust = trusted if trusted is not None else self.trusted_checkpoints
        kwargs: Dict[str, Any] = {"map_location": "cpu"}
        kwargs["weights_only"] = False if trust else True
        try:
            ckpt = torch.load(checkpoint_path, **kwargs)
        except TypeError:
            kwargs.pop("weights_only", None)
            ckpt = torch.load(checkpoint_path, **kwargs)
        except Exception as error:
            self.logger.warning(
                f"Erro ao carregar {checkpoint_path.name}: {error}"
            )
            return None

        if not isinstance(ckpt, dict):
            self.logger.warning(
                f"{checkpoint_path.name}: checkpoint não é dict, é {type(ckpt)}"
            )
            return None

        return ckpt

    def _parse_filename(self, filename: str) -> Optional[Dict[str, str]]:
        base = filename[:-3] if filename.endswith(".pt") else filename
        match = self.FILENAME_PATTERN.match(base)
        if not match:
            self.logger.warning(f"Nome não segue padrão: {filename}")
            return None
        return match.groupdict()

    def _extract_metadata(
        self, ckpt: Dict[str, Any], parsed_name: Dict[str, str], basename: str
    ) -> Dict[str, Any]:
        model_type = ckpt.get("model")
        if model_type not in self.MODELS:
            self.logger.warning(f"Modelo desconhecido: {model_type}")
            model_type = "unknown"

        history_state, history_length, _ = self._history_state_and_length(ckpt)
        metadata: Dict[str, Any] = {
            "checkpoint": basename,
            "image": parsed_name["image"],
            "model": parsed_name["model"],
            "capacity": int(parsed_name["capacity"]),
            "seed": int(parsed_name["seed"]),
            "checkpoint_model_type": model_type,
            "history_state": history_state,
            "history_length": history_length,
            "som_rows": None,
            "som_cols": None,
            "som_num_neurons": None,
            "gng_num_nodes": None,
            "gng_num_edges": None,
            "num_centroids": None,
            "kmeans_inertia": None,
            "weights_shape": None,
            "weights_dtype": None,
            "centroids_shape": None,
            "centroids_dtype": None,
            "input_file_size_bytes": self._input_file_hashes.get(
                basename, {}
            ).get("size_bytes"),
            "input_sha256": self._input_file_hashes.get(basename, {}).get(
                "sha256"
            ),
        }

        if model_type == "som":
            rows = ckpt.get("rows")
            cols = ckpt.get("cols")
            metadata["som_rows"] = rows if rows is not None else None
            metadata["som_cols"] = cols if cols is not None else None
            if rows is not None and cols is not None:
                metadata["som_num_neurons"] = int(rows) * int(cols)
            weights = ckpt.get("weights")
            if weights is not None:
                metadata["weights_shape"] = self._safe_shape(weights)
                metadata["weights_dtype"] = str(weights.dtype)

        elif model_type == "gng":
            weights = ckpt.get("weights")
            if weights is not None:
                metadata["gng_num_nodes"] = int(weights.shape[0])
                metadata["weights_shape"] = self._safe_shape(weights)
                metadata["weights_dtype"] = str(weights.dtype)
            edges = ckpt.get("edges")
            if isinstance(edges, dict):
                metadata["gng_num_edges"] = len(edges)

        elif model_type == "kmeans":
            centroids = ckpt.get("centroids")
            if centroids is not None:
                metadata["num_centroids"] = int(centroids.shape[0])
                metadata["centroids_shape"] = self._safe_shape(centroids)
                metadata["centroids_dtype"] = str(centroids.dtype)
            if "inertia" in ckpt:
                metadata["kmeans_inertia"] = ckpt.get("inertia")

        return metadata

    def generate_structure_txt(
        self,
        ckpt: Dict[str, Any],
        basename: str,
    ) -> str:
        lines = []
        lines.append(f"Checkpoint: {basename}")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append("")

        model_type = ckpt.get("model")
        lines.append(f"Model Type: {model_type}")
        lines.append(f"Keys in Checkpoint: {', '.join(sorted(ckpt.keys()))}")
        lines.append("")

        if model_type == "som":
            lines.append("=== SOM (Self-Organizing Map) ===")
            rows = ckpt.get("rows")
            cols = ckpt.get("cols")
            lines.append(f"Grid: {rows} rows x {cols} cols")
            if rows is not None and cols is not None:
                lines.append(f"Neurons: {int(rows) * int(cols)}")
            weights = ckpt.get("weights")
            if weights is not None:
                lines.append(f"Weights Shape: {tuple(weights.shape)}")
                lines.append(f"Weights Dtype: {weights.dtype}")

        elif model_type == "gng":
            lines.append("=== GNG (Growing Neural Gas) ===")
            weights = ckpt.get("weights")
            if weights is not None:
                lines.append(f"Nodes: {weights.shape[0]}")
                lines.append(f"Weights Shape: {tuple(weights.shape)}")
                lines.append(f"Weights Dtype: {weights.dtype}")
            edges = ckpt.get("edges")
            if isinstance(edges, dict):
                lines.append(f"Edges: {len(edges)} connections")
            else:
                lines.append("Edges: absent")

        elif model_type == "kmeans":
            lines.append("=== k-means ===")
            centroids = ckpt.get("centroids")
            if centroids is not None:
                lines.append(f"Centroids: {centroids.shape[0]}")
                lines.append(f"Centroids Shape: {tuple(centroids.shape)}")
                lines.append(f"Centroids Dtype: {centroids.dtype}")
            lines.append(f"Inertia Present: {'inertia' in ckpt}")

        lines.append("")
        history_state, history_length, history = (
            self._history_state_and_length(ckpt)
        )
        if history_length is not None:
            lines.append(f"History: {history_length} records")
        lines.append(f"History State: {history_state}")
        lines.append(f"History Length: {history_length}")
        if history:
            lines.append(
                f"  First record keys: {', '.join(sorted(history[0].keys()))}"
            )
            lines.append(
                f"  Last record keys: {', '.join(sorted(history[-1].keys()))}"
            )

        return "\n".join(lines)

    def generate_summary_csv(self) -> pd.DataFrame:
        df = pd.DataFrame(self.exported_checkpoints)
        if df.empty:
            return df
        for col in self.SUMMARY_COLUMNS:
            if col not in df.columns:
                df[col] = None
        df = df[self.SUMMARY_COLUMNS]
        return df.sort_values(
            ["image", "model", "capacity", "seed"], kind="stable"
        ).reset_index(drop=True)

    def generate_history_csv(
        self,
        ckpt: Dict[str, Any],
        metadata: Dict[str, Any],
        stride: int = 1,
        history_mode: str = "full",
    ) -> List[Dict[str, Any]]:
        rows = []
        history_state, _, history = self._history_state_and_length(ckpt)

        base = {
            "checkpoint": metadata["checkpoint"],
            "image": metadata["image"],
            "model": metadata["model"],
            "capacity": metadata["capacity"],
            "seed": metadata["seed"],
            "history_mode": history_mode,
            "history_state": history_state,
        }

        if history_state in {"absent", "empty", "invalid"}:
            row = dict(base)
            row.update(
                {
                    "history_index": None,
                    "history_point": "state",
                    "epoch": None,
                    "step": None,
                    "iteration": None,
                    "qe": None,
                    "lr": None,
                    "sigma": None,
                    "nodes": None,
                    "edges": None,
                    "shift": None,
                }
            )
            return [row]

        if history_mode == "none":
            return []

        if history_mode == "summary":
            indices = [0] if len(history) == 1 else [0, len(history) - 1]
        else:
            stride = max(1, int(stride))
            indices = [
                idx for idx, _ in enumerate(history) if idx % stride == 0
            ]

        seen = set()
        for idx in indices:
            if idx in seen:
                continue
            seen.add(idx)
            record = history[idx]
            row = dict(base)
            row.update(
                {
                    "history_index": idx,
                    "history_point": "first"
                    if idx == 0
                    else "last"
                    if idx == len(history) - 1
                    else "sample",
                    "epoch": record.get("epoch")
                    if isinstance(record, dict)
                    else None,
                    "step": record.get("step")
                    if isinstance(record, dict)
                    else None,
                    "iteration": record.get("iteration")
                    if isinstance(record, dict)
                    else None,
                    "qe": record.get("qe")
                    if isinstance(record, dict)
                    else None,
                    "lr": record.get("lr")
                    if isinstance(record, dict)
                    else None,
                    "sigma": record.get("sigma")
                    if isinstance(record, dict)
                    else None,
                    "nodes": record.get("nodes")
                    if isinstance(record, dict)
                    else None,
                    "edges": record.get("edges")
                    if isinstance(record, dict)
                    else None,
                    "shift": record.get("shift")
                    if isinstance(record, dict)
                    else None,
                }
            )
            rows.append(row)

        return rows

    def generate_prototypes_csv(
        self,
        ckpt: Dict[str, Any],
        metadata: Dict[str, Any],
        max_rows: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = []
        model_type = ckpt.get("model")

        def append_tensor(tensor: Any, unit_type: str) -> None:
            if tensor is None:
                return
            vals = tensor.detach().cpu().numpy()
            for prototype_index in range(min(vals.shape[0], max_rows)):
                rows.append(
                    {
                        "checkpoint": metadata["checkpoint"],
                        "image": metadata["image"],
                        "model": metadata["model"],
                        "capacity": metadata["capacity"],
                        "seed": metadata["seed"],
                        "unit_type": unit_type,
                        "unit_id": prototype_index,
                        "r": float(vals[prototype_index, 0]),
                        "g": float(vals[prototype_index, 1]),
                        "b": float(vals[prototype_index, 2]),
                    }
                )

        if model_type == "som":
            append_tensor(ckpt.get("weights"), "neuron")
        elif model_type == "gng":
            append_tensor(ckpt.get("weights"), "node")
        elif model_type == "kmeans":
            append_tensor(ckpt.get("centroids"), "centroid")

        return rows

    def generate_edges_csv(
        self, ckpt: Dict[str, Any], metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        rows = []
        if ckpt.get("model") != "gng":
            return rows

        edges = ckpt.get("edges")
        if not isinstance(edges, dict):
            return rows

        for (node1, node2), age in sorted(
            edges.items(), key=lambda kv: (kv[0][0], kv[0][1])
        ):
            rows.append(
                {
                    "checkpoint": metadata["checkpoint"],
                    "image": metadata["image"],
                    "model": metadata["model"],
                    "capacity": metadata["capacity"],
                    "seed": metadata["seed"],
                    "node1": int(node1),
                    "node2": int(node2),
                    "age": int(age),
                }
            )

        return rows

    def generate_manifest_json(
        self,
        output_files: Dict[str, Path],
    ) -> Dict[str, Any]:
        manifest = {
            "export_timestamp": datetime.now().isoformat(),
            "checkpoint_count": len(self.exported_checkpoints),
            "summary": {
                "by_model": {},
                "by_image": {},
            },
            "cross_validation": self.cross_validation_summary,
            "input_files": {},
            "output_files": {},
            "checkpoints": {},
        }

        for ckpt_data in self.exported_checkpoints:
            model = ckpt_data["model"]
            image = ckpt_data["image"]
            manifest["summary"]["by_model"][model] = (
                manifest["summary"]["by_model"].get(model, 0) + 1
            )
            manifest["summary"]["by_image"][image] = (
                manifest["summary"]["by_image"].get(image, 0) + 1
            )
            manifest["checkpoints"][ckpt_data["checkpoint"]] = ckpt_data

        manifest["summary"]["by_model"] = dict(
            sorted(manifest["summary"]["by_model"].items())
        )
        manifest["summary"]["by_image"] = dict(
            sorted(manifest["summary"]["by_image"].items())
        )

        for ckpt_name, hashes in sorted(self._input_file_hashes.items()):
            manifest["input_files"][f"{ckpt_name}.pt"] = hashes

        for _, path in sorted(output_files.items(), key=lambda t: t[1].name):
            if path.exists():
                manifest["output_files"][path.name] = {
                    "size_bytes": int(path.stat().st_size),
                    "sha256": self._sha256_file(path),
                }

        return manifest

    def validate_against_runs_csv(
        self, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        key = self._checkpoint_key(
            metadata["image"],
            metadata["model"],
            int(metadata["capacity"]),
            int(metadata["seed"]),
        )

        result = {
            "checkpoint": metadata["checkpoint"],
            "image": metadata["image"],
            "model": metadata["model"],
            "capacity": int(metadata["capacity"]),
            "seed": int(metadata["seed"]),
            "checkpoint_key": key,
            "runs_csv_row_found": False,
            "validation_ok": True,
            "errors": "",
            "warnings": "",
        }

        if self.runs_df is None:
            result["warnings"] = "runs.csv não disponível"
            return result

        found = key in self._runs_key_set
        result["runs_csv_row_found"] = bool(found)
        if not found:
            result["warnings"] = (
                f"Checkpoint não encontrado em runs.csv: {key}"
            )
        return result

    def _finalize_cross_validation(self, rows: List[Dict[str, Any]]) -> None:
        checkpoint_keys = {row["checkpoint_key"] for row in rows}
        run_keys = set(self._runs_key_set)
        missing_in_runs = sorted(checkpoint_keys - run_keys)
        missing_in_checkpoints = sorted(run_keys - checkpoint_keys)

        self.cross_validation_summary = {
            "runs_csv_available": self.runs_df is not None,
            "runs_csv_total_rows": int(len(self.runs_df))
            if self.runs_df is not None
            else 0,
            "runs_csv_unique_keys": int(len(run_keys)),
            "checkpoint_total": int(len(checkpoint_keys)),
            "checkpoint_keys_found_in_runs": int(
                len(checkpoint_keys & run_keys)
            ),
            "checkpoint_keys_missing_in_runs": int(len(missing_in_runs)),
            "runs_keys_missing_in_checkpoints": int(
                len(missing_in_checkpoints)
            ),
            "missing_in_runs": missing_in_runs,
            "missing_in_checkpoints": missing_in_checkpoints,
        }

    def _stable_dataframe(
        self,
        rows: List[Dict[str, Any]],
        columns: List[str],
        sort_cols: List[str],
    ) -> pd.DataFrame:
        df = pd.DataFrame(rows)
        for col in columns:
            if col not in df.columns:
                df[col] = None
        df = df[columns]
        if len(df) > 0:
            df = df.sort_values(sort_cols, kind="stable").reset_index(
                drop=True
            )
        return df

    def export_all(
        self,
        history_stride: int = 1,
        prototype_max_rows: int = 100,
        consolidate: bool = True,
        history_mode: str = "full",
    ) -> Dict[str, Path]:
        if not self.checkpoint_dir.exists():
            msg = f"Diretório não existe: {self.checkpoint_dir}"
            if self.strict_mode:
                raise FileNotFoundError(msg)
            self.logger.warning(msg)
            return {}

        checkpoint_files = sorted(self.checkpoint_dir.glob("*.pt"))
        self.logger.info(f"Encontrados {len(checkpoint_files)} checkpoints")

        if not checkpoint_files:
            self.logger.warning("Nenhum checkpoint encontrado")
            return {}

        all_history = []
        all_prototypes = []
        all_edges = []
        all_validations = []
        all_structures = []
        self.exported_checkpoints = []
        self._input_file_hashes = {}

        for ckpt_path in checkpoint_files:
            basename = ckpt_path.stem
            parsed = self._parse_filename(ckpt_path.name)
            if not parsed:
                continue

            self._input_file_hashes[basename] = {
                "size_bytes": int(ckpt_path.stat().st_size),
                "sha256": self._sha256_file(ckpt_path),
            }

            ckpt = self.load_checkpoint(ckpt_path)
            if ckpt is None:
                continue

            metadata = self._extract_metadata(ckpt, parsed, basename)
            self.exported_checkpoints.append(metadata)

            all_structures.append(self.generate_structure_txt(ckpt, basename))
            all_history.extend(
                self.generate_history_csv(
                    ckpt,
                    metadata,
                    stride=history_stride,
                    history_mode=history_mode,
                )
            )
            all_prototypes.extend(
                self.generate_prototypes_csv(
                    ckpt, metadata, max_rows=prototype_max_rows
                )
            )
            all_edges.extend(self.generate_edges_csv(ckpt, metadata))
            all_validations.append(self.validate_against_runs_csv(metadata))

        self._finalize_cross_validation(all_validations)

        output_files = {}
        if not consolidate:
            return output_files

        if all_structures:
            txt_path = self.output_dir / "checkpoints_atuais_consolidado.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(all_structures))
            output_files["structure_txt"] = txt_path

        if self.exported_checkpoints:
            csv_path = self.output_dir / "checkpoints_atuais_resumo.csv"
            self.generate_summary_csv().to_csv(csv_path, index=False)
            output_files["summary_csv"] = csv_path

        if history_mode != "none":
            csv_path = self.output_dir / "checkpoints_atuais_historicos.csv"
            self._stable_dataframe(
                all_history,
                self.HISTORY_COLUMNS,
                ["image", "model", "capacity", "seed", "history_index"],
            ).to_csv(csv_path, index=False)
            output_files["history_csv"] = csv_path

        csv_path = self.output_dir / "checkpoints_atuais_prototipos.csv"
        self._stable_dataframe(
            all_prototypes,
            self.PROTOTYPE_COLUMNS,
            ["image", "model", "capacity", "seed", "unit_type", "unit_id"],
        ).to_csv(csv_path, index=False)
        output_files["prototypes_csv"] = csv_path

        csv_path = self.output_dir / "checkpoints_atuais_arestas.csv"
        self._stable_dataframe(
            all_edges,
            self.EDGE_COLUMNS,
            ["image", "model", "capacity", "seed", "node1", "node2"],
        ).to_csv(csv_path, index=False)
        output_files["edges_csv"] = csv_path

        csv_path = self.output_dir / "checkpoints_atuais_consistencia.csv"
        self._stable_dataframe(
            all_validations,
            self.CONSISTENCY_COLUMNS,
            ["image", "model", "capacity", "seed"],
        ).to_csv(csv_path, index=False)
        output_files["validation_csv"] = csv_path

        json_path = self.output_dir / "checkpoints_atuais_manifesto.json"
        manifest = self.generate_manifest_json(output_files)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        output_files["manifest_json"] = json_path

        return output_files


def main() -> None:
    """Ponto de entrada para testes rápidos."""
    from pathlib import Path

    # Paths padrão (assumindo execução do root)
    project_root = Path.cwd()
    checkpoint_dir = project_root / "outputs" / "checkpoints"
    output_dir = project_root / "validation"
    runs_csv = project_root / "outputs" / "metrics" / "runs.csv"

    exporter = CheckpointExporter(
        checkpoint_dir=checkpoint_dir,
        output_dir=output_dir,
        runs_csv_path=runs_csv,
        trusted_checkpoints=False,
        strict_mode=False,
    )

    output_files = exporter.export_all(
        history_stride=1,
        prototype_max_rows=100,
        consolidate=True,
    )

    print("\n=== Arquivos Gerados ===")
    for key, path in output_files.items():
        print(f"  {key}: {path}")

    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    main()
