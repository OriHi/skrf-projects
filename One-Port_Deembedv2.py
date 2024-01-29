#%%
import numpy as np
from matplotlib import pyplot as plt
import skrf as rf
import math

#%%
#read data
ntwk1 = rf.Network('/home/ori/Documents/Work/NanoVNA/testprobe/MoS2/1-1.s1p')
ntwk2 = rf.Network('/home/ori/Documents/Work/NanoVNA/testprobe/MoS2/1-5.s1p')
ntwk3 = rf.Network('/home/ori/Documents/Work/NanoVNA/testprobe/MoS2/1-10.s1p')
ntwk4 = rf.Network('/home/ori/Documents/Work/NanoVNA/testprobe/MoS2/1-20.s1p')
ntwk5 = rf.Network('/home/ori/Documents/Work/NanoVNA/testprobe/smaract/Graphene_test/1-1.s1p')
o = rf.Network('/home/ori/Documents/Work/NanoVNA/testprobe/smaract/Graphene_test/open.s1p')
#new_freq = rf.Frequency(100,4000,156,'mhz')
#open = o.interpolate(new_freq, kind = 'cubic')
#%%
#convert to dc 
ntwk1_dc = ntwk1.extrapolate_to_dc(kind='linear')
ntwk2_dc = ntwk2.extrapolate_to_dc(kind='linear')
ntwk3_dc = ntwk3.extrapolate_to_dc(kind='linear')
ntwk4_dc = ntwk4.extrapolate_to_dc(kind='linear')
ntwk5_dc = ntwk5.extrapolate_to_dc(kind='linear')

open_dc = o.extrapolate_to_dc(kind='linear')
ntwk_not = ntwk5_dc
ntwk_working = ntwk5
#new_freqi = rf.Frequency(0,4000,160,'mhz')
#open_dc = open_idc.interpolate(new_freqi, kind = 'linear')
#%%
#test plot for D
fig = plt.figure(figsize=(9,8))
plt.subplot(2,2,1)
plt.title('Time')
ntwk_not.s11.plot_z_time_step(window='hamming', label='center')
#plt.xlim((-10,10))

ax = plt.subplot(2,2,2)
plt.title('Frequency')
ntwk_not.s11.plot_s_db(label='center')

ax = plt.subplot(2,2,3)
ntwk_dcgate = ntwk_not.time_gate(center=2.5, span=1.9, t_unit='ns')
ntwk_dcgate.plot_s_db_time(label='center, gated')
ntwk_not.s11.plot_s_db_time(label='center')
plt.title('Time-Gated')

ax = plt.subplot(2,2,4)
ntwk_dcgate.plot_s_db(label='center, gated')
ntwk_not.plot_s_db(label='center')
plt.title('Frequency, Time-Gated')
plt.tight_layout()
plt.show()
# %%
#test plot for K
fig = plt.figure(figsize=(9,8))
plt.subplot(2,2,1)
plt.title('Time')
open_dc.s11.plot_z_time_step(window='hamming', label='open')
plt.xlim((0,60))

ax = plt.subplot(2,2,2)
plt.title('Frequency')
open_dc.s11.plot_s_db(label='open')
plt.ylim(-45,5)

ax = plt.subplot(2,2,3)
open_dcgate = open_dc.time_gate(center=2.5, span=1.9, t_unit='ns')
open_dcgate.plot_s_db_time(label='open, gated')
open_dc.s11.plot_s_db_time(label='open')
plt.title('Time-Gated')

ax = plt.subplot(2,2,4)
open_dcgate.plot_s_db(label='open, gated')
open_dc.plot_s_db(label='open')
plt.title('Frequency, Time-Gated')
plt.tight_layout()
plt.show()
# %%
#plot for corrected S11

deembed = (ntwk_dcgate / open_dcgate)

fig=plt.figure(figsize=(9,8))
plt.subplot(2,2,1)
ntwk_working['0.1-1Ghz'].plot_s_smith(draw_labels=True,show_legend=False,draw_vswr=True,label='1-1')
deembed['0.1-1Ghz'].plot_s_smith(draw_labels=True,show_legend=False,draw_vswr=True,label='Deembed 1-1')
plt.title("1-3.5 GHz")

