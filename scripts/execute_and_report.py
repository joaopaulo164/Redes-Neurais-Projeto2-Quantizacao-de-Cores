#!/usr/bin/env python
"""
Script completo para executar experimentos, fazer backup e gerar relatório estruturado.

Fluxo:
1. Fazer backup da pasta outputs com timestamp
2. Limpar pastas outputs e validation
3. Executar experimentos (run_all.py)
4. Gerar validação e evidências
5. Gerar relatório final estruturado
"""

import argparse
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable


class ProjectExecution:
    """Orquestra a execução completa do projeto com backup e relatório."""

    def __init__(self, project_root: str | Path | None = None) -> None:
        self.root = Path(project_root or Path(__file__).resolve().parents[1])
        self.outputs_dir = self.root / "outputs"
        self.validation_dir = self.root / "validation"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def print_header(self, text: str) -> None:
        """Imprime um cabeçalho formatado."""
        print(f"\n{'=' * 70}")
        print(f"🔷 {text}")
        print(f"{'=' * 70}\n")

    def print_step(
        self,
        step_num: int | float,
        text: str,
        total: int | None = None,
    ) -> None:
        """Imprime um passo numerado."""
        if total:
            print(f"[{step_num}/{total}] {text}")
        else:
            print(f"[{step_num}] {text}")

    def backup_outputs(self) -> bool:
        """Faz backup das pastas outputs e validation com timestamp."""
        self.print_step(1, "Fazendo backup dos outputs e validation", 7)

        ok = True

        if self.outputs_dir.exists():
            backup_dir = self.root / f"outputs_execucao_{self.timestamp}"
            try:
                print(f"  📦 Copiando {self.outputs_dir} → {backup_dir.name}/")
                shutil.copytree(
                    self.outputs_dir, backup_dir, dirs_exist_ok=True
                )
                num_files = sum(
                    1 for _ in backup_dir.rglob("*") if _.is_file()
                )
                print(
                    f"  ✅ Backup de outputs criado com {num_files} arquivos"
                )
            except Exception as error:
                print(f"  ❌ Erro ao fazer backup de outputs: {error}")
                ok = False
        else:
            print("  ℹ️  Pasta outputs não existe ainda (primeira execução)")

        if self.validation_dir.exists():
            validation_backup_dir = (
                self.root / f"validation_execucao_{self.timestamp}"
            )
            try:
                print(
                    f"  📦 Copiando {self.validation_dir} → {validation_backup_dir.name}/"
                )
                shutil.copytree(
                    self.validation_dir,
                    validation_backup_dir,
                    dirs_exist_ok=True,
                )
                num_files = sum(
                    1 for _ in validation_backup_dir.rglob("*") if _.is_file()
                )
                print(
                    f"  ✅ Backup de validation criado com {num_files} arquivos"
                )
            except Exception as error:
                print(f"  ❌ Erro ao fazer backup de validation: {error}")
                ok = False
        else:
            print("  ℹ️  Pasta validation não existe ainda (primeira execução)")

        return ok

    def clean_outputs(self) -> bool:
        """Limpa as pastas de saída mantendo a estrutura e .gitkeep."""
        self.print_step(2, "Limpando pastas de saída", 7)

        dirs_to_clean = [
            self.outputs_dir / "checkpoints",
            self.outputs_dir / "reconstructed",
            self.outputs_dir / "figures",
            self.outputs_dir / "metrics",
            self.outputs_dir / "tables",
            self.outputs_dir / "logs",
            self.validation_dir,
            self.validation_dir / "checkpoints",
        ]

        for directory in dirs_to_clean:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                continue

            for item in directory.iterdir():
                if item.name == ".gitkeep":
                    continue
                if item.is_dir():
                    try:
                        shutil.rmtree(item)
                        print(
                            f"  🗑️  Removido diretório: {item.relative_to(self.root)}"
                        )
                    except Exception as error:
                        print(
                            f"  ⚠️  Erro ao remover diretório {item}: {error}"
                        )
                elif item.is_file():
                    try:
                        item.unlink()
                        print(
                            f"  🗑️  Removido arquivo: {item.relative_to(self.root)}"
                        )
                    except Exception as error:
                        print(f"  ⚠️  Erro ao remover arquivo {item}: {error}")

        print("  ✅ Limpeza concluída!")
        return True

    def run_experiments(
        self,
        config: str = "config/experiments.yaml",
        quick: bool = False,
    ) -> bool:
        """Executa os experimentos."""
        step = 3 if not quick else 2.5
        self.print_step(step, "Executando experimentos", 7)

        if quick:
            config = "config/experiments - teste rapido.yaml"
            print("  ⚡ Modo rápido ativo (matriz reduzida)")

        print(f"  📋 Configuração: {config}")
        print(
            f"  ⏱️  Tempo estimado: {'10-15 min' if quick else '45-60 min'}\n"
        )

        try:
            result = subprocess.run(
                [sys.executable, "scripts/run_all.py", "--config", config],
                cwd=self.root,
                check=False,
            )

            if result.returncode == 0:
                print("\n  ✅ Experimentos concluídos com sucesso!")
                return True
            else:
                print(
                    f"\n  ⚠️  Experimentos terminaram com código: {result.returncode}"
                )
                return True  # Continua mesmo com avisos
        except Exception as error:
            print(f"  ❌ Erro ao executar experimentos: {error}")
            return False

    def generate_evidences(self) -> bool:
        """Gera as evidências (validação, figuras, etc)."""
        self.print_step(4, "Gerando validações e evidências", 7)

        scripts = [
            ("scripts/validate_unique_colors.py", "Validando cores únicas"),
        ]

        for script, description in scripts:
            script_path = self.root / script
            if script_path.exists():
                print(f"  🔍 {description}...")
                try:
                    result = subprocess.run(
                        [sys.executable, str(script_path)],
                        cwd=self.root,
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        print(f"  ✅ {description} concluído")
                    else:
                        print(f"  ⚠️  {description} com avisos")
                except Exception as error:
                    print(f"  ⚠️  Erro em {description}: {error}")

        return True

    def export_checkpoints(self) -> bool:
        """Exporta os checkpoints em formatos auditáveis."""
        self.print_step(
            5, "Exportando checkpoints para formatos auditáveis", 7
        )

        script_path = self.root / "scripts/export_current_checkpoints.py"
        if not script_path.exists():
            print("  ⚠️  Script export_current_checkpoints.py não encontrado")
            return True  # Não interrompe pipeline

        print("  📦 Exportando checkpoints em CSV/TXT/JSON...")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--input-dir",
                    "outputs/checkpoints",
                    "--output-dir",
                    "validation",
                    "--format",
                    "all",
                    "--history-mode",
                    "summary",
                    "--overwrite",
                ],
                cwd=self.root,
                check=False,
            )

            if result.returncode == 0:
                print("  ✅ Checkpoints exportados com sucesso!")
                return True
            else:
                print("  ⚠️  Exportação de checkpoints com avisos")
                return True
        except Exception as error:
            print(f"  ⚠️  Erro ao exportar checkpoints: {error}")
            return True  # Não interrompe pipeline

    def generate_report(self) -> bool:
        """Gera o relatório estruturado."""
        self.print_step(6, "Gerando relatório estruturado", 7)

        script_path = self.root / "scripts/generate_report.py"
        if not script_path.exists():
            print("  ⚠️  Script generate_report.py não encontrado")
            return False

        print("  📝 Gerando relatório Markdown...")
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.root,
                check=False,
            )

            if result.returncode == 0:
                print("  ✅ Relatório gerado com sucesso!")
                report_path = self.root / "report" / "relatorio_final.md"
                if report_path.exists():
                    print(
                        f"  📄 Relatório em: {report_path.relative_to(self.root)}"
                    )
                return True
            else:
                print("  ⚠️  Relatório gerado com avisos")
                return True
        except Exception as error:
            print(f"  ❌ Erro ao gerar relatório: {error}")
            return False

    def create_summary(self) -> bool:
        """Cria um resumo da execução."""
        self.print_step(7, "Criando resumo da execução", 7)

        summary_file = self.root / "EXECUCAO_RESUMO.txt"

        # Contar arquivos gerados
        num_images = len(
            list((self.outputs_dir / "reconstructed").glob("*.png"))
        )
        num_figures = len(list((self.outputs_dir / "figures").glob("*")))
        num_checkpoints = len(
            list((self.outputs_dir / "checkpoints").glob("*.pt"))
        )

        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║           RESUMO DA EXECUÇÃO - {self.timestamp}            ║
