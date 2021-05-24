import torch

if torch.cuda.is_available():
    print("yes")
else:
    print("no")