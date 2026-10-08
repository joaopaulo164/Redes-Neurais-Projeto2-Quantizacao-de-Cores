# Copilot Instructions: Neural Color Quantization

## Project Overview
**Projeto 2** implements three PyTorch color quantizers (SOM, GNG, and k-means). YAML configurations drive reproducible experiments that produce reconstructed images, metrics, plots, checkpoints, and aggregated CSV reports. Run commands from the project root. Image tensors use RGB values normalized to [0, 1].

## Core Architecture

### Three-Phase Pipeline Per Experiment
1. **Fit** (`model.fit(x)`) - Train quantizer on sampled pixels (see `max_train_pixels` in config)
2. **Quantize** (`model.quantize(x, batch_size)`) - Inference on all image pixels, returns reconstructed image and assignments
3. **Evaluate** - Metrics (quantization error, MAE/MSE/RMSE/PSNR, Delta E CIEDE2000) + topology analysis

### Key Classes in `src/models/quantizers.py`
- **Base** - Shared implementation of `.quantize()` and `.save(path)`; concrete quantizers provide `.predict_bmu()`, `.prototypes()`, and `.state_dict()`.
- **SOM** - Self-Organizing Map: rows/cols grid, neighborhood decay via sigma, weights shape `(rows*cols, 3)`
- **GNG** - Growing Neural Gas: dynamic node insertion, edge aging, error tracking; max nodes capped at capacity
- **TorchKMeans** - k-means++: centroid initialization, early stopping via tolerance threshold

### Data Flow
```
data/raw/{image}.png 
  → load_image() [PIL → [0,1] RGB tensor]
  → sample_pixels(x, max_train_pixels, seed)  [reproducible per seed]
  → model.fit(train_subset)
  → model.quantize(full_image, inference_batch_size)
  → save_image() → outputs/reconstructed/
  → evaluate() + make_plots() → outputs/figures/
```

## Configuration & Experiments
- **config/experiments.yaml**: YAML defines device, seeds, capacities [16,64,256], model hyperparams
- **Key params**: `max_train_pixels` (default 100k), `inference_batch_size` (65536), device fallback (CUDA→CPU)
- **Hyperparams tuned per model**:
  - SOM: `epochs`, `lr0`/`lrf` (learning rate decay), `sigma_final` (neighborhood decay)
  - GNG: `steps`, `eps_b`/`eps_n` (weights/neighbors learning), `insertion_interval`, `max_edge_age`
  - k-means: `max_iter`, `tolerance`

## Python Development Standards
- Keep one statement per line; do not use semicolons to combine statements.
- Use descriptive names, type hints on functions and methods, and Google-style docstrings for public APIs.
- Preserve seeded random-generator use and output schemas when changing experiment behavior.
- Format Python files with `python -m ruff format --line-length 79 .`.
- Check imports and core lint with `python -m ruff check --select E4,E7,E9,F,I --ignore E402 .`; `E402` is ignored for entry points that deliberately bootstrap `sys.path`.
- Run tests with `python -m pytest -q`.
- Formatting and lint tools (`autopep8`, `black`, and `ruff`) are included in `requirements.txt`; use Ruff for the project's formatter and lint checks.

## Developer Workflows

### Single Experiment
```bash
python scripts/run_single.py --image data/raw/img.png --model som --capacity 16 --seed 13 [--config config/experiments.yaml]
```
Returns dict with metrics; appends row to `outputs/metrics/runs.csv`.

### Full Matrix Execution
```bash
python scripts/run_all.py [--config config/experiments.yaml]
```
Iterates: images × models × capacities × seeds; auto-aggregates to `outputs/tables/summary.csv`.

### Report Generation
```bash
python scripts/generate_report.py
```
Generates Markdown report from CSV metrics; outputs to `report/`.

### Testing & Validation
```bash
python -m pytest -q
python scripts/validate_unique_colors.py  # Color validation per experiment
```

