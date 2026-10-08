"""
test_checkpoint_exporter.py

Testes para o módulo checkpoint_exporter.py.

Utiliza pytest com tmp_path para criar checkpoints sintéticos sem modificar
os dados reais de outputs/checkpoints/.
"""

import json
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
import torch

from src.validation.checkpoint_exporter import CheckpointExporter


@pytest.fixture
def tmp_checkpoints(tmp_path: Path) -> Path:
    """Cria diretório com checkpoints sintéticos."""
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()

    # SOM checkpoint
    som_ckpt = {
        "model": "som",
        "rows": 4,
        "cols": 4,
        "weights": torch.randn(16, 3),
        "history": [
            {"epoch": 0, "qe": 1.5, "lr": 0.1, "sigma": 2.0},
            {"epoch": 1, "qe": 1.2, "lr": 0.09, "sigma": 1.9},
            {"epoch": 2, "qe": 1.0, "lr": 0.08, "sigma": 1.8},
        ],
    }
    torch.save(som_ckpt, checkpoint_dir / "test_img_som_16_s13.pt")

    # GNG checkpoint
    gng_ckpt = {
        "model": "gng",
        "weights": torch.randn(20, 3),
        "errors": torch.randn(20),
        "edges": {(0, 1): 0, (1, 2): 1, (2, 3): 2},
        "history": [
            {"step": 0, "nodes": 2, "edges": 1},
            {"step": 1, "nodes": 3, "edges": 2},
            {"step": 2, "nodes": 4, "edges": 3},
        ],
    }
    torch.save(gng_ckpt, checkpoint_dir / "test_img_gng_64_s37.pt")

    # k-means checkpoint
    kmeans_ckpt = {
        "model": "kmeans",
        "centroids": torch.randn(16, 3),
        "history": [
            {"iteration": 0, "shift": 0.5},
            {"iteration": 1, "shift": 0.3},
            {"iteration": 2, "shift": 0.1},
        ],
    }
    torch.save(kmeans_ckpt, checkpoint_dir / "test_img_kmeans_16_s101.pt")

    return checkpoint_dir


@pytest.fixture
def tmp_runs_csv(tmp_path: Path) -> Path:
    """Cria runs.csv sintético."""
    csv_path = tmp_path / "runs.csv"
    df = pd.DataFrame(
        [
            {
                "image": "test_img",
                "model": "som",
                "capacity": 16,
                "seed": 13,
                "quantization_error": 1.0,
            },
            {
                "image": "test_img",
                "model": "gng",
                "capacity": 64,
                "seed": 37,
                "quantization_error": 0.9,
            },
            {
                "image": "test_img",
                "model": "kmeans",
                "capacity": 16,
                "seed": 101,
                "quantization_error": 1.2,
            },
        ]
    )
    df.to_csv(csv_path, index=False)
    return csv_path


class TestCheckpointExporterInit:
    """Testes de inicialização."""

    def test_init_basic(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Inicialização básica."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path / "output",
        )
        assert exporter.checkpoint_dir == tmp_checkpoints
        assert exporter.output_dir == (tmp_path / "output")
        assert exporter.output_dir.exists()

    def test_init_with_runs_csv(
        self,
        tmp_checkpoints: Path,
        tmp_runs_csv: Path,
        tmp_path: Path,
    ) -> None:
        """Inicialização com runs.csv."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path / "output",
            runs_csv_path=tmp_runs_csv,
        )
        assert exporter.runs_df is not None
        assert len(exporter.runs_df) == 3

    def test_init_missing_checkpoint_dir(self, tmp_path: Path) -> None:
        """Diretório de checkpoints não existe."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_path / "nonexistent",
            output_dir=tmp_path / "output",
            strict_mode=False,
        )
        # Não deve falhar em strict_mode=False
        assert exporter is not None

    def test_init_missing_checkpoint_dir_strict(self, tmp_path: Path) -> None:
        """Diretório de checkpoints não existe com strict_mode=True."""
        with pytest.raises(FileNotFoundError):
            CheckpointExporter(
                checkpoint_dir=tmp_path / "nonexistent",
                output_dir=tmp_path / "output",
                strict_mode=True,
            )


