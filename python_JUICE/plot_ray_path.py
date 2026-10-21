import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import time


object_name = "ganymede" # "ganymede" or "callisto"
Freq_str = "3.984813988208770752e5"
start_time = time.time()
existing_maxdens = []
existing_scaleheight = []


if object_name == "ganymede":
    max_array = np.array(["0e2", "1e2", "2e2", "3e2", "4e2"])
    scale_array = np.array(["0.125e2", "0.5e2", "1e2", "3e2","9e2", "15e2"])
    raytracing_result_path = "/data1/rikutoyasuda/raytracing_ganymede_results"


elif object_name == "callisto":
    raytracing_result_path = "/data1/rikutoyasuda/raytracing_callisto_results"
    max_array = np.array(["0e2", "1e2", "5e2", "10e2", "15e2", "20e2", "25e2", "29e2"])
    scale_array = np.array(["4e2", "6e2", "9e2"])

def Detectable_range_calc(object_name, Freq_str, max_dens, scale_height):

    dir_path = raytracing_result_path + "/" + object_name + "_" + max_dens + "_" + scale_height + "/"
    pattern = f"ray-P{object_name}_nonplume_{max_dens}_{scale_height}-Mtest_simple-benchmark-LO-Z*-FR{Freq_str}"
    leader_path = f"ray-P{object_name}_nonplume_{max_dens}_{scale_height}-Mtest_simple-benchmark-LO-Z54-FR{Freq_str}"



    if os.path.exists(dir_path + leader_path):
        existing_maxdens.append(max_dens)
        existing_scaleheight.append(scale_height)

        matched_files = glob.glob(os.path.join(dir_path, pattern))
        plt.figure(figsize=(10, 6))  
        l = len(matched_files)
        n = 0

        for path in matched_files:
            n+=1
            Radio_propagation_route  = np.loadtxt(path)

            if Radio_propagation_route.ndim == 2:
                ray_x_array = Radio_propagation_route[:, 1]
                ray_z_array = Radio_propagation_route[:, 3]
                plt.plot(ray_x_array, ray_z_array, color='gray', alpha=0.5)

        
        outline_path = dir_path + "Outlines_" + object_name + "_Nmax-" + max_dens + "_scaleheight-" + scale_height + "_Freq-" + Freq_str + "Hz"

        outline_txt = np.loadtxt(outline_path)
        outline_x = outline_txt[:, 0]
        outline_z = outline_txt[:, 1]

        plt.plot(outline_x, outline_z, color='red', label='Detectable Range Outline')
        plt.ylim(-1000, 10000)
        plt.xlim(-2000, 18000)

        plt.xlabel('Distance (km)')
        plt.ylabel('Altitude (km)')
        plt.title(f'Observation Range Outlines for {object_name}')
        plt.legend()
        plt.grid()

        plt.savefig(dir_path + f"/Observation_Range_Outlines_{object_name}.png")
        plt.close()


for max_d in max_array:
    for scale_h in scale_array:
        Detectable_range_calc(object_name, Freq_str, max_d, scale_h)
        print(f"Processed max_dens: {max_d}, scale_height: {scale_h}")



plt.figure(figsize=(10, 6)) 
plt.scatter(existing_maxdens, existing_scaleheight, color='blue', label='Existing Outlines')
plt.xlabel('Maximum Density (cm^-3)')
plt.ylabel('Scale Height (km)')
plt.title(f'Existing Outlines for {object_name}')
plt.legend()
plt.grid()
plt.savefig(raytracing_result_path + f"/Existing_Outlines_{object_name}.png")

            
