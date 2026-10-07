import math, torch
from skimage.color import rgb2lab,deltaE_ciede2000
def evaluate(original,recon,shape):
 d=original-recon;mse=float((d*d).mean());a=original.detach().cpu().numpy().reshape(*shape,3);b=recon.detach().cpu().numpy().reshape(*shape,3);de=deltaE_ciede2000(rgb2lab(a),rgb2lab(b))
 return {'quantization_error':float(torch.norm(d,dim=1).mean()),'mae_rgb':float(d.abs().mean()),'mse_rgb':mse,'rmse_rgb':math.sqrt(mse),'psnr':float('inf') if mse==0 else 10*math.log10(1/mse),'mean_delta_e':float(de.mean()),'std_delta_e':float(de.std()),'max_delta_e':float(de.max()),'delta_e_map':de}
def usage(assign,n):
 c=torch.bincount(assign.cpu(),minlength=n);p=c.float()/c.sum();nz=p>0
 return {'active_neurons':int((c>0).sum()),'inactive_neurons':int((c==0).sum()),'usage_entropy':float(-(p[nz]*p[nz].log2()).sum()),'counts':c.numpy()}
def topology(model,x,kind,batch=65536):
 if kind=='kmeans':return float('nan')
 b=model.two_best(x,batch).cpu()
 if kind=='som':
  r1,c1=b[:,0]//model.cols,b[:,0]%model.cols;r2,c2=b[:,1]//model.cols,b[:,1]%model.cols;return float((((r1-r2).abs()+(c1-c2).abs())!=1).float().mean())
 e=set(model.edges);return sum((min(int(a),int(z)),max(int(a),int(z))) not in e for a,z in b.numpy())/len(b)
