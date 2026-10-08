#!/usr/bin/env python3
"""
export_current_checkpoints.py

Script CLI para exportar todos os checkpoints em outputs/checkpoints/ para formatos auditáveis.

Exporta: estrutura TXT, resumo CSV, históricos CSV, protótipos CSV, arestas CSV,
validação cruzada CSV, e manifesto JSON.

Uso:
  python scripts/export_current_checkpoints.py
  python scripts/export_current_checkpoints.py --input-dir custom/checkpoints --output-dir custom/exports
  python scripts/export_current_checkpoints.py --format csv-only
  python scripts/export_current_checkpoints.py --history-stride 2 --prototype-max-rows 50
  python scripts/export_current_checkpoints.py --strict --overwrite
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Adiciona src/ ao path para importar módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from validation.checkpoint_exporter import CheckpointExporter


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configura logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    return logging.getLogger(__name__)


def main():
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(
        description='Exporta checkpoints .pt para formatos auditáveis (TXT, CSV, JSON)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos:
  python scripts/export_current_checkpoints.py
      → Exporta outputs/checkpoints/ para validation/

  python scripts/export_current_checkpoints.py --strict
      → Modo strict: falha se erros em validação/limpeza

  python scripts/export_current_checkpoints.py \\
      --input-dir outputs_backup/checkpoints \\
      --output-dir outputs_backup/exports
      → Exporta de diretório customizado

  python scripts/export_current_checkpoints.py \\
      --history-stride 2 \\
      --prototype-max-rows 50
      → Amostragem de histórico (metade) e protótipos (primeiros 50)

  python scripts/export_current_checkpoints.py \\
      --format csv-only
      → Apenas CSVs, sem TXT e JSON

  python scripts/export_current_checkpoints.py \\
      --trusted-checkpoints \\
      --overwrite
      → Confia em checkpoints (map_location=None) e sobrescreve arquivos existentes
        ''',
    )

    parser.add_argument(
        '--input-dir',
        type=Path,
        default=None,
        help='Diretório com checkpoints .pt (default: outputs/checkpoints/)',
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help='Diretório para arquivos exportados (default: validation/)',
    )

    parser.add_argument(
        '--runs-csv',
        type=Path,
        default=None,
        help='Caminho para runs.csv (default: outputs/metrics/runs.csv)',
    )

    parser.add_argument(
        '--history-stride',
        type=int,
        default=1,
        help='Amostragem de histórico: 1=todos, 2=metade, etc. (default: 1)',
    )

    parser.add_argument(
        '--history-mode',
        choices=['full', 'summary', 'none'],
        default='full',
        help='Modo de exportação do histórico: full|summary|none (default: full)',
    )

    parser.add_argument(
        '--prototype-max-rows',
        type=int,
        default=100,
        help='Máximo de protótipos/centróides a exportar por checkpoint (default: 100)',
    )

    parser.add_argument(
        '--trusted-checkpoints',
        action='store_true',
        help='Carrega checkpoints sem map_location=cpu (menos seguro)',
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Modo strict: falha em erros, não continua',
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Sobrescreve arquivos existentes',
    )

    parser.add_argument(
        '--format',
        choices=['all', 'csv-only', 'json-only', 'txt-only'],
        default='all',
        help='Quais formatos exportar (default: all)',
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Logging verboso (DEBUG)',
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(verbose=args.verbose)

    # Resolve paths com defaults
    input_dir = args.input_dir or (project_root / 'outputs' / 'checkpoints')
    output_dir = args.output_dir or (project_root / 'validation')
    runs_csv = args.runs_csv or (project_root / 'outputs' / 'metrics' / 'runs.csv')

    logger.info("=== Exportador de Checkpoints ===")
    logger.info(f"Input:  {input_dir}")
    logger.info(f"Output: {output_dir}")
    logger.info(f"Runs CSV: {runs_csv if runs_csv.exists() else '(não encontrado)'}")
    logger.info(f"History Stride: {args.history_stride}")
    logger.info(f"History Mode: {args.history_mode}")
    logger.info(f"Prototype Max Rows: {args.prototype_max_rows}")
    logger.info(f"Trusted Checkpoints: {args.trusted_checkpoints}")
    logger.info(f"Strict Mode: {args.strict}")
    logger.info("")

    # Verificar se input existe
    if not input_dir.exists():
        logger.error(f"Diretório não existe: {input_dir}")
        return 1

    # Verificar se há checkpoints
    checkpoint_files = list(input_dir.glob('*.pt'))
    if not checkpoint_files:
        logger.warning(f"Nenhum checkpoint encontrado em {input_dir}")
        return 0

    logger.info(f"Encontrados {len(checkpoint_files)} checkpoints")

    # Verificar se output_dir precisa ser limpo
    if output_dir.exists() and not args.overwrite:
        existing_exports = list(output_dir.glob('checkpoints_atuais_*'))
        if existing_exports and not args.overwrite:
            logger.warning(
                f"Arquivos de exportação já existem em {output_dir}. "
                f"Use --overwrite para sobrescrever."
            )

    # Criar exportador
    exporter = CheckpointExporter(
        checkpoint_dir=input_dir,
        output_dir=output_dir,
        runs_csv_path=runs_csv if runs_csv.exists() else None,
        trusted_checkpoints=args.trusted_checkpoints,
        strict_mode=args.strict,
        logger_obj=logger,
    )

    logger.info("")
    logger.info("Iniciando exportação...")
    start_time = datetime.now()

    try:
        # Determinar se consolida based on format
        consolidate = args.format in ('all', 'csv-only', 'txt-only', 'json-only')

        output_files = exporter.export_all(
            history_stride=args.history_stride,
            prototype_max_rows=args.prototype_max_rows,
            consolidate=consolidate,
            history_mode=args.history_mode,
        )

        # Filtrar por formato se necessário
        if args.format != 'all':
            if args.format == 'csv-only':
                output_files = {
                    k: v for k, v in output_files.items() if 'csv' in k
                }
            elif args.format == 'json-only':
                output_files = {
                    k: v for k, v in output_files.items() if 'json' in k
                }
            elif args.format == 'txt-only':
                output_files = {
                    k: v for k, v in output_files.items() if 'txt' in k
                }

        elapsed = datetime.now() - start_time

        logger.info("")
        logger.info("=== Resultado ===")
        logger.info(f"Checkpoints Exportados: {len(exporter.exported_checkpoints)}")
        logger.info(f"Tempo Total: {elapsed.total_seconds():.2f}s")
        logger.info("")

        if output_files:
            logger.info("Arquivos Gerados:")
            for key, path in sorted(output_files.items()):
                size_mb = path.stat().st_size / (1024 * 1024)
                logger.info(f"  [{key}] {path.name} ({size_mb:.2f} MB)")
        else:
            logger.warning("Nenhum arquivo foi gerado")
            return 1

        logger.info("")
        logger.info("✓ Exportação concluída com sucesso")
        return 0

    except Exception as e:
        logger.exception(f"Erro durante exportação: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
