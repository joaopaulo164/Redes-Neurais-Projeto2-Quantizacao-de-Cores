from pathlib import Path

import pytest

from scripts.execute_and_report import ProjectExecution


def test_pipeline_stops_when_backup_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    execution = ProjectExecution(tmp_path)
    executed_steps: list[str] = []

    def backup_outputs() -> bool:
        executed_steps.append("backup")
        return False

    def clean_outputs() -> bool:
        executed_steps.append("clean")
        return True

    monkeypatch.setattr(execution, "backup_outputs", backup_outputs)
    monkeypatch.setattr(execution, "clean_outputs", clean_outputs)
    monkeypatch.setattr(
        execution,
        "run_experiments",
        lambda *args, **kwargs: executed_steps.append("experiments") or True,
    )
    monkeypatch.setattr(
        execution,
        "generate_evidences",
        lambda: executed_steps.append("evidences") or True,
    )
    monkeypatch.setattr(
        execution,
        "export_checkpoints",
        lambda: executed_steps.append("checkpoints") or True,
    )
    monkeypatch.setattr(
        execution,
        "generate_report",
        lambda: executed_steps.append("report") or True,
    )
    monkeypatch.setattr(
        execution,
        "create_summary",
        lambda: executed_steps.append("summary") or True,
    )

    execution.run_full_pipeline()

    assert executed_steps == ["backup"]