class TestCheckpointExporterParsing:
    """Testes de parsing de nome de arquivo."""

    def test_parse_valid_som(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Parse de nome SOM válido."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        result = exporter._parse_filename("test_img_som_16_s13.pt")
        assert result is not None
        assert result["image"] == "test_img"
        assert result["model"] == "som"
        assert result["capacity"] == "16"
        assert result["seed"] == "13"

    def test_parse_valid_gng(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Parse de nome GNG válido."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        result = exporter._parse_filename("test_img_gng_64_s37.pt")
        assert result is not None
        assert result["model"] == "gng"

    def test_parse_image_with_underscores(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Parse de imagem com múltiplos underscores."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        result = exporter._parse_filename("my_test_img_som_16_s13.pt")
        assert result is not None
        assert result["image"] == "my_test_img"

    def test_parse_invalid(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Parse de nome inválido."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        result = exporter._parse_filename("invalid_name.pt")
        assert result is None


class TestCheckpointExporterLoad:
    """Testes de carregamento de checkpoint."""

    def test_load_som_checkpoint(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Carrega checkpoint SOM."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
            trusted_checkpoints=False,
        )
        ckpt = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_som_16_s13.pt"
        )
        assert ckpt is not None
        assert ckpt["model"] == "som"
        assert ckpt["rows"] == 4
        assert ckpt["cols"] == 4

    def test_load_gng_checkpoint(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Carrega checkpoint GNG."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        ckpt = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_gng_64_s37.pt"
        )
        assert ckpt is not None
        assert ckpt["model"] == "gng"
        assert isinstance(ckpt["edges"], dict)

    def test_load_nonexistent_checkpoint(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Tenta carregar checkpoint que não existe."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        ckpt = exporter.load_checkpoint(tmp_checkpoints / "nonexistent.pt")
        assert ckpt is None

    def test_load_uses_cpu_map_location_even_when_trusted(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Garante map_location='cpu' sempre e weights_only=False só em trusted."""
        captured = {}

        def fake_load(path: Path, **kwargs: Any) -> dict[str, str]:
            captured["kwargs"] = kwargs
            return {"model": "som"}

        monkeypatch.setattr(torch, "load", fake_load)

        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
            trusted_checkpoints=True,
        )
        _ = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_som_16_s13.pt"
        )

        assert captured["kwargs"]["map_location"] == "cpu"
        assert captured["kwargs"]["weights_only"] is False


class TestCheckpointExporterMetadata:
    """Testes de extração de metadados."""

    def test_extract_som_metadata(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Extrai metadados SOM."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        ckpt = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_som_16_s13.pt"
        )
        parsed = exporter._parse_filename("test_img_som_16_s13.pt")
        metadata = exporter._extract_metadata(
            ckpt, parsed, "test_img_som_16_s13"
        )

        assert metadata["image"] == "test_img"
        assert metadata["model"] == "som"
        assert metadata["capacity"] == 16
        assert metadata["seed"] == 13
        assert metadata["checkpoint_model_type"] == "som"
        assert metadata["som_rows"] == 4
        assert metadata["som_cols"] == 4
        assert metadata["som_num_neurons"] == 16
        assert metadata["history_length"] == 3

    def test_extract_gng_metadata(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Extrai metadados GNG."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        ckpt = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_gng_64_s37.pt"
        )
        parsed = exporter._parse_filename("test_img_gng_64_s37.pt")
        metadata = exporter._extract_metadata(
            ckpt, parsed, "test_img_gng_64_s37"
        )

        assert metadata["checkpoint_model_type"] == "gng"
        assert metadata["gng_num_nodes"] == 20
        assert metadata["gng_num_edges"] == 3

    def test_extract_kmeans_metadata(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Extrai metadados k-means."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        ckpt = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_kmeans_16_s101.pt"
        )
        parsed = exporter._parse_filename("test_img_kmeans_16_s101.pt")
        metadata = exporter._extract_metadata(
            ckpt, parsed, "test_img_kmeans_16_s101"
        )

        assert metadata["checkpoint_model_type"] == "kmeans"
        assert metadata["num_centroids"] == 16


class TestCheckpointExporterGeneration:
    """Testes de geração de formatos de saída."""

    def test_generate_structure_txt(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Gera TXT estrutural."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        ckpt = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_som_16_s13.pt"
        )
        txt = exporter.generate_structure_txt(ckpt, "test_img_som_16_s13")

        assert "SOM" in txt
        assert "Grid: 4 rows x 4 cols" in txt
        assert "Neurons: 16" in txt
        assert "History: 3 records" in txt

    def test_generate_history_csv(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Gera CSV de histórico."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        ckpt = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_som_16_s13.pt"
        )
        parsed = exporter._parse_filename("test_img_som_16_s13.pt")
        metadata = exporter._extract_metadata(
            ckpt, parsed, "test_img_som_16_s13"
        )
        rows = exporter.generate_history_csv(ckpt, metadata)

        assert len(rows) == 3
        assert rows[0]["epoch"] == 0
        assert rows[0]["qe"] == 1.5

    def test_generate_prototypes_csv_som(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Gera CSV de protótipos SOM."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        ckpt = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_som_16_s13.pt"
        )
        parsed = exporter._parse_filename("test_img_som_16_s13.pt")
        metadata = exporter._extract_metadata(
            ckpt, parsed, "test_img_som_16_s13"
        )
        rows = exporter.generate_prototypes_csv(ckpt, metadata)

        assert len(rows) == 16
        assert rows[0]["unit_type"] == "neuron"
        assert "unit_id" in rows[0]
        assert "r" in rows[0]
        assert "g" in rows[0]
        assert "b" in rows[0]

    def test_generate_prototypes_csv_kmeans(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Gera CSV de protótipos k-means."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        ckpt = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_kmeans_16_s101.pt"
        )
        parsed = exporter._parse_filename("test_img_kmeans_16_s101.pt")
        metadata = exporter._extract_metadata(
            ckpt, parsed, "test_img_kmeans_16_s101"
        )
        rows = exporter.generate_prototypes_csv(ckpt, metadata)

        assert len(rows) == 16
        assert rows[0]["unit_type"] == "centroid"
        assert "unit_id" in rows[0]

    def test_generate_edges_csv(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Gera CSV de arestas."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        ckpt = exporter.load_checkpoint(
            tmp_checkpoints / "test_img_gng_64_s37.pt"
        )
        parsed = exporter._parse_filename("test_img_gng_64_s37.pt")
        metadata = exporter._extract_metadata(
            ckpt, parsed, "test_img_gng_64_s37"
        )
        rows = exporter.generate_edges_csv(ckpt, metadata)

        assert len(rows) == 3
        assert rows[0]["node1"] == 0
        assert rows[0]["node2"] == 1

    def test_generate_manifest_json(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Gera manifesto JSON."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        # Exportar para popular self.exported_checkpoints
        _ = exporter.export_all(consolidate=False)

        manifest = exporter.generate_manifest_json({})

        assert "export_timestamp" in manifest
        assert "checkpoint_count" in manifest
        assert "summary" in manifest
        assert "checkpoints" in manifest
        assert manifest["checkpoint_count"] == 3


class TestCheckpointExporterExportAll:
    """Testes da exportação completa."""

    def test_export_all_creates_files(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Export all cria arquivos."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        output_files = exporter.export_all(consolidate=True)

        assert len(output_files) > 0
        assert "summary_csv" in output_files
        assert "history_csv" in output_files
        assert "prototypes_csv" in output_files

    def test_export_all_summary_csv_valid(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """CSV resumido é válido."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        output_files = exporter.export_all(consolidate=True)

        summary_csv = output_files["summary_csv"]
        df = pd.read_csv(summary_csv)

        assert len(df) == 3
        assert "image" in df.columns
        assert "model" in df.columns
        assert "capacity" in df.columns
        assert "seed" in df.columns
        assert list(df.columns) == exporter.SUMMARY_COLUMNS

    def test_export_all_prototypes_csv_valid(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """CSV protótipos é válido."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        output_files = exporter.export_all(consolidate=True)

        prototypes_csv = output_files["prototypes_csv"]
        df = pd.read_csv(prototypes_csv)

        # 16 (SOM) + 20 (GNG) + 16 (k-means) = 52
        assert len(df) == 52
        assert list(df.columns) == exporter.PROTOTYPE_COLUMNS

    def test_export_all_with_stride(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Export all com history_stride."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        output_files = exporter.export_all(history_stride=2, consolidate=True)

        history_csv = output_files["history_csv"]
        df = pd.read_csv(history_csv)

        # Com stride=2, esperamos menos linhas
        # SOM tem 3 históricos, com stride=2 → 2 linhas (0, 2)
        # GNG tem 3 históricos, com stride=2 → 2 linhas
        # k-means tem 3 históricos, com stride=2 → 2 linhas
        # Total esperado: ~6
        assert len(df) <= 6

    def test_export_all_with_summary_history_mode(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Exporta apenas os pontos inicial e final do histórico."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        output_files = exporter.export_all(
            history_mode="summary", consolidate=True
        )
        history_csv = output_files["history_csv"]
        df = pd.read_csv(history_csv)
        # primeiro/último por checkpoint -> 2 * 3 = 6
        assert len(df) == 6
        assert set(df["history_mode"].unique()) == {"summary"}

    def test_export_all_manifest_json_valid(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """JSON manifesto é válido."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
        )
        output_files = exporter.export_all(consolidate=True)

        manifest_json = output_files["manifest_json"]
        with open(manifest_json) as f:
            manifest = json.load(f)

        assert manifest["checkpoint_count"] == 3
        assert "som" in manifest["summary"]["by_model"]
        assert "gng" in manifest["summary"]["by_model"]
        assert "kmeans" in manifest["summary"]["by_model"]
        assert "input_files" in manifest
        assert "output_files" in manifest


class TestCheckpointExporterValidation:
    """Testes de validação contra runs.csv."""

    def test_validate_against_runs_csv_found(
        self,
        tmp_checkpoints: Path,
        tmp_runs_csv: Path,
        tmp_path: Path,
    ) -> None:
        """Validação encontra checkpoint em runs.csv."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
            runs_csv_path=tmp_runs_csv,
        )
        ckpt_data = {
            "image": "test_img",
            "model": "som",
            "capacity": 16,
            "seed": 13,
        }
        result = exporter.validate_against_runs_csv(
            {
                "checkpoint": "test_img_som_16_s13",
                **ckpt_data,
            }
        )

        assert result["runs_csv_row_found"] is True
        assert result["validation_ok"] is True

    def test_validate_against_runs_csv_not_found(
        self,
        tmp_checkpoints: Path,
        tmp_runs_csv: Path,
        tmp_path: Path,
    ) -> None:
        """Validação não encontra checkpoint em runs.csv."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
            runs_csv_path=tmp_runs_csv,
        )
        ckpt_data = {
            "image": "other_img",
            "model": "som",
            "capacity": 16,
            "seed": 13,
        }
        result = exporter.validate_against_runs_csv(
            {
                "checkpoint": "other_img_som_16_s13",
                **ckpt_data,
            }
        )

        assert result["runs_csv_row_found"] is False
        assert result["warnings"]

    def test_validate_no_runs_csv(
        self,
        tmp_checkpoints: Path,
        tmp_path: Path,
    ) -> None:
        """Validação sem runs.csv."""
        exporter = CheckpointExporter(
            checkpoint_dir=tmp_checkpoints,
            output_dir=tmp_path,
            runs_csv_path=None,
        )
        ckpt_data = {
            "image": "test_img",
            "model": "som",
            "capacity": 16,
            "seed": 13,
        }
        result = exporter.validate_against_runs_csv(
            {
                "checkpoint": "test_img_som_16_s13",
                **ckpt_data,
            }
        )

        assert result["validation_ok"] is True
        assert result["warnings"]

    def test_history_absent_vs_empty(self, tmp_path: Path) -> None:
        checkpoint_dir = tmp_path / "checkpoints"
        checkpoint_dir.mkdir()
        torch.save(
            {
                "model": "som",
                "rows": 1,
                "cols": 1,
                "weights": torch.randn(1, 3),
            },
            checkpoint_dir / "img_a_som_16_s1.pt",
        )
        torch.save(
            {
                "model": "som",
                "rows": 1,
                "cols": 1,
                "weights": torch.randn(1, 3),
                "history": [],
            },
            checkpoint_dir / "img_b_som_16_s1.pt",
        )

        exporter = CheckpointExporter(
            checkpoint_dir=checkpoint_dir, output_dir=tmp_path
        )
        output_files = exporter.export_all(consolidate=True)
        df = pd.read_csv(output_files["summary_csv"])

        row_absent = df[df["image"] == "img_a"].iloc[0]
        row_empty = df[df["image"] == "img_b"].iloc[0]
        assert row_absent["history_state"] == "absent"
        assert pd.isna(row_absent["history_length"])
        assert row_empty["history_state"] == "empty"
        assert row_empty["history_length"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
