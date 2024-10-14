import os, sys
sys.path.append(os.getcwd())


from googlesearch import search
from time import time as t
from rich import print

C = t()
s = search("perplexity", num_results=5, advanced=True)
print(*s, sep="\n")
print(t()-C)

C = t()
s = search("perplexity", num_results=5, advanced=True)
print(*s, sep="\n")
print(t()-C)



# 3.5
# render 0.6 + 0.3 = 0.9