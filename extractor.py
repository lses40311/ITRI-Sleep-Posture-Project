'''
a class for feature extraction.
'''
import numpy as np
class Features:
    window_size = 50
    def __init__(self, set_window_size):
        self.window_size = set_window_size
        self.data_mat = np.zeros(shape=(set_window_size,3))
        self.x_array = np.zeros(set_window_size)
        self.y_array = np.zeros(set_window_size)
        self.z_array = np.zeros(set_window_size)
        self.cnt = 0
    def add_data(self,x,y,z):
        idx = self.cnt
        self.x_array[idx] = float(x)
        self.y_array[idx] = float(y)
        self.z_array[idx] = float(z)
        self.cnt += 1
        if self.cnt == self.window_size:
            self.cnt = 0
            return 1, np.mean(self.x_array), np.mean(self.y_array), np.mean(self.z_array)
        else:
            return 0, 0, 0, 0
