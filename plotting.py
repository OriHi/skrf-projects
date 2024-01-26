#%%
import skrf as rf
from skrf import Network, Frequency
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np 
%matplotlib inline
rf.stylely()
from pylab import *

#%%
# load data for the waveguide to CPW probe
probe1 = rf.Network('/home/ori/Documents/Work/VNA/Capacitor/000.S1P')
probe2 = rf.Network('/home/ori/Documents/Work/VNA/Capacitor/105.S1P')
probe3 = rf.Network('/home/ori/Documents/Work/VNA/Capacitor/102.S1P')
probe4 = rf.Network('/home/ori/Documents/Work/VNA/Capacitor/474.S1P')
#probe5 = rf.Network('/home/ori/Documents/Work/VNA/Capacitor/Cu10x10.s1p')
# we will focus on s11
pr_000 = probe1.s11
pr_105 = probe2.s11
pr_102 = probe3.s11
pr_474 = probe4.s11
#Cu_10x10 = probe5.s11
#frequency set to GHz
pr_000.frequency.unit='ghz'
pr_105.frequency.unit='ghz'
pr_102.frequency.unit='ghz'
pr_474.frequency.unit='ghz'
#Cu_10x10.frequency.unit='ghz'
# add names to waveguide objects for use in plot legends
pr_000.name = 'No Contact, s11'
pr_105.name = '105, s11'
pr_102.name = '102, s11'
pr_474.name = '474, s11'
#Cu_10x10.name = 'Cu 10x10, s11'

wg_list = [pr_000, pr_102, pr_105, pr_474]
#%%
for wg in wg_list:
    wg.plot_s_db(label=wg.name)
title('Frequency Domain')

#%%
figure(figsize=(10,10))
for wg in wg_list:
    subplot(211)
    wg.plot_s_deg(label=wg.name, title='Phase Domain')
    subplot(212)
    wg.plot_s_deg_unwrap(label=wg.name, title='Unwrapped')
#%%
for wg in wg_list:
    wg.plot(abs(wg.s11.group_delay)*1e9, label=wg.name)
    plt.ylabel('Group Delay (ns)')
    plt.title('Group Delay')
    plt.legend()
#%%
for wg in wg_list:
    
# %%
#plot smith chart
fig = figure(figsize=(9,8))
subplot(221)
pr_000.plot_s_smith(m=0,n=0, 
                r=1,
                chart_type='z',
                show_legend=False,
                draw_labels=True,
                draw_vswr=True)
title('No Contact')
subplot(222)
pr_102.plot_s_smith(m=0,n=0, 
                r=1,
                chart_type='z',
                show_legend=False,
                draw_labels=True,
                draw_vswr=True)
title('102')
subplot(223)
pr_105.plot_s_smith(m=0,n=0, 
                r=1,
                chart_type='z',
                show_legend=False,
                draw_labels=True,
                draw_vswr=True)
title('105')
subplot(224)
pr_474.plot_s_smith(m=0,n=0, 
                r=1,
                chart_type='z',
                show_legend=False,
                draw_labels=True,
                draw_vswr=True)
title('106')
fig.tight_layout()
# %%
#plot Impedance Variables
fig = figure(figsize=(9,8))
subplot(211)
Silicon.plot_z_im(label='Silicon Oxide, S11')
SiGr.plot_z_im(label='SiO2 w/Graphene, S11')
Copper.plot_z_im()
Air.plot_z_im()
title('Impedance vs Frequency, Imag(Reactance)')

subplot(212)
Silicon.plot_z_re(label='Silicon Oxide, S11')
SiGr.plot_z_re(label='SiO2 w/Graphene, S11')
Copper.plot_z_re()
Air.plot_z_re()
title('Impedance vs Frequency, Real(Resistance)')
fig.tight_layout()

fig = figure(figsize=(9,8))
subplot(211)
Silicon.plot_y_im(label='Silicon Oxide, S11')
SiGr.plot_y_im(label='SiO2 w/Graphene, S11')
Copper.plot_y_im()
Air.plot_y_im()
title('Admittance vs Frequency, Imag(Susceptance)')

