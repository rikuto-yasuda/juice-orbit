import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import time


object_name = "callisto" # "ganymede" or "callisto"

start_time = time.time()

if object_name == "ganymede":
    max_array = np.array(["0e2", "1e2", "2e2", "3e2", "4e2"])
    scale_array = np.array(["0.125e2", "0.5e2", "1e2", "3e2","9e2", "15e2"])

    raytracing_result_path = "/data1/rikutoyasuda/raytracing_ganymede_results"

    Freq_str = [
        "3.984813988208770752e5",
        "4.395893216133117676e5",
        "4.849380254745483398e5",
        "5.349649786949157715e5",
        "5.901528000831604004e5",
        "6.510338783264160156e5",
        "7.181954979896545410e5",
        "7.922856807708740234e5",
        "8.740190267562866211e5",
        "9.641842246055603027e5",
        "1.063650846481323242e6",
        "1.173378825187683105e6",
        "1.294426321983337402e6",
        "1.427961349487304688e6",
        "1.575271964073181152e6",
        "1.737779378890991211e6",
        "1.917051434516906738e6",
        "2.114817380905151367e6",
        "2.332985162734985352e6",
        "2.573659420013427734e6",
        "2.839162111282348633e6",
        "3.132054328918457031e6",
        "3.455161809921264648e6",
        "3.811601638793945312e6",
        "4.204812526702880859e6",
        "4.638587474822998047e6",
        "5.117111206054687500e6",
        "5.644999980926513672e6",
    ]

elif object_name == "callisto":
    raytracing_result_path = "/data1/rikutoyasuda/raytracing_callisto_results"
    max_array = np.array(["0e2", "1e2", "5e2", "10e2", "15e2", "20e2", "25e2", "29e2"])
    scale_array = np.array(["4e2", "6e2", "9e2"])

    Freq_str = [
        "3.612176179885864258e5",
        "3.984813988208770752e5",
        "4.395893216133117676e5",
        "4.849380254745483398e5",
        "5.349649786949157715e5",
        "5.901528000831604004e5",
        "6.510338783264160156e5",
        "7.181954979896545410e5",
        "7.922856807708740234e5",
        "8.740190267562866211e5",
        "9.641842246055603027e5",
        "1.063650846481323242e6",
        "1.173378825187683105e6",
        "1.294426321983337402e6",
        "1.427961349487304688e6",
        "1.575271964073181152e6",
        "1.737779378890991211e6",
        "1.917051434516906738e6",
        "2.114817380905151367e6",
        "2.332985162734985352e6",
        "2.573659420013427734e6",
        "2.839162111282348633e6",
        "3.132054328918457031e6",
        "3.455161809921264648e6",
        "3.811601638793945312e6",
        "4.204812526702880859e6",
        "4.638587474822998047e6",
        "5.117111206054687500e6",
        "5.644999980926513672e6",
    ]

Freq_num = []
for idx in Freq_str:
    Freq_num.append(float(idx) / 1000000)

def Detectable_range_calc(planet, max, scale):

    dir_path = raytracing_result_path + "/" + object_name + "_" + max + "_" + scale + "/"

    for freq in range(len(Freq_str)):
        pattern = f"ray-P{object_name}_nonplume_{max}_{scale}-Mtest_simple-benchmark-LO-Z*-FR{Freq_str[freq]}"
        matched_files = glob.glob(os.path.join(dir_path, pattern))
        detectable_outline_x = np.arange(-2000, 30000, 10)
        detectable_outline_z1 = np.ones(len(detectable_outline_x))*100000 # 掩蔽境界線のz座標（電波が見え始める高度）
        
        for path in matched_files:

            Radio_propagation_route  = np.loadtxt(path)

            if Radio_propagation_route.ndim == 2:
                ray_x_array = Radio_propagation_route[:, 1]
                ray_z_array = Radio_propagation_route[:, 3]


                for i in range(len(detectable_outline_x)):
                    x = detectable_outline_x[i]
                    index = np.where(ray_x_array >x)[0]
                    #print("x:"+str(x))
                    #print("index:"+str(index
                    #print("len:"+str(len(index)))

                    if len(index) >0:

                        index_first = index[0]

                        x0 = ray_x_array[index_first - 1]
                        x1 = ray_x_array[index_first]
                        z0 = ray_z_array[index_first - 1]
                        z1 = ray_z_array[index_first]

                        dericed_z = z0 + (z1 - z0) * (x - x0) / (x1 - x0)

                        if dericed_z < detectable_outline_z1[i]:
                            detectable_outline_z1[i] = dericed_z

    
        save_array =np.column_stack((detectable_outline_x, detectable_outline_z1))
        np.savetxt(dir_path + "Outlines_" + object_name + "_Nmax-" + max + "_scaleheight-" + scale + "_Freq-" + Freq_str[freq] + "Hz", save_array)

        



