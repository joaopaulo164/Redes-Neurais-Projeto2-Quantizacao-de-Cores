import torch
from src.models import SOM,GNG,TorchKMeans
X=torch.rand(120,3)
def test_som():assert SOM(2,2,epochs=1,batch_size=32).fit(X).quantize(X)[0].shape==X.shape
def test_kmeans():assert TorchKMeans(4,max_iter=3).fit(X).quantize(X)[0].shape==X.shape
def test_gng():
 m=GNG(4,steps=50,insertion_interval=10).fit(X);assert m.quantize(X)[0].shape==X.shape and len(m.prototypes())<=4