ax=plt.subplot(2,2,2)
#ntwk_working['0-1Ghz'].s11.plot_z_time_step(window='hamming', label='1-1')
deembed['0-1Ghz'].plot_z_time_step(window='hamming', label='deembed 1-1')
#plt.xlim[(-10,10)]
plt.title("Z-load")
ax.grid()

ax=plt.subplot(2,1,2)
ntwk_working['0.1-6Ghz'].plot_s_db(label='Graphene')
deembed['0.1-6Ghz'].plot_s_db(label='deembed Graphene')
#plt.ylabel('S11(dB)')
ax.grid()

# %%
fig=plt.figure(figsize=(9,8))
ntwk1.s11.plot_z_re(label='1')
ntwk2.s11.plot_z_re(label='2')
ntwk3.s11.plot_z_re(label='3')
ntwk4.s11.plot_z_re(label='4')
#ntwk5.s11.plot_s_db(label='center')
#o.s11.plot_s_db(label='open')
plt.title("Resistance (Ohms)")
#%%
fig=plt.figure(figsize=(9,8))
ntwk1.s11.plot_s_db(label='1')
ntwk2.s11.plot_s_db(label='2')
ntwk3.s11.plot_s_db(label='3')
ntwk4.s11.plot_s_db(label='4')
#ntwk5.s11.plot_s_db(label='center')
o.s11.plot_s_db(label='open')
plt.title("")
# %%
#define
#for mobility
eps_s = 9.3203
eps_ox = 3.9
T_k = 300 #Kelvin
t_ox = 300e-6 #micrometer
k_b = 1.380649e-23 #Joule/Kelvin
#t_gr = 0.345e-9 #nanometer
#t_gr = 0.65e-9 #nanometer
t_gr = 50e-9 #nanometer
q_c = 1.60217663e-19 #Coulombs/elementary charge
r_tip = 0.5e-6 #nanometer/tip radius

#for frequency 
im = 1j
z0 = 50
start_freq = 1000e6
end_freq = 3500e6
step_freq = 10e6

def step_res(b):
    t, ymea =  b.s11.step_response(window='hamming', pad=0)
    ymea[ymea ==  1.] =  1. + 1e-12  # solve numerical singularity
    ymea[ymea == -1.] = -1. + 1e-12  # solve numerical singularity
    ymea = z0 * (1+ymea) / (1-ymea)
    return t, ymea
    
def solve_capac_i(l, m):
    if (l or m) == 0:
        return "Infinite solutions (0x = 0)"
    else:
        #o = (1/(2*np.pi*l*m))*1e12
        o = ((1-l)/(im*2*np.pi*m*(1+l)))
        return o
        
def solve_capac(l, m):
    if (l or m) == 0:
        return "Infinite solutions (0x = 0)"
    else:
        o = (1/(2*np.pi*l*m))
        return o        
    
def solve_mobility(f):
    if f == 0:
        return "Infinite solutions (0x = 0)"
    else:
        exp_1 = (eps_s*(q_c)**2)/(k_b*T_k*(eps_ox)**2)
        exp_2 = ((eps_ox*np.pi*r_tip**2)-(f*t_ox))/f
        exp_3 = exp_2*math.sqrt(exp_1)    
        exp_4 = (exp_3)**-2
        g = exp_4*(t_gr)*(1/10000) #convert m3 t0 m2 #convert to cm-2
        return g
#%%


t, z_data = step_res(deembed)
idx = np.argmin(np.abs(deembed.frequency.f))
mag_data = deembed.s_re[idx,0,0]+(im*deembed.s_im[idx,0,0])
f_data=deembed.f[idx]
z_im_data = (deembed.z_im[idx,0,0])*((1+mag_data)/(1-mag_data))
idx_z = np.argmax(z_data)
z_time_data = z_data[idx_z]
capac_data = solve_capac(f_data,z_time_data)
capac_data_i = solve_capac_i(mag_data,z_im_data)
mob_data = solve_mobility(abs(capac_data_i.real))
#%%
print(capac_data)
print(capac_data_i)
print(mob_data)
# %%