## Project Automation & Backup Discipline
- `scripts/execute_and_report.py --full` and `--quick` back up `outputs/` and `validation/`, clean generated data, then run the selected workflow. The pipeline must stop before cleanup if backup fails, and before experiments if cleanup fails.
- Interactive option 8 and `python scripts/automate.py clean` run `--backup-only` first, then `--clean-only`; cleanup is skipped if backup fails.
- Interactive option 10 runs the complete backup, clean, experiment, validation, report, and summary pipeline.
- `--clean-only`, `make clean`, the PowerShell `clean-outputs` helper, and the VS Code task `Clean: Remove Outputs` are direct cleanup paths and do not create backups. `make clean`, `clean-outputs`, and the VS Code task clear only `outputs/`; `--clean-only` clears `outputs/` and `validation/`.
- `python scripts/automate.py pipeline` and `make pipeline` are basic pipelines without the timestamped backup-and-clean stage. Use interactive option 10 or `scripts/execute_and_report.py` with `--full` or `--quick` for that protected workflow.
- Backups use `outputs_execucao_YYYYMMDD_HHMMSS/` and `validation_execucao_YYYYMMDD_HHMMSS/`. Cleanup must never remove these backup directories.
- Keep timestamped backups out of version control with patterns such as `outputs_execucao_*/` and `validation_execucao_*/`.

## Automation Options

### 1. Interactive Menu (Recommended)
```bash
python scripts/automate.py
# or
python scripts/automate.py interactive
```
The menu includes install, test, demo, full and quick matrices, report generation, color validation, backup-and-clean (option 8), a basic pipeline, the full backup pipeline (option 10), and checkpoint export.

### 2. Command-Line Interface
```bash
python scripts/automate.py install      # Install dependencies
python scripts/automate.py test         # Run tests
python scripts/automate.py single       # Single demo experiment
python scripts/automate.py full         # Full matrix
python scripts/automate.py quick        # Quick test (reduced matrix)
python scripts/automate.py report       # Generate report
python scripts/automate.py validate     # Validate colors
python scripts/automate.py clean        # Back up, then clean outputs and validation
python scripts/automate.py pipeline     # Full pipeline (install→test→run→report)
```

### 3. Full Pipeline Script
```bash
python scripts/execute_and_report.py --quick
python scripts/execute_and_report.py --full
python scripts/execute_and_report.py --backup-only
python scripts/execute_and_report.py --clean-only
```
The full and quick modes create timestamped backups for both `outputs/` and `validation/`, then remove old generated content before running experiments and generating the report. `--backup-only` and `--clean-only` can also be run separately; the latter does not make a backup.

### 4. Make Commands (Unix/Linux/Git Bash)
```bash
make help              # Show all commands
make install           # Install dependencies
make test              # Run tests
make single-demo       # Single experiment demo
make quick-test        # Reduced matrix
make full-matrix       # Complete matrix
make report            # Generate report
make validate          # Validate colors
make clean             # Clean outputs
make pipeline          # Full pipeline
make interactive       # Interactive menu
```

### 5. VS Code Tasks
Press **Ctrl+Shift+P** (Windows/Linux) or **Cmd+Shift+P** (macOS), type `Tasks: Run Task`, and select:
- Setup: Install Dependencies
- Test: Run Pytest
- Experiment: Single Run (Quick Demo)
- Experiment: Full Matrix
- Experiment: Quick Test
- Report: Generate Markdown Report
- Validation: Unique Colors Check
- Clean: Remove Outputs
- Full Pipeline: Setup → Test → Run All → Report

### 6. GitHub Actions (CI/CD)
Automated workflow on `push`, scheduled daily, or manual trigger via GitHub Actions UI:
- Runs tests on Python 3.10, 3.11, 3.12
- Auto-executes quick test on push
- Auto-executes full matrix daily (2 AM UTC)
- Generates report and uploads artifacts

## Output Structure
```
outputs/
  checkpoints/          ← Saved model states (.pt)
  reconstructed/        ← Quantized images (.png)
  figures/              ← Per-experiment plots (.png)
  metrics/runs.csv      ← Raw results (5+ MB after full matrix)
  tables/summary.csv    ← Aggregated mean/std by image/model/capacity

validation/
  validation_unique_colors.csv  ← Unique-color validation summary
  checkpoint audit exports     ← CSV/TXT/JSON files when exported

backup folders (timestamped):
  outputs_execucao_YYYYMMDD_HHMMSS/
  validation_execucao_YYYYMMDD_HHMMSS/
```

## Validation & Evidence
- **Validation script**: `scripts/validate_unique_colors.py` checks whether each reconstructed image uses no more unique colors than the configured capacity
- **Validation output**: CSV file in `validation/` with per-image status and counts
- **Execution evidence**: backup folders preserve prior validation runs and output artifacts for comparison
- **Reproducibility expectation**: a fresh run should produce a clean `outputs/` and `validation/` while retaining old backups for audit and diffing
