#%%
import skrf as rf
%matplotlib inline
from pylab import *
rf.stylely()

from skrf.calibration import OnePort
#from skrf.calibration import TwoPortOnePath
from skrf.media import RectangularWaveguide
#from skrf import two_port_reflect as tpr
from skrf import mil
from skrf import NetworkSet
from skrf import Network, Frequency

#%%
raw = rf.read_all_networks("/home/ori/Documents/Work/VNA/oneport_tiered_calibration/tier1/measured/")
data1 = Network('/home/ori/Documents/Work/VNA/oneport_tiered_calibration/tier1/measured/load.S1P')
data1
#%%
# pull frequency information from measurements
frequency = raw['/home/ori/Documents/Work/VNA/oneport_tiered_calibration/tier1/measured/load'].frequency

#%%
# the media object
wg = RectangularWaveguide(frequency=frequency, a=120*mil, z0=50)

# list of 'ideal' responses of the calibration standards
ideals = [wg.short(nports=2),
          tpr(wg.delay_short( 90,'deg'), wg.match()),
          wg.match(nports=2),
          wg.thru()]

# corresponding measurements to the 'ideals'
measured = [raw['short'],
            raw['quarter wave delay short'],
            raw['load'],
            raw['thru']]

# the Calibration object
cal = TwoPortOnePath(measured = measured, ideals = ideals )
# %%

# %%
