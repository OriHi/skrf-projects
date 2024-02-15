#%%
import numpy as np
import os
from matplotlib import pyplot as plt
import skrf as rf
import imageio.v2 as imageio
import math
import cmath

# %%
#define variables

dataset_dir = "/home/ori/Documents/Work/NanoVNA/testprobe/smaract/Graphene_test/"

open = rf.Network('/home/ori/Documents/Work/NanoVNA/testprobe/smaract/Graphene_test/open.s1p')
open_dc = open.extrapolate_to_dc(kind='linear')
open_dcgate = open_dc.time_gate(center=5, span=7, t_unit='ns')

#for mobility
eps_s = 9.3203
#eps_ox = 3.4 #hBN
#eps_s = 6.9 #gold
eps_ox = 3.9
T_k = 300 #Kelvin
t_ox = 300e-6 #micrometer
k_b = 1.380649e-23 #Joule/Kelvin
t_gr = 0.345e-9 #nanometer
#t_gold = 70e-9 #nanometer
#t_hBN = 60e-9 #nanometer
#t_gr = 0.65e-9 #nanometer
q_c = 1.60217663e-19 #Coulombs/elementary charge
r_tip = 0.5e-6 #nanometer/tip radius

#for frequency 
im = 1j
z0 = 50
start_freq = 100e6
end_freq = 3000e6
step_freq = 10e6
duration_per_frame = 0.2
freqs = np.arange(start_freq, end_freq + step_freq, step_freq)# %%

#%%
#define functions
def extrapolate_dc(a):
    ntdc = a.extrapolate_to_dc(kind='linear')
    ntdc_gate = ntdc.time_gate(center=10, span=7, t_unit='ns')
    return ntdc_gate
    
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
#run
frames = []
frames_z = []
frames_c = []
for target_freq in freqs:
    rows = []
    cols = []
    capac_values = []
    capac_values_i = []
    z_im_values = []
    z_time_values = []
    s_mag_values = []
    mob_values = []
    for col in range(1,6):
        for row in range(1,6):
            filename = f"{row}-{col}.s1p"
            file_path = os.path.join(dataset_dir, filename)
            if os.path.exists(file_path):
                ntwk = rf.Network(file_path)
                ntwk_dcgate = extrapolate_dc(ntwk)
                deembed = (ntwk_dcgate / open_dcgate)
                t, z_data = step_res(deembed)
                idx = np.argmin(np.abs(deembed.frequency.f - target_freq))
                mag_data = deembed.s_re[idx,0,0]+(im*deembed.s_im[idx,0,0])
                f_data=deembed.f[idx]
                z_im_data = (deembed.z_im[idx,0,0])*((1+mag_data)/(1-mag_data))
                idx_z = np.argmax(z_data)
                z_time_data = z_data[idx_z]
                capac_data = solve_capac(f_data,z_time_data)
                capac_data_i = solve_capac_i(mag_data,z_im_data)
                capac_data_real = capac_data_i.real
                capac_data_real = capac_data_real.astype('float64')
                mob_data = solve_mobility(abs(capac_data_i.real))
                cols.append(col)
                rows.append(row)
                z_im_values.append(z_im_data)
                z_time_values.append(z_time_data)
                s_mag_values.append(mag_data)
                capac_values.append(capac_data)
                capac_values_i.append(capac_data_real)
                mob_values.append(mob_data)
            else:
                print(f"{filename} missing")
            
    min_capac_i = min(capac_values_i)
    max_capac_i = max(capac_values_i)
        
    plt.figure(figsize=(8, 8))
    plt.hist2d(cols, rows, weights=capac_values_i, bins=(np.arange(0.5, 6.5), np.arange(0.5, 6.5)),
                cmap='viridis', vmin=min_capac_i, vmax=max_capac_i)
    plt.colorbar(label='Capacitance (F)')
    plt.xlabel('Column')
    plt.ylabel('Row')
    plt.title(f'2D Histogram of Capacitance at {target_freq/1e9:.2f} GHz')
    plt.xticks(np.arange(1, 6))
    plt.yticks(np.arange(1, 6))
    plt.gca().invert_yaxis()
    plt.savefig(f'/home/ori/Documents/Work/NanoVNA/Mapping/data_dump/Capacitance/frame_{int(target_freq/1e6)}.png')
    frames.append(imageio.imread(f'/home/ori/Documents/Work/NanoVNA/Mapping/data_dump/Capacitance/frame_{int(target_freq/1e6)}.png'))
    plt.close()
        
    imageio.mimsave('/home/ori/Documents/Work/NanoVNA/Mapping/data_dump/Capacitance/2D_Cap_histogram.gif', frames, duration=duration_per_frame)
    
    min_capac = min(capac_values)
    max_capac = max(capac_values)
        
    plt.figure(figsize=(8, 8))
    plt.hist2d(cols, rows, weights=capac_values, bins=(np.arange(0.5, 6.5), np.arange(0.5, 6.5)),
                cmap='viridis', vmin=min_capac, vmax=max_capac)
    plt.colorbar(label='Capacitance (F)')
    plt.xlabel('Column')
    plt.ylabel('Row')
    plt.title(f'2D Histogram of Capacitance at {target_freq/1e9:.2f} GHz')
    plt.xticks(np.arange(1, 6))
    plt.yticks(np.arange(1, 6))
    plt.gca().invert_yaxis()
    plt.savefig(f'/home/ori/Documents/Work/NanoVNA/Mapping/data_dump/Capacitance_v2/frame_{int(target_freq/1e6)}.png')
    frames_c.append(imageio.imread(f'/home/ori/Documents/Work/NanoVNA/Mapping/data_dump/Capacitance_v2/frame_{int(target_freq/1e6)}.png'))
    plt.close()
        
    imageio.mimsave('/home/ori/Documents/Work/NanoVNA/Mapping/data_dump/Capacitance_v2/2D_Cap_histogram.gif', frames_c, duration=duration_per_frame)
# %%
