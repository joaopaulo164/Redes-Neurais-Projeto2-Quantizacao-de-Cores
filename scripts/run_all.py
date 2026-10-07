import argparse,sys,yaml
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));from src.data.images import list_images;from src.experiments.runner import run,aggregate
p=argparse.ArgumentParser();p.add_argument('--config',default='config/experiments.yaml');a=p.parse_args();c=yaml.safe_load(open(a.config,encoding='utf-8'));images=list_images(c['data_dir']);print(f'{len(images)} imagens encontradas')
for im in images:
 for m in c['models']:
  for k in c['capacities']:
   for s in c['seeds']:print(im.name,m,k,s);run(im,m,k,s,c)
aggregate(c['output_dir'])
