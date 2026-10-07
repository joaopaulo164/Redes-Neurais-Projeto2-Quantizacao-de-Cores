import math, torch
class Base:
 def quantize(self,x,batch_size=65536):
  b=self.predict_bmu(x,batch_size); return self.prototypes()[b],b
 def save(self,path): torch.save(self.state_dict(),path)
class SOM(Base):
 def __init__(self,rows,cols,epochs=15,batch_size=512,lr0=.5,lrf=.05,sigma_final=.5,device='cpu',seed=13):
  self.rows,self.cols,self.epochs,self.batch_size=rows,cols,epochs,batch_size; self.lr0,self.lrf=lr0,lrf
  self.s0=max(rows,cols)/2; self.sf=sigma_final; self.device,self.seed=device,seed; self.history=[]
  r,c=torch.meshgrid(torch.arange(rows),torch.arange(cols),indexing='ij'); self.grid=torch.stack([r.flatten(),c.flatten()],1).float().to(device)
 def fit(self,x):
  x=x.to(self.device); g=torch.Generator(device=self.device).manual_seed(self.seed); k=self.rows*self.cols
  self.weights=x[torch.randperm(len(x),generator=g,device=self.device)[:k]].clone() if len(x)>=k else torch.rand(k,3,generator=g,device=self.device)
  total=max(1,self.epochs*math.ceil(len(x)/self.batch_size)-1); step=0
  for ep in range(self.epochs):
   order=torch.randperm(len(x),generator=g,device=self.device); err=0.
   for st in range(0,len(x),self.batch_size):
    z=x[order[st:st+self.batch_size]]; f=step/total; lr=self.lr0*(self.lrf/self.lr0)**f; sig=self.s0*(self.sf/self.s0)**f
    d=torch.cdist(z,self.weights); b=d.argmin(1); err+=d.gather(1,b[:,None]).sum().item()
    gd=((self.grid[None]-self.grid[b][:,None])**2).sum(2); h=torch.exp(-gd/(2*sig*sig)); den=h.sum(0)[:,None].clamp_min(1e-12)
    self.weights+=lr*((h.T@z)/den-self.weights); self.weights.clamp_(0,1); step+=1
   self.history.append({'epoch':ep+1,'qe':err/len(x),'lr':lr,'sigma':sig})
  return self
 def predict_bmu(self,x,batch_size=65536): return torch.cat([torch.cdist(x[i:i+batch_size].to(self.device),self.weights).argmin(1) for i in range(0,len(x),batch_size)])
 def two_best(self,x,batch_size=65536): return torch.cat([torch.cdist(x[i:i+batch_size].to(self.device),self.weights).topk(2,largest=False).indices for i in range(0,len(x),batch_size)])
 def prototypes(self):return self.weights
 def state_dict(self):return {'model':'som','rows':self.rows,'cols':self.cols,'weights':self.weights.cpu(),'history':self.history}
class TorchKMeans(Base):
 def __init__(self,k,max_iter=100,tolerance=1e-4,device='cpu',seed=13):self.k,self.max_iter,self.tolerance,self.device,self.seed=k,max_iter,tolerance,device,seed;self.history=[]
 def fit(self,x):
  x=x.to(self.device);g=torch.Generator(device=self.device).manual_seed(self.seed); centers=[x[torch.randint(len(x),(1,),generator=g,device=self.device)].squeeze()]
  for _ in range(1,self.k):
   d2=torch.cdist(x,torch.stack(centers)).pow(2).min(1).values; idx=torch.multinomial(d2/d2.sum(),1,generator=g) if d2.sum()>0 else torch.randint(len(x),(1,),generator=g,device=self.device);centers.append(x[idx].squeeze())
  self.centroids=torch.stack(centers)
  for it in range(self.max_iter):
   d=torch.cdist(x,self.centroids); lab=d.argmin(1); new=self.centroids.clone()
   for j in range(self.k):
    if (lab==j).any():new[j]=x[lab==j].mean(0)
   shift=torch.norm(new-self.centroids).item();self.centroids=new;self.history.append({'iteration':it+1,'shift':shift})
   if shift<self.tolerance:break
  return self
 def predict_bmu(self,x,batch_size=65536):return torch.cat([torch.cdist(x[i:i+batch_size].to(self.device),self.centroids).argmin(1) for i in range(0,len(x),batch_size)])
 def prototypes(self):return self.centroids
 def state_dict(self):return {'model':'kmeans','centroids':self.centroids.cpu(),'history':self.history}
