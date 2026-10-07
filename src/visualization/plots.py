import numpy as np, matplotlib.pyplot as plt
def make_plots(original,recon,shape,de,counts,prototypes,path_prefix,title,edges=None,seed=13):
 a=original.cpu().numpy().reshape(*shape,3);b=recon.cpu().numpy().reshape(*shape,3)
 f,ax=plt.subplots(1,2,figsize=(12,5));ax[0].imshow(a);ax[0].set_title('Original');ax[1].imshow(b);ax[1].set_title(title)
 for x in ax:x.axis('off')
 f.tight_layout();f.savefig(str(path_prefix)+'_comparison.png',dpi=150);plt.close(f)
 f,ax=plt.subplots();im=ax.imshow(de,cmap='magma');ax.axis('off');ax.set_title('Mapa Delta E CIEDE2000');f.colorbar(im,ax=ax);f.savefig(str(path_prefix)+'_deltae.png',dpi=150);plt.close(f)
 diff=np.linalg.norm(a.reshape(-1,3)-b.reshape(-1,3),axis=1);f,ax=plt.subplots(1,2,figsize=(12,4));ax[0].hist(diff,bins=50);ax[0].set_title('Diferença RGB');ax[1].bar(range(len(counts)),counts);ax[1].set_title('Vitórias');f.tight_layout();f.savefig(str(path_prefix)+'_hist.png',dpi=150);plt.close(f)
 p=original.cpu().numpy();q=prototypes.cpu().numpy();rng=np.random.default_rng(seed);p=p[rng.choice(len(p),min(10000,len(p)),replace=False)];f=plt.figure();ax=f.add_subplot(111,projection='3d');ax.scatter(p[:,0],p[:,1],p[:,2],c=p,s=2,alpha=.12);ax.scatter(q[:,0],q[:,1],q[:,2],c=q,edgecolor='black',s=40)
 if edges:
  for i,j in edges:ax.plot(q[[i,j],0],q[[i,j],1],q[[i,j],2],color='black',lw=.6)
 ax.set_xlabel('R');ax.set_ylabel('G');ax.set_zlabel('B');f.savefig(str(path_prefix)+'_rgb.png',dpi=150);plt.close(f)
