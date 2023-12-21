import matplotlib.pyplot as plt

X = [15000, 30000, 40000, 42500, 45000, 47500, 50000, 52500, 55000]

# T => Toroidal
y_T = [6.1, 16.5, 24.1, 26.2, 27.4, 28.4, 30.3, 30.5, 35.1]
weight_T = 25.7
# B => Big
y_B = [10.0, 23.2, 32.8, 34.0, 35.1, 37.6, 39.1, 42.5, 44.7]
weight_B = 23.9
# M => Medium
y_M = [6.9, 18.3, 26.6, 28.7, 31.7, 33.7, 36.8, 39.5, 41.5]
weight_M = 19.4
# S => Small
y_S = [6.6, 17.5, 26.6, 28.9, 31.1, 33.7, 35.6, 38.2, 40.3]
weight_S = 19.8

weight_250MAH = 8.1
weight_300MAH = 9.4

# Plotting the data
plt.figure(figsize=(10, 6))

plt.plot(X, y_T, label='Toroidal', marker='o')
plt.plot(X, y_B, label='Big', marker='o')
plt.plot(X, y_M, label='Medium', marker='o')
plt.plot(X, y_S, label='Small', marker='o')

# Adding dashed lines for the weight + weight of 250MAH battery
plt.axhline(y=weight_T + weight_250MAH, linestyle='--', color='blue', label='Toroidal Weight')
plt.axhline(y=weight_B + weight_250MAH, linestyle='--', color='orange', label='Big Weight')
plt.axhline(y=weight_M + weight_250MAH, linestyle='--', color='green', label='Medium Weight')
plt.axhline(y=weight_S + weight_250MAH, linestyle='--', color='red', label='Small Weight')

plt.xlabel('PWM')
plt.ylabel('Thrust (g)')
plt.title('Thrust vs PWM with Battery Weight')
plt.legend()
plt.grid(True)
plt.show()