class GNG(Base):
 def __init__(self,max_nodes,steps=100000,eps_b=.05,eps_n=.0006,insertion_interval=100,max_edge_age=90,alpha=.5,beta=.005,device='cpu',seed=13):
  self.max_nodes,self.steps,self.eb,self.en,self.lam,self.amax,self.alpha,self.beta,self.device,self.seed=max_nodes,steps,eps_b,eps_n,insertion_interval,max_edge_age,alpha,beta,device,seed;self.edges={};self.history=[]
 def edge(self,a,b):return min(int(a),int(b)),max(int(a),int(b))
 def neighbors(self,n):return [b if a==n else a for a,b in self.edges if a==n or b==n]
 def insert(self):
  if len(self.weights)>=self.max_nodes or not self.edges:return
  q=int(self.errors.argmax());ns=self.neighbors(q)
  if not ns:return
  f=max(ns,key=lambda n:float(self.errors[n]));r=len(self.weights);self.weights=torch.cat([self.weights,((self.weights[q]+self.weights[f])/2)[None]])
  self.errors[q]*=self.alpha;self.errors[f]*=self.alpha;self.errors=torch.cat([self.errors,((self.errors[q]+self.errors[f])/2)[None]])
  self.edges.pop(self.edge(q,f),None);self.edges[self.edge(q,r)]=0;self.edges[self.edge(f,r)]=0
 def fit(self,x):
  x=x.to(self.device);g=torch.Generator(device=self.device).manual_seed(self.seed);idx=torch.randperm(len(x),generator=g,device=self.device)[:2];self.weights=x[idx].clone();self.errors=torch.zeros(2,device=self.device)
  for step in range(1,self.steps+1):
   z=x[torch.randint(len(x),(1,),generator=g,device=self.device)].squeeze();d=((self.weights-z)**2).sum(1);b=d.topk(2,largest=False).indices;s1,s2=int(b[0]),int(b[1]);self.errors[s1]+=d[s1]
   for e in list(self.edges):
    if s1 in e:self.edges[e]+=1
   self.weights[s1]+=self.eb*(z-self.weights[s1]);ns=self.neighbors(s1)
   if ns:self.weights[torch.tensor(ns,device=self.device)]+=self.en*(z-self.weights[torch.tensor(ns,device=self.device)])
   self.edges[self.edge(s1,s2)]=0;self.edges={e:a for e,a in self.edges.items() if a<=self.amax}
   if step%self.lam==0:self.insert()
   self.errors*=1-self.beta
   if step%max(1,self.steps//100)==0:self.history.append({'step':step,'nodes':len(self.weights),'edges':len(self.edges)})
  return self
 def predict_bmu(self,x,batch_size=65536):return torch.cat([torch.cdist(x[i:i+batch_size].to(self.device),self.weights).argmin(1) for i in range(0,len(x),batch_size)])
 def two_best(self,x,batch_size=65536):return torch.cat([torch.cdist(x[i:i+batch_size].to(self.device),self.weights).topk(2,largest=False).indices for i in range(0,len(x),batch_size)])
 def prototypes(self):return self.weights
 def state_dict(self):return {'model':'gng','weights':self.weights.cpu(),'errors':self.errors.cpu(),'edges':self.edges,'history':self.history}
