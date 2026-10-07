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
from datetime import datetime
from pathlib import Path
import time


class ProjectExecution:
    """Orquestra a execução completa do projeto com backup e relatório."""

    def __init__(self, project_root=None):
        self.root = Path(project_root or Path(__file__).resolve().parents[1])
        self.outputs_dir = self.root / "outputs"
        self.validation_dir = self.root / "validation"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def print_header(self, text):
        """Imprime um cabeçalho formatado."""
        print(f"\n{'=' * 70}")
        print(f"🔷 {text}")
        print(f"{'=' * 70}\n")

    def print_step(self, step_num, text, total=None):
        """Imprime um passo numerado."""
        if total:
            print(f"[{step_num}/{total}] {text}")
        else:
            print(f"[{step_num}] {text}")

    def backup_outputs(self):
        """Faz backup da pasta outputs com timestamp."""
        self.print_step(1, "Fazendo backup dos outputs", 6)

        if not self.outputs_dir.exists():
            print("  ℹ️  Pasta outputs não existe ainda (primeira execução)")
            return True

        backup_dir = self.root / f"outputs_execucao_{self.timestamp}"

        try:
            print(f"  📦 Copiando {self.outputs_dir} → {backup_dir.name}/")
            shutil.copytree(self.outputs_dir, backup_dir, dirs_exist_ok=True)
            
            # Contar arquivos
            num_files = sum(1 for _ in backup_dir.rglob("*") if _.is_file())
            print(f"  ✅ Backup criado com {num_files} arquivos")
            return True
        except Exception as e:
            print(f"  ❌ Erro ao fazer backup: {e}")
            return False

    def clean_outputs(self):
        """Limpa as pastas de saída mantendo .gitkeep."""
        self.print_step(2, "Limpando pastas de saída", 6)

        dirs_to_clean = [
            self.outputs_dir / "checkpoints",
            self.outputs_dir / "reconstructed",
            self.outputs_dir / "figures",
            self.outputs_dir / "metrics",
            self.outputs_dir / "tables",
            self.outputs_dir / "logs",
            self.validation_dir / "checkpoints",
        ]

        for directory in dirs_to_clean:
            if directory.exists():
                for file in directory.glob("*"):
                    if file.is_file() and file.name != ".gitkeep":
                        try:
                            file.unlink()
                            print(f"  🗑️  Removido: {directory.name}/{file.name}")
                        except Exception as e:
                            print(f"  ⚠️  Erro ao remover {file.name}: {e}")
            else:
                directory.mkdir(parents=True, exist_ok=True)

        print("  ✅ Limpeza concluída!")
        return True

    def run_experiments(self, config="config/experiments.yaml", quick=False):
        """Executa os experimentos."""
        step = 3 if not quick else 2.5
        self.print_step(step, "Executando experimentos", 6)

        if quick:
            config = "config/experiments - teste rapido.yaml"
            print(f"  ⚡ Modo rápido ativo (matriz reduzida)")
        
        print(f"  📋 Configuração: {config}")
        print(f"  ⏱️  Tempo estimado: {'10-15 min' if quick else '45-60 min'}\n")

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
                print(f"\n  ⚠️  Experimentos terminaram com código: {result.returncode}")
                return True  # Continua mesmo com avisos
        except Exception as e:
            print(f"  ❌ Erro ao executar experimentos: {e}")
            return False

    def generate_evidences(self):
        """Gera as evidências (validação, figuras, etc)."""
        self.print_step(4, "Gerando validações e evidências", 6)

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
                except Exception as e:
                    print(f"  ⚠️  Erro em {description}: {e}")

        return True

    def generate_report(self):
        """Gera o relatório estruturado."""
        self.print_step(5, "Gerando relatório estruturado", 6)

        script_path = self.root / "scripts/generate_report.py"
        if not script_path.exists():
            print(f"  ⚠️  Script generate_report.py não encontrado")
            return False

        print(f"  📝 Gerando relatório Markdown...")
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.root,
                check=False,
            )
            
            if result.returncode == 0:
                print(f"  ✅ Relatório gerado com sucesso!")
                report_path = self.root / "report" / "relatorio_final.md"
                if report_path.exists():
                    print(f"  📄 Relatório em: {report_path.relative_to(self.root)}")
                return True
            else:
                print(f"  ⚠️  Relatório gerado com avisos")
                return True
        except Exception as e:
            print(f"  ❌ Erro ao gerar relatório: {e}")
            return False

    def create_summary(self):
        """Cria um resumo da execução."""
        self.print_step(6, "Criando resumo da execução", 6)

        summary_file = self.root / "EXECUCAO_RESUMO.txt"
        
        # Contar arquivos gerados
        num_images = len(list((self.outputs_dir / "reconstructed").glob("*.png")))
        num_figures = len(list((self.outputs_dir / "figures").glob("*")))
        num_checkpoints = len(list((self.outputs_dir / "checkpoints").glob("*.pt")))

        summary = f"""
╔════════════════════════════════════════════════════════════════╗
║           RESUMO DA EXECUÇÃO - {self.timestamp}            ║
╚════════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS GERADAS:
  • Imagens reconstruídas: {num_images}
  • Figuras de análise: {num_figures}
  • Checkpoints salvos: {num_checkpoints}
  • Pasta de backup: outputs_execucao_{self.timestamp}/

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
  • Backup salvo em: {self.root}/outputs_execucao_{self.timestamp}
  • Compare com: outputs/

Para reexecutar:
  python scripts/execute_and_report.py --full
  ou
  python scripts/automate.py pipeline
"""

        try:
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"  📋 Resumo salvo em: {summary_file.name}")
            print(summary)
            return True
        except Exception as e:
            print(f"  ❌ Erro ao criar resumo: {e}")
            return False

    def run_full_pipeline(self, config="config/experiments.yaml", quick=False):
        """Executa o pipeline completo."""
        self.print_header("🚀 PIPELINE COMPLETO DE EXECUÇÃO E RELATÓRIO")
        
        start_time = time.time()
        print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        steps = [
            ("Backup", self.backup_outputs),
            ("Limpeza", self.clean_outputs),
            ("Experimentos", lambda: self.run_experiments(config, quick)),
            ("Evidências", self.generate_evidences),
            ("Relatório", self.generate_report),
            ("Resumo", self.create_summary),
        ]

        results = []
        for step_name, step_func in steps:
            try:
                success = step_func()
                results.append((step_name, success))
                if not success and step_name in ["Experimentos", "Relatório"]:
                    print(f"\n⚠️  Pipeline continuando apesar de erro em: {step_name}\n")
            except Exception as e:
                print(f"\n❌ Erro fatal em {step_name}: {e}\n")
                results.append((step_name, False))
                break

        elapsed = time.time() - start_time
        self.print_header("📊 RESUMO DO PIPELINE")
        
        for step_name, success in results:
            status = "✅" if success else "❌"
            print(f"{status} {step_name}")

        print(f"\n⏱️  Tempo total: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Sugestões finais
        report_path = self.root / "report" / "relatorio_final.md"
        if report_path.exists():
            print(f"📖 Leia o relatório: {report_path.relative_to(self.root)}")


def main():
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
        """
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Executar matriz completa (padrão)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Executar matriz reduzida (teste rápido)"
    )
    parser.add_argument(
        "--backup-only",
        action="store_true",
        help="Apenas fazer backup"
    )
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Apenas limpar outputs"
    )
    parser.add_argument(
        "--config",
        default="config/experiments.yaml",
        help="Arquivo de configuração (padrão: config/experiments.yaml)"
    )

    args = parser.parse_args()

    execution = ProjectExecution()

    if args.backup_only:
        execution.backup_outputs()
    elif args.clean_only:
        execution.clean_outputs()
    else:
        # Pipeline completo
        execution.run_full_pipeline(
            config=args.config,
            quick=args.quick
        )


if __name__ == "__main__":
    main()
