#!/usr/bin/env python
"""
Automation script para gerenciar o projeto de quantização de cores com redes neurais.
Fornece um CLI interativo para executar experimentos, testes e gerar relatórios.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time


class ProjectAutomation:
    """Automação do projeto de quantização de cores."""

    def __init__(self):
        self.root = Path(__file__).resolve().parents[1]
        self.data_dir = self.root / "data" / "raw"
        self.output_dir = self.root / "outputs"

    def run_command(self, *args, description=""):
        """Execute um comando e retorne o status."""
        if description:
            print(f"\n{'=' * 60}")
            print(f"🚀 {description}")
            print(f"{'=' * 60}")
        print(f"Executando: {' '.join(args)}\n")
        try:
            result = subprocess.run(args, cwd=self.root, check=False)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

    def install_dependencies(self):
        """Instala dependências do projeto."""
        return self.run_command(
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt",
            description="Instalando dependências"
        )

    def run_tests(self):
        """Executa testes unitários."""
        return self.run_command(
            sys.executable, "-m", "pytest", "-q",
            description="Executando testes"
        )

    def single_experiment(self, image=None, model="som", capacity=16, seed=13, config=None):
        """Executa um único experimento."""
        if not image:
            images = list(self.data_dir.glob("*.png")) + list(self.data_dir.glob("*.jpg"))
            if not images:
                print(f"❌ Nenhuma imagem encontrada em {self.data_dir}")
                return False
            image = str(images[0])
        
        config = config or "config/experiments.yaml"
        cmd = [
            sys.executable, "scripts/run_single.py",
            "--image", image,
            "--model", model,
            "--capacity", str(capacity),
            "--seed", str(seed),
            "--config", config
        ]
        return self.run_command(
            *cmd,
            description=f"Experimento Single: {Path(image).name} | {model} | {capacity} cores | seed {seed}"
        )

    def full_matrix(self, config=None):
        """Executa matriz completa de experimentos."""
        config = config or "config/experiments.yaml"
        return self.run_command(
            sys.executable, "scripts/run_all.py", "--config", config,
            description="Executando matriz completa de experimentos"
        )

    def quick_test(self):
        """Executa matriz reduzida (quick test)."""
        return self.run_command(
            sys.executable, "scripts/run_all.py",
            "--config", "config/experiments - teste rapido.yaml",
            description="Teste rápido: matriz reduzida"
        )

    def generate_report(self):
        """Gera relatório Markdown."""
        return self.run_command(
            sys.executable, "scripts/generate_report.py",
            description="Gerando relatório Markdown"
        )

    def validate_colors(self):
        """Valida cores únicas nos experimentos."""
        return self.run_command(
            sys.executable, "scripts/validate_unique_colors.py",
            description="Validando cores únicas"
        )

    def run_execute_and_report(self):
        """Executa o pipeline completo com backup e relatório."""
        return self.run_command(
            sys.executable, "scripts/execute_and_report.py", "--full",
            description="Pipeline com backup, limpeza, experimentos e relatório"
        )

    def clean_outputs(self):
        """Remove arquivos de saída."""
        dirs_to_clean = [
            self.output_dir / "checkpoints",
            self.output_dir / "reconstructed",
            self.output_dir / "figures",
            self.output_dir / "metrics",
            self.output_dir / "tables"
        ]
        
        print(f"\n{'=' * 60}")
        print("🧹 Limpando arquivos de saída")
        print(f"{'=' * 60}\n")
        
        for d in dirs_to_clean:
            if d.exists():
                for f in d.glob("*"):
                    if f.is_file():
                        f.unlink()
                        print(f"  Removido: {f.name}")
        print("\n✅ Limpeza concluída!")
        return True

    def full_pipeline(self):
        """Executa pipeline completo: install → test → run_all → report."""
        print(f"\n{'=' * 60}")
        print("🔄 PIPELINE COMPLETO")
        print(f"{'=' * 60}")
        print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        steps = [
            ("Instalar dependências", self.install_dependencies),
            ("Executar testes", self.run_tests),
            ("Executar matriz completa", self.full_matrix),
            ("Gerar relatório", self.generate_report),
            ("Validar cores únicas", self.validate_colors),
        ]
        
        start_time = time.time()
        results = []
        
        for step_name, step_func in steps:
            success = step_func()
            results.append((step_name, success))
            if not success:
                print(f"\n⚠️  Pipeline pausado em: {step_name}")
                break
        
        elapsed = time.time() - start_time
        print(f"\n{'=' * 60}")
        print("📊 RESUMO")
        print(f"{'=' * 60}")
        for step_name, success in results:
            status = "✅" if success else "❌"
            print(f"{status} {step_name}")
        print(f"\nTempo total: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def interactive_menu(self):
        """Menu interativo para automação."""
        while True:
            print(f"\n{'=' * 60}")
            print("🤖 AUTOMAÇÃO - QUANTIZAÇÃO DE CORES")
            print(f"{'=' * 60}")
            print("1️⃣  Instalar dependências")
            print("2️⃣  Executar testes")
            print("3️⃣  Experimento único (demo)")
            print("4️⃣  Matriz completa")
            print("5️⃣  Teste rápido (matriz reduzida)")
            print("6️⃣  Gerar relatório")
            print("7️⃣  Validar cores")
            print("8️⃣  Limpar outputs")
            print("9️⃣  Pipeline completo (install → test → run → report)")
            print("🔟 Pipeline com backup (backup → limpeza → full → report)")
            print("0️⃣  Sair")
            print(f"{'=' * 60}\n")
            
            choice = input("Escolha uma opção (0-10): ").strip()
            
            if choice == "0":
                print("\n👋 Até logo!")
                break
            elif choice == "1":
                self.install_dependencies()
            elif choice == "2":
                self.run_tests()
            elif choice == "3":
                self.single_experiment()
            elif choice == "4":
                self.full_matrix()
            elif choice == "5":
                self.quick_test()
            elif choice == "6":
                self.generate_report()
            elif choice == "7":
                self.validate_colors()
            elif choice == "8":
                self.clean_outputs()
            elif choice == "9":
                self.full_pipeline()
            elif choice == "10":
                self.run_execute_and_report()
            else:
                print("❌ Opção inválida!")


def main():
    parser = argparse.ArgumentParser(
        description="Automação para projeto de quantização de cores com redes neurais",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python scripts/automate.py install           # Instalar dependências
  python scripts/automate.py test              # Rodar testes
  python scripts/automate.py single            # Experimento único
  python scripts/automate.py full              # Matriz completa
  python scripts/automate.py quick             # Teste rápido
  python scripts/automate.py report            # Gerar relatório
  python scripts/automate.py pipeline          # Pipeline completo
  python scripts/automate.py clean             # Limpar outputs
  python scripts/automate.py interactive       # Menu interativo (padrão)
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    
    subparsers.add_parser("install", help="Instalar dependências")
    subparsers.add_parser("test", help="Executar testes")
    subparsers.add_parser("single", help="Experimento único (demo)")
    subparsers.add_parser("full", help="Matriz completa")
    subparsers.add_parser("quick", help="Teste rápido")
    subparsers.add_parser("report", help="Gerar relatório")
    subparsers.add_parser("validate", help="Validar cores")
    subparsers.add_parser("clean", help="Limpar outputs")
    subparsers.add_parser("pipeline", help="Pipeline completo")
    subparsers.add_parser("interactive", help="Menu interativo")
    
    args = parser.parse_args()
    automation = ProjectAutomation()
    
    if args.command == "install":
        automation.install_dependencies()
    elif args.command == "test":
        automation.run_tests()
    elif args.command == "single":
        automation.single_experiment()
    elif args.command == "full":
        automation.full_matrix()
    elif args.command == "quick":
        automation.quick_test()
    elif args.command == "report":
        automation.generate_report()
    elif args.command == "validate":
        automation.validate_colors()
    elif args.command == "clean":
        automation.clean_outputs()
    elif args.command == "pipeline":
        automation.full_pipeline()
    elif args.command == "interactive" or not args.command:
        automation.interactive_menu()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
