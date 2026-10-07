from pathlib import Path
from time import perf_counter
import pandas as pd,torch
from src.data.images import load_image,sample_pixels,save_image
from src.models import SOM,GNG,TorchKMeans
from src.metrics.evaluation import evaluate,usage,topology
from src.visualization.plots import make_plots
def build(name,k,c,device,seed):
 if name=='som':s=int(k**.5);return SOM(s,s,device=device,seed=seed,**c['som'])
 if name=='gng':return GNG(k,device=device,seed=seed,**c['gng'])
 return TorchKMeans(k,device=device,seed=seed,**c['kmeans'])
def run(image,name,k,seed,c):
 device=c.get('device','cpu');device='cpu' if device.startswith('cuda') and not torch.cuda.is_available() else device;out=Path(c['output_dir'])
 for d in ['checkpoints','reconstructed','figures','metrics','tables']:(out/d).mkdir(parents=True,exist_ok=True)
 torch.manual_seed(seed);x,shape=load_image(image,device);train=sample_pixels(x,c['max_train_pixels'],seed);m=build(name,k,c,device,seed);key=f'{Path(image).stem}_{name}_{k}_s{seed}'
 t=perf_counter();m.fit(train);tt=perf_counter()-t;t=perf_counter();rec,a=m.quantize(x,c['inference_batch_size']);ti=perf_counter()-t
 e=evaluate(x,rec,shape);u=usage(a,len(m.prototypes()));te=topology(m,x,name,c['inference_batch_size']);de=e.pop('delta_e_map');save_image(rec,shape,out/'reconstructed'/f'{key}.png');make_plots(x,rec,shape,de,u['counts'],m.prototypes(),out/'figures'/key,f'{name.upper()} {k}',list(m.edges) if name=='gng' else None,seed);m.save(out/'checkpoints'/f'{key}.pt')
 r={'run_id':key,'image_name':Path(image).name,'model':name,'capacity_requested':k,'capacity_actual':len(m.prototypes()),'seed':seed,'train_pixels':len(train),'total_pixels':len(x),**e,'topographic_error':te,'active_neurons':u['active_neurons'],'inactive_neurons':u['inactive_neurons'],'usage_entropy':u['usage_entropy'],'training_time_s':tt,'inference_time_s':ti,'device':device}
 csv=out/'metrics'/'runs.csv';pd.DataFrame([r]).to_csv(csv,mode='a',header=not csv.exists(),index=False);return r
def aggregate(out='outputs'):
 out=Path(out);df=pd.read_csv(out/'metrics'/'runs.csv');metrics=['quantization_error','topographic_error','mae_rgb','mse_rgb','rmse_rgb','psnr','mean_delta_e','std_delta_e','max_delta_e','active_neurons','inactive_neurons','usage_entropy','training_time_s','inference_time_s'];s=df.groupby(['image_name','model','capacity_requested'])[metrics].agg(['mean','std']).reset_index();s.columns=['_'.join(str(x) for x in c if x) for c in s.columns];s.to_csv(out/'tables'/'summary.csv',index=False);return s
