#%%
from matplotlib import pyplot as plt
import matplotlib
import skrf as rf
from skrf import NetworkSet
import numpy as np
from scipy import signal

ntwk1 = rf.Network ('/home/ori/Documents/Work/NanoVNA/Suraj/New_VNA/SiO2-Background.s1p')
rf.stylely (style_file='skrf2.mplstyle')

fig=plt.figure ()
ax = plt.subplot (1,1,1)
ntwk1.plot_s_db(label="SiO2 peaks")
ntwk1.frequency.unit='Ghz'

s_leng=np.size (ntwk1.f)
s_data=np.zeros ((s_leng,2))
s_data[:,0]=ntwk1.f[:]
s_data[:,1]=ntwk1.s_db[:,0,0]

pk = signal.argrelmin (s_data[:,1],order=10)
pks=np.array (pk[0])
for i in range (np.size (pk)):
    plt.text (s_data[pks[i],0],s_data[pks[i],1],format(s_data[pks[i],0],'.3e'))

plt.plot (s_data[pk,0],s_data[pk,1],"ro")
# %%
