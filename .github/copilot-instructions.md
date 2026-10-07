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

## Code Patterns & Conventions

### Reproducibility
- **All randomness seeded**: `torch.Generator(device=device).manual_seed(seed)` in model init/fit
- **Train sample fixed per image/seed**: `sample_pixels()` uses seed; inference uses full image
- **Device fallback**: Code checks `torch.cuda.is_available()`, defaults CPU

### Tensor Conventions
- **RGB tensors**: shape `(N, 3)`, dtype `float32`, range [0,1] (normalized by PIL read, denormalized on save)
- **Batch processing**: All `.predict_bmu()` / `.quantize()` use `batch_size` to avoid memory overflow
- **Assignments**: BMU indices stored as assignment tensor; used for metrics (entropy, active neurons)

### File Naming
- **Checkpoints**: `{image_stem}_{model}_{capacity}_s{seed}.pt` (e.g., `cat_som_16_s13.pt`)
- **Keys**: Same prefix used for figures, reconstructed images, CSV row identifier

### Metrics Pipeline (`src/metrics/evaluation.py`)
- `evaluate(x_original, x_reconstructed, shape)` - Quantization error, image-level metrics (MAE, MSE, RMSE, PSNR), Delta E per pixel
- `usage(assignments, n_prototypes)` - Active/inactive neurons, usage entropy
- `topology(model, x, model_name, batch_size)` - Topographic error (ratio of incorrectly ordered nearest neighbors)

### Visualization Patterns (`src/visualization/plots.py`)
- **Output**: Multi-panel figures (original, reconstructed, Delta E heatmap, histograms, prototype cloud)
- **GNG-specific**: Plots neural graph (edges as lines, nodes as points)

## Common Task Patterns

### Adding a New Model
1. Inherit from `Base` in `src/models/quantizers.py`
2. Implement: `fit(x)`, `predict_bmu(x, batch_size)`, `prototypes()`, `state_dict()`
3. Add hyperparams to config YAML and `build()` function in `src/experiments/runner.py`
4. Add unit test to `tests/test_models.py`

### Modifying Metrics
- Edit `src/metrics/evaluation.py` `evaluate()` function
- New metrics appear in `outputs/metrics/runs.csv` automatically
- Update `runner.py` `aggregate()` metric list for summary CSV

### Tuning Hyperparameters
- Edit `config/experiments.yaml` or create variant (e.g., `experiments-quick.yaml`)
- Run: `python scripts/run_all.py --config config/experiments-quick.yaml`
- Quick test: 1-2 images, 1-2 seeds, single capacity (avoid 225+ runs)

## Testing & Validation
- **Unit tests**: `pytest` checks model shapes in-memory (minimal data)
- **Integration**: Run single experiment, inspect `outputs/reconstructed/*.png`, `outputs/metrics/runs.csv`
- **Color validation**: `validate_unique_colors.py` ensures quantizer uses distinct prototypes (avoid duplicates)

## Output Structure
```
outputs/
  checkpoints/          ← Saved model states (.pt)
  reconstructed/        ← Quantized images (.png)
  figures/              ← Per-experiment plots (.png)
  metrics/runs.csv      ← Raw results (5+ MB after full matrix)
  tables/summary.csv    ← Aggregated mean/std by image/model/capacity
```

## Critical Edge Cases
- **Empty image folder**: `run_all.py` detects no images, logs "0 images found"
- **Insufficient CUDA memory**: Device fallback to CPU handled; no error thrown
- **Capacity > image pixels**: All pixels become unique prototypes; GNG skips insertion
- **Seed consistency**: Must manually reset seeds between independent runs (scripts do this)
