import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

def minimax_time_plot():
    x = np.arange(1, 7)
    y = np.random.rand(6, 6)  
    max_val = 300

    c0 = [0, 3.3, 84, max_val, max_val, max_val]
    c1 = [0, 1, 32, 120, max_val, max_val]
    c2 = [0, 0.3, 4, 20, 180, max_val]
    c3 = [0, 0.25, 2.25, 8.2, 35, max_val]
    c4 = [0, 0.15, 0.8, 4, 20, 169]
    c5 = [0, 0.05, 0.12, 5, 6, 19]

    legend_points = [(2, 3.3), (3, 32), (4, 20), (5, 35), (5, 20), (6, 19)]

    for point, label in zip(legend_points, ['C0', 'C1', 'C2', 'C3', 'C4', 'C5']):
        plt.scatter(*point, marker='o', color='black')
        plt.text(point[0] + 0.1, point[1], label, verticalalignment='center')

    plt.plot(x, c0, label='Normal')
    plt.plot(x, c1, label='Sorted')
    plt.plot(x, c2, label='Sorted // 2')
    plt.plot(x, c3, label='Sorted // 3')
    plt.plot(x, c4, label='Sorted // 4')
    plt.plot(x, c5, label='Sorted // 6')

    plt.ylim(0, 100)
    plt.xlim(1, 6)

    plt.legend()

    plt.xlabel('Depth')
    plt.ylabel('Time (s)')

    plt.grid(True)
    plt.savefig('minimax_time_plot.png')
    plt.show()

def MCTS_time_plot():
    x = [0, 3, 5, 7]
    y = [0, 15, 32, 62]
    
    plt.plot(x, y)
    for x, y in zip(x, y):
        plt.scatter(x, y, marker='o', color='black')
        plt.text(x + 0.1, y, f'{y}', verticalalignment='center')
    plt.xlabel('Nombre de simulations')
    plt.ylabel('Temps (s)')
    plt.grid(True)
    plt.savefig('MCTS_time_plot.png')
    plt.show()

minimax_time_plot()