╚════════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS GERADAS:
  • Imagens reconstruídas: {num_images}
  • Figuras de análise: {num_figures}
  • Checkpoints salvos: {num_checkpoints}
  • Backup de outputs: outputs_execucao_{self.timestamp}/
  • Backup de validation: validation_execucao_{self.timestamp}/

📂 ARQUIVOS PRINCIPAIS:
  • Métricas: outputs/metrics/runs.csv
  • Resumo: outputs/tables/summary.csv
  • Validação: validation/validation_unique_colors.csv
  • Relatório: report/relatorio_final.md

🔗 LINKS ÚTEIS:
  • Abrir relatório: report/relatorio_final.md
  • Ver imagens: outputs/reconstructed/
  • Ver figuras: outputs/figures/
  • Ver métricas: outputs/tables/summary.csv

⏱️  TIMESTAMP: {self.timestamp}
🖥️  Projeto raiz: {self.root}

Para comparar com execução anterior:
  • Backup outputs: {self.root}/outputs_execucao_{self.timestamp}
  • Backup validation: {self.root}/validation_execucao_{self.timestamp}
  • Compare com: outputs/ e validation/

Para reexecutar:
  python scripts/execute_and_report.py --full
  ou
  python scripts/automate.py pipeline
"""

        try:
            if summary_file.exists():
                with open(summary_file, "a", encoding="utf-8") as f:
                    f.write("\n\n" + "─" * 64 + "\n\n")
                    f.write(summary)
            else:
                with open(summary_file, "w", encoding="utf-8") as f:
                    f.write(summary)
            print(f"  📋 Resumo salvo em: {summary_file.name}")
            print(summary)
            return True
        except Exception as error:
            print(f"  ❌ Erro ao criar resumo: {error}")
            return False

    def run_full_pipeline(
        self,
        config: str = "config/experiments.yaml",
        quick: bool = False,
    ) -> None:
        """Executa o pipeline completo."""
        self.print_header("🚀 PIPELINE COMPLETO DE EXECUÇÃO E RELATÓRIO")

        start_time = time.time()
        print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        steps: list[tuple[str, Callable[[], bool]]] = [
            ("Backup", self.backup_outputs),
            ("Limpeza", self.clean_outputs),
            ("Experimentos", lambda: self.run_experiments(config, quick)),
            ("Evidências", self.generate_evidences),
            ("Checkpoints", self.export_checkpoints),
            ("Relatório", self.generate_report),
            ("Resumo", self.create_summary),
        ]

        results = []
        for step_name, step_function in steps:
            try:
                success = step_function()
                results.append((step_name, success))
                if not success and step_name in ["Backup", "Limpeza"]:
                    print(f"\n⚠️  Pipeline interrompido em: {step_name}\n")
                    break
                if not success and step_name in ["Experimentos", "Relatório"]:
                    print(
                        f"\n⚠️  Pipeline continuando apesar de erro em: {step_name}\n"
                    )
            except Exception as error:
                print(f"\n❌ Erro fatal em {step_name}: {error}\n")
                results.append((step_name, False))
                break

        elapsed = time.time() - start_time
        self.print_header("📊 RESUMO DO PIPELINE")

        for step_name, success in results:
            status = "✅" if success else "❌"
            print(f"{status} {step_name}")

        print(f"\n⏱️  Tempo total: {elapsed:.1f}s ({elapsed / 60:.1f} min)")
        print(
            f"Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        # Sugestões finais
        report_path = self.root / "report" / "relatorio_final.md"
        if report_path.exists():
            print(f"📖 Leia o relatório: {report_path.relative_to(self.root)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Executa pipeline completo com backup, experimentos e relatório",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/execute_and_report.py          # Backup + Limpeza + Full + Relatório
  python scripts/execute_and_report.py --full   # Matriz completa
  python scripts/execute_and_report.py --quick  # Matriz reduzida (teste rápido)
  python scripts/execute_and_report.py --backup # Apenas fazer backup
  python scripts/execute_and_report.py --clean  # Apenas limpar
        """,
    )

    parser.add_argument(
        "--full", action="store_true", help="Executar matriz completa (padrão)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Executar matriz reduzida (teste rápido)",
    )
    parser.add_argument(
        "--backup-only", action="store_true", help="Apenas fazer backup"
    )
    parser.add_argument(
        "--clean-only", action="store_true", help="Apenas limpar outputs"
    )
    parser.add_argument(
        "--config",
        default="config/experiments.yaml",
        help="Arquivo de configuração (padrão: config/experiments.yaml)",
    )

    args = parser.parse_args()

    execution = ProjectExecution()

    if args.backup_only:
        execution.backup_outputs()
    elif args.clean_only:
        execution.clean_outputs()
    else:
        # Pipeline completo
        execution.run_full_pipeline(config=args.config, quick=args.quick)


if __name__ == "__main__":
    main()
