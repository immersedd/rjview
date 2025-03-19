import numpy as np
import math
import torch


def mape(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true))*100

def smape(y_true, y_pred):
    return 100/len(y_true) * np.sum(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred)))