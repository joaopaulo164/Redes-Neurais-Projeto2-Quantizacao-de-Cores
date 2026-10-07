from pathlib import Path
from PIL import Image
import numpy as np, torch
EXT={'.png','.jpg','.jpeg','.bmp','.tif','.tiff','.webp'}
def list_images(folder): return sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in EXT)
def load_image(path,device='cpu'):
 a=np.asarray(Image.open(path).convert('RGB'),dtype=np.float32)/255.; h,w,_=a.shape
 return torch.from_numpy(a.reshape(-1,3)).to(device),(h,w)
def sample_pixels(x,n,seed):
 if len(x)<=n:return x.clone()
 g=torch.Generator(device=x.device).manual_seed(seed)
 return x[torch.randperm(len(x),generator=g,device=x.device)[:n]]
def save_image(x,shape,path):
 a=x.detach().cpu().clamp(0,1).reshape(*shape,3).numpy()
 Image.fromarray((a*255).round().astype('uint8')).save(path)
