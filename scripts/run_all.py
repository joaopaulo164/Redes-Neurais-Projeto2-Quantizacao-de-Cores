import argparse,sys,yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from src.data.images import list_images
from src.experiments.runner import run, aggregate


def load_config(path):
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    with open(config_path, encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}

    config.setdefault('data_dir', 'data/raw')
    config.setdefault('output_dir', 'outputs')

    for key in ['data_dir', 'output_dir']:
        value = config[key]
        if not Path(value).is_absolute():
            config[key] = str(ROOT / value)

    missing = [key for key in ['data_dir', 'output_dir', 'seeds', 'capacities', 'models'] if key not in config]
    if missing:
        raise KeyError(
            f"Config inválido '{config_path}': faltam chaves obrigatórias: {missing}. "
            "Use config/experiments.yaml ou inclua data_dir/output_dir no arquivo."
        )

    return config


p = argparse.ArgumentParser()
p.add_argument('--config', default='config/experiments.yaml')
a = p.parse_args()

c = load_config(a.config)
images = list_images(c['data_dir'])
print(f'{len(images)} imagens encontradas')

for im in images:
    for m in c['models']:
        for k in c['capacities']:
            for s in c['seeds']:
                print(im.name, m, k, s)
                run(im, m, k, s, c)

aggregate(c['output_dir'])
