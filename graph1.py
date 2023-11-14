import matplotlib.pyplot as plt

bus_list = [['R11', 10161],
            ['R22', 13636],
            ['R10', 9892],
            ['R74', 11665],
            ['R55', 14102],
            ['R61', 16047],
            ['R81', 15034],
            ['R45', 15749],
            ['R88', 17431],
            ['R16', 15557],
            ['R747', 11811],
            ['R56', 16450],
            ['R12X', 15145],
            ['R172', 14808],
            ['R12', 12855],
            ['R102X', 13074],
            ['R42', 15167],
            ['R18', 14814],
            ['R43', 18828],
            ['R33', 15286],
            ['R303', 12232],
            ['R302', 13107],
            ['R41', 17922],
            ['R34', 17369],
            ['R49', 12817],
            ['R104', 14908],
            ['R101', 16899],
            ['R104A', 14463],
            ['R100', 15470],
            ['R94', 11931],
            ['R31', 18513],
            ['R20', 13958],
            ['R170', 15381],
            ['R129', 13026],
            ['R32', 13812],
            ['R40', 15462],
            ['R156', 12211],
            ['R777', 11735],
            ['R300', 11698],
            ['R137', 14339],
            ['R109', 13105],
            ['R119', 12244],
            ['136', 14928],
            ['R21', 14816],
            ['R102', 13294],
            ['R304', 14928],
            ['R301', 14160]]

line_list = []
dist_list = []
for x in bus_list:
    line_list.append(x[0])
    dist_list.append(x[1])

plt.bar(line_list, dist_list, width=0.3, color='b', label='distance travelled per day')
plt.xlabel('Bus lines')
plt.ylabel('Distance (km)')
plt.rcParams['font.family'] = 'Verdana'
plt.ylim(0,20000)
plt.grid(axis='y')
plt.yticks(range(0, 20001, 2000))
plt.legend(loc='upper right')
for a,b in zip(line_list,dist_list):
     plt.text(a,b,b,ha='center',va='bottom')

plt.show()