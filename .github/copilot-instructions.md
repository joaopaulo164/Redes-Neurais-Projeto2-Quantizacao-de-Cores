# Copilot Instructions: Neural Networks Color Quantization

## Project Overview
**Projeto 2** implements three neural network-based color quantizers (SOM, GNG, k-means) for image color reduction in PyTorch. The codebase runs reproducible experiments via YAML config, producing quantized images, error metrics, visualizations, and aggregated CSV reports. All commands run from project root; fixtures use tensors and numpy arrays normalized to [0,1].

## Core Architecture

### Three-Phase Pipeline Per Experiment
1. **Fit** (`model.fit(x)`) - Train quantizer on sampled pixels (see `max_train_pixels` in config)
2. **Quantize** (`model.quantize(x, batch_size)`) - Inference on all image pixels, returns reconstructed image and assignments
3. **Evaluate** - Metrics (quantization error, MAE/MSE/RMSE/PSNR, Delta E CIEDE2000) + topology analysis

### Key Classes in `src/models/quantizers.py`
- **Base** - Abstract interface: `.quantize()`, `.predict_bmu()`, `.prototypes()`, `.save(path)`, `.state_dict()`
- **SOM** - Self-Organizing Map: rows/cols grid, neighborhood decay via sigma, weights shape `(rows*cols, 3)`
- **GNG** - Growing Neural Gas: dynamic node insertion, edge aging, error tracking; max nodes capped at capacity
- **TorchKMeans** - k-means++: centroid initialization, early stopping via tolerance threshold

### Data Flow
```
data/raw/{image}.png 
  → load_image() [PIL → [0,1] RGB tensor]
  → sample_pixels(x, max_train_pixels, seed)  [reproducible per seed]
  → model.fit(train_subset)
  → model.quantize(full_image)
  → save_image() → outputs/reconstructed/
  → evaluate() + make_plots() → outputs/
```

## Configuration & Experiments
- **config/experiments.yaml**: YAML defines device, seeds, capacities [16,64,256], model hyperparams
- **Key params**: `max_train_pixels` (default 100k), `inference_batch_size` (65536), device fallback (CUDA→CPU)
- **Hyperparams tuned per model**:
  - SOM: `epochs`, `lr0`/`lrf` (learning rate decay), `sigma_final` (neighborhood decay)
  - GNG: `steps`, `eps_b`/`eps_n` (weights/neighbors learning), `insertion_interval`, `max_edge_age`
  - k-means: `max_iter`, `tolerance`

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
- **Execution backup pattern**: `outputs_execucao_YYYYMMDD_HHMMSS/` and `validation_execucao_YYYYMMDD_HHMMSS/` are created before each pipeline run
- **Cleanup policy**: both `outputs/` and `validation/` are reset before running experiments so each execution starts from a clean state
- **Safety rule**: backup folders are never deleted by the cleanup step; they are preserved for comparison and auditing
- **Git ignore policy**: use wildcard patterns such as `outputs_execucao_*/` and `validation_execucao_*/` to keep timestamped backups out of version control

## Automation Options

### 1. Interactive Menu (Recommended)
```bash
python scripts/automate.py
# or
python scripts/automate.py interactive
```
User-friendly menu with options to install dependencies, run tests, execute a demo, run the full matrix, generate reports, validate unique colors, clean generated outputs, and run the full backup→clean→run→report pipeline.

### 2. Command-Line Interface
```bash
python scripts/automate.py install      # Install dependencies
python scripts/automate.py test         # Run tests
python scripts/automate.py single       # Single demo experiment
python scripts/automate.py full         # Full matrix
python scripts/automate.py quick        # Quick test (reduced matrix)
python scripts/automate.py report       # Generate report
python scripts/automate.py validate     # Validate colors
python scripts/automate.py clean        # Clean outputs
python scripts/automate.py pipeline     # Full pipeline (install→test→run→report)
```

### 3. Full Pipeline Script
```bash
python scripts/execute_and_report.py --quick
python scripts/execute_and_report.py --full
python scripts/execute_and_report.py --backup-only
python scripts/execute_and_report.py --clean-only
```
This script creates timestamped backups for both `outputs/` and `validation/`, then removes old generated content before rerunning the experiments and report generation.

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

backup folders (timestamped):
  outputs_execucao_YYYYMMDD_HHMMSS/
  validation_execucao_YYYYMMDD_HHMMSS/
```

## Validation & Evidence
- **Validation script**: `scripts/validate_unique_colors.py` checks whether each reconstructed image uses no more unique colors than the configured capacity
- **Validation output**: CSV file in `validation/` with per-image status and counts
- **Execution evidence**: backup folders preserve prior validation runs and output artifacts for comparison
- **Reproducibility expectation**: a fresh run should produce a clean `outputs/` and `validation/` while retaining old backups for audit and diffing
