import numpy as np
import matplotlib.pyplot as plt

callisto_data = np.loadtxt("/data1/rikutoyasuda/raytracing_callisto_results/Observation_Range_Outlines_callisto.txt")
ganymede_data = np.loadtxt("/data1/rikutoyasuda/raytracing_ganymede_results/Observation_Range_Outlines_ganymede.txt")


ganymede_x = ganymede_data[:, 0]
ganymede_y_max = ganymede_data[:, 2]
ganymede_max_dens = ganymede_data[:, 6]
ganymede_max_scale = ganymede_data[:, 8]

print(ganymede_x)
print(ganymede_y_min)
print(ganymede_y_max)
print(ganymede_max_dens)
print(ganymede_max_scale)
plt.plot(ganymede_x, ganymede_max_dens, label='Ganymede Max Density', color='blue')
plt.show()

plt.plot(ganymede_x, ganymede_max_scale, label='Ganymede Max Scale', color='green')
plt.show()
# %%
callisto_x = callisto_data[:, 0]
callisto_y_max = callisto_data[:, 2]
callisto_max_dens = callisto_data[:, 6]
callisto_max_scale = callisto_data[:, 8]

print(callisto_x)python -m pip install --upgrade pip
print(callisto_y_min)
print(callisto_y_max)
print(callisto_max_dens)
print(callisto_max_scale)
plt.plot(callisto_x, callisto_max_dens, label='Callisto Max Density', color='orange')
plt.show()  
plt.plot(callisto_x, callisto_max_scale, label='Callisto Max Scale', color='red')
plt.show()