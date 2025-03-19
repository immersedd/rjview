import numpy as np
import math
import torch


class LogMADScaler(object):
    def __init__(self):
        self.median = None
        self.mad = None

    def fit(self, lis):
        arr = np.array(lis)
        arr = np.log(arr + 1)
        self.median = np.median(arr)
        self.mad = np.median(np.abs(arr - self.median))

    def transform(self, num):
        x = num
        x = (math.log(x + 1) - self.median) / (self.mad if self.mad != 0 else 1)
        return x

    def detransform(self, num):
        x = num
        x = math.exp(x * (self.mad if self.mad != 0 else 1) + self.median) - 1
        return x


class LogStandardScaler(object):
    def __init__(self):
        self.mean = None
        self.std = None

    def fit(self, lis):
        arr = np.log(lis)
        self.mean = np.mean(arr)
        self.std = np.std(arr)

    def transform(self, num):
        if isinstance(num, (np.ndarray, torch.Tensor)):
            if isinstance(num, torch.Tensor):
                num = num.detach().cpu().numpy()
            return (np.log(num) - self.mean) / self.std
        else:
            return (math.log(num) - self.mean) / self.std

    def detransform(self, num):
        if isinstance(num, (np.ndarray, torch.Tensor)):
            if isinstance(num, torch.Tensor):
                num = num.detach().cpu().numpy()
            return np.exp(num * self.std + self.mean)
        else:
            return math.exp(num * self.std + self.mean)
