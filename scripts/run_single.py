import argparse,sys,yaml
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));from src.experiments.runner import run
p=argparse.ArgumentParser();p.add_argument('--image',required=True);p.add_argument('--model',choices=['som','gng','kmeans'],required=True);p.add_argument('--capacity',type=int,choices=[16,64,256],required=True);p.add_argument('--seed',type=int,default=13);p.add_argument('--config',default='config/experiments.yaml');a=p.parse_args();c=yaml.safe_load(open(a.config,encoding='utf-8'));print(run(a.image,a.model,a.capacity,a.seed,c))