total_num = len(max_array) * len(scale_array)
current_num = 0
start_time = time.time()
observation_outline_x = np.arange(-2000, 18000, 10)
observation_outline_min = np.ones(len(observation_outline_x))*100000 # 掩蔽境界線のz座標の最低値
observation_outline_max = np.zeros(len(observation_outline_x)) # 掩蔽境界線のz座標の最高値
observation_outline_min_maxdens = np.zeros(len(observation_outline_x)) # 掩蔽境界線のz座標の最低値の最大密度
observation_outline_max_maxdens = np.zeros(len(observation_outline_x)) # 掩蔽境界線のz座標の最高値の最大密度
observation_outline_min_scaleheight = np.zeros(len(observation_outline_x)) # 掩蔽境界線のz座標の最低値のスケールハイト
observation_outline_max_scaleheight = np.zeros(len(observation_outline_x)) # 掩蔽境界線のz座標の最高値のスケールハイト
observation_outline_min_deg = np.zeros(len(observation_outline_x)) # 掩蔽境界線のz座標の最低値の傾き
observation_outline_max_deg = np.zeros(len(observation_outline_x)) # 掩蔽境界線のz座標の最高値の傾き
observation_outline_max_freq = np.zeros(len(observation_outline_x)) # 掩蔽境界線のz座標の最高値の時の周波数


plt.figure(figsize=(10, 6))   

for max_d in max_array:
    for scale_h in scale_array:
        time_elapsed = time.time() - start_time
        current_num += 1
        print(f"Processing: {object_name}, Max: {max_d}, Scale: {scale_h} ({current_num}/{total_num})")
        print(f"Time elapsed: {(time_elapsed/60):.2f} minutes")
        print(f"Estimated time remaining: {((time_elapsed/60) * (total_num - current_num)/(current_num if current_num > 0 else 1)):.2f} minutes")

        dir_path = raytracing_result_path + "/" + object_name + "_" + max_d + "_" + scale_h + "/"


        if os.path.isdir(dir_path):
            Detectable_range_calc(object_name, max_d, scale_h)
            

            for freq in range(len(Freq_str)):
                outline_path = dir_path + "Outlines_" + object_name + "_Nmax-" + max_d + "_scaleheight-" + scale_h + "_Freq-" + Freq_str[freq] + "Hz"
                if not os.path.isfile(outline_path):
                    continue
                

                outline_data = np.loadtxt(outline_path)
                z_line = outline_data[:, 1]
                z_line = np.where(z_line == 100000, np.nan, z_line) # 初期値のままの点をNaNに置換
                plt.plot(observation_outline_x, z_line[0:len(observation_outline_x)], color='black')

                for i in range(len(observation_outline_x)):
                    if not np.isnan(z_line[i]): # 初期値のままの点は無視
                        if z_line[i] < observation_outline_min[i]:
                            
                            observation_outline_min[i] = z_line[i]
                            observation_outline_min_deg[i] = np.degrees(np.arctan2(z_line[i], observation_outline_x[i]))
                            observation_outline_min_maxdens[i] = float(max_d)
                            observation_outline_min_scaleheight[i] = float(scale_h)
                            
                        if z_line[i] > observation_outline_max[i]:
                            observation_outline_max[i] = z_line[i]
                            observation_outline_max_deg[i] = np.degrees(np.arctan2(z_line[i], observation_outline_x[i]))
                            observation_outline_max_maxdens[i] = float(max_d)
                            observation_outline_max_scaleheight[i] = float(scale_h)
                            observation_outline_max_freq[i] = Freq_num[freq]

plt.plot(observation_outline_x, observation_outline_min, color='red', label='Minimum Detectable Range Outline')
plt.plot(observation_outline_x, observation_outline_max, color='blue', label='Maximum Detectable Range Outline')
plt.ylim(-1000, 10000)
plt.xlim(-2000, 18000)
plt.xlabel('Distance (km)')
plt.ylabel('Altitude (km)')
plt.title(f'Observation Range Outlines for {object_name}')
plt.legend()
plt.grid()

plt.savefig(raytracing_result_path + f"/Observation_Range_Outlines_{object_name}.png")
plt.close()

plt.figure(figsize=(10, 6))   
plt.plot(observation_outline_x, observation_outline_min_deg, color='red', label='Minimum Detectable Range Outline Slope')
plt.plot(observation_outline_x, observation_outline_max_deg, color='blue', label='Maximum Detectable Range Outline Slope')
plt.xlabel('Distance (km)')
plt.ylabel('Angle (degrees)')
plt.title(f'Observation Range Outline Angles for {object_name}')
plt.legend()
plt.grid()
plt.savefig(raytracing_result_path + f"/Observation_Range_Outlines_Angles_{object_name}.png")
plt.close()

save_array =np.column_stack((observation_outline_x, observation_outline_min, observation_outline_max, observation_outline_min_deg, observation_outline_max_deg, observation_outline_min_maxdens, observation_outline_max_maxdens, observation_outline_min_scaleheight, observation_outline_max_scaleheight, observation_outline_max_freq))
np.savetxt(raytracing_result_path + f"/Observation_Range_Outlines_{object_name}.txt", save_array)




            