subplot(212)
Silicon.plot_y_re(label='Silicon Oxide, S11')
SiGr.plot_y_re(label='SiO2 w/Graphene, S11')
Copper.plot_y_re()
Air.plot_y_re()
title('Admittance vs Frequency, Real(Conductance)')
fig.tight_layout()
# %%
#plot complex plane
fig = figure(figsize=(9,8))
#Silicon.plot_s_complex(label='Silicon Oxide, S11')
#SiGr.plot_s_complex(label='SiO2 w/Graphene, S11')
#Copper.plot_s_complex()
Air.plot_s_complex()
title('Complex Plane')
fig.tight_layout()
# %%
#plot unwrapped phase
#fig = figure(figsize=(9,8))
Silicon.plot_s_deg_unwrap(label='Silicon Oxide, S11')
SiGr.plot_s_deg_unwrap(ls='--',label='SiO2 w/Graphene, S11')
Copper.plot_s_deg_unwrap()
Air.plot_s_deg_unwrap()
title('Unwrapped Phase')
plt.tight_layout() 
# %%
#get dataframe of reactance
rt_Si = rf.network_2_dataframe(Silicon, ['z_im'])
rt_SiGr = rf.network_2_dataframe(SiGr, ['z_im'])
rt_Cu = rf.network_2_dataframe(Copper, ['z_im'])
rt_air = rf.network_2_dataframe(Air, ['z_im'])

rt_Si.columns = ['Reactance']
rt_Si['Freq'] = rt_Si.index*1e9

rt_SiGr.columns = ['Reactance']
rt_SiGr['Freq'] = rt_SiGr.index*1e9

rt_Cu.columns = ['Reactance']
rt_Cu['Freq'] = rt_Cu.index*1e9

rt_air.columns = ['Reactance']
rt_air['Freq'] = rt_air.index*1e9
# %%
#Calculate Capacitance
rt_Si['Capacitance']=1/(2*np.pi*rt_Si['Freq']*abs(rt_Si['Reactance']))
rt_SiGr['Capacitance']=1/(2*np.pi*rt_SiGr['Freq']*abs(rt_SiGr['Reactance']))
rt_Cu['Capacitance']=1/(2*np.pi*rt_Cu['Freq']*abs(rt_Cu['Reactance']))
rt_air['Capacitance']=1/(2*np.pi*rt_air['Freq']*abs(rt_air['Reactance']))
# %%
#plot values
#plt.plot(rt_Si['Freq'], rt_Si['Capacitance'], label='Silicon Oxide')
plt.plot(rt_SiGr['Freq'], rt_SiGr['Capacitance'], label='SiO2 w/Graphene')
plt.plot(rt_Cu['Freq'], rt_Cu['Capacitance'], label='Copper')
#plt.plot(rt_air['Freq'], rt_air['Capacitance'], label='Air')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Capacitance')
plt.legend()
#title('Derived Capacitance from Reactance')
# %%
rt_Si.to_csv('/home/ori/Documents/Work/VNA/Convert/CapacitanceCalc_Si.csv', sep='\t', index=False)
rt_SiGr.to_csv('/home/ori/Documents/Work/VNA/Convert/CapacitanceCalc_SiGr.csv', sep='\t', index=False)
rt_Cu.to_csv('/home/ori/Documents/Work/VNA/Convert/CapacitanceCalc_Cu.csv', sep='\t', index=False)
rt_air.to_csv('/home/ori/Documents/Work/VNA/Convert/CapacitanceCalc_air.csv', sep='\t', index=False)
# %%
#group delay
gd_Si = abs(Silicon.s11.group_delay) *1e9
gd_SiGr = abs(SiGr.s11.group_delay) *1e9
gd_Cu = abs(Copper.s11.group_delay) *1e9
gd_air = abs(Air.s11.group_delay) *1e9 # in ns

Air.plot(gd_air, label='Air, S11')
Silicon.plot(gd_Si, label='Silicon Oxide, S11')
SiGr.plot(gd_SiGr, label='SiO2 w/Graphene, S11')
Copper.plot(gd_Cu, label='Copper,S11')
plt.ylabel('Group Delay (ns)')
plt.title('Group Delay, S11')
plt.legend()

# %%

# %%
