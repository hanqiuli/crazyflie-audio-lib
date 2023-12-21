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

# Function to calculate intersection point
def find_intersection(X, Y, weight, battery_weight):
    for i in range(len(X)):
        if Y[i] >= weight + battery_weight:
            return X[i], Y[i]

# Calculate intersection points
intersection_T = find_intersection(X, y_T, weight_T, weight_250MAH)
intersection_B = find_intersection(X, y_B, weight_B, weight_250MAH)
intersection_M = find_intersection(X, y_M, weight_M, weight_250MAH)
intersection_S = find_intersection(X, y_S, weight_S, weight_250MAH)

# Plotting the data
plt.figure(figsize=(10, 6))

plt.plot(X, y_T, label='Toroidal', marker='o')
plt.plot(X, y_B, label='Big', marker='o')
plt.plot(X, y_M, label='Medium', marker='o')
plt.plot(X, y_S, label='Small', marker='o')

# Marking intersection points on the graph
plt.scatter(*intersection_T, color='blue', marker='x', label='Toroidal Intersection')
plt.scatter(*intersection_B, color='orange', marker='x', label='Big Intersection')
plt.scatter(*intersection_M, color='green', marker='x', label='Medium Intersection')
plt.scatter(*intersection_S, color='red', marker='x', label='Small Intersection')

# Adding dashed lines from intersection points to x-axis
plt.plot([intersection_T[0], intersection_T[0]], [0, intersection_T[1]], linestyle='--', color='blue')
plt.plot([intersection_B[0], intersection_B[0]], [0, intersection_B[1]], linestyle='--', color='orange')
plt.plot([intersection_M[0], intersection_M[0]], [0, intersection_M[1]], linestyle='--', color='green')
plt.plot([intersection_S[0], intersection_S[0]], [0, intersection_S[1]], linestyle='--', color='red')

plt.xlabel('PWM')
plt.ylabel('Thrust (g)')
plt.title('Thrust vs PWM with Battery Weight')
plt.legend()
plt.grid(True)
plt.show()
