import matplotlib.pyplot as plt

fuel_list = [3613485286]#, 16375310, 4366749]
electricity_list = [110322421]#, 269079, 53816]
x = ['CO2 emission']#, 'Hg emission', 'Cd emission']

plt.bar(x, fuel_list, color='b', width=-0.4, align='edge', label='fuel')
plt.bar(x, electricity_list, color='r', width=0.4, align='edge', label='electricity')
plt.rcParams['font.family'] = 'Verdana'
plt.grid(axis='y')
for a, b in zip(x, fuel_list):
    plt.text(a, b, b, ha='right', va='bottom')
for a, b in zip(x, electricity_list):
    plt.text(a, b, b, ha='left', va='bottom')
plt.legend(loc='upper right')
plt.show()
