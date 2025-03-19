import torch

def gaussian_loss(y_true, y_pred):
    mu, log_var = y_pred[:, 0], y_pred[:, 1]
    sigma = torch.exp(log_var) + 1e-6

    loss = 0.5 * torch.log(sigma) + 0.5 * torch.div(torch.pow(y_true - mu, 2), sigma)
    return torch.mean(loss)