#%%
from skrf.calibration import OnePort
import skrf as rf
%matplotlib inline
from pylab import *
rf.stylely()


tier1_ideals = rf.read_all_networks('/home/ori/Downloads/scikit-rf-master/doc/source/examples/metrology/oneport_tiered_calibration/tier1/ideals/')
tier1_measured = rf.read_all_networks('/home/ori/Downloads/scikit-rf-master/doc/source/examples/metrology/oneport_tiered_calibration/tier1/measured/')


tier1 = OnePort(measured = tier1_measured,
                ideals = tier1_ideals,
                name = 'tier1',
                sloppy_input=True)
tier1

# %%
