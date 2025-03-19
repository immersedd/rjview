
import torch
import torch.nn as nn
from binary_tree_conv import BinaryTreeConv, TreeLayerNorm, TreeActivation, DynamicPooling



device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_left_child(node):
    return node[1] if len(node) == 3 else None


def get_right_child(node):
    return node[2] if len(node) == 3 else None


def extract_features(node):
    return node[0]


class TreeCNN(nn.Module):
    def __init__(self, input_channels, num_inputs=1):
        super(TreeCNN, self).__init__()

        self.input_channels = input_channels
        self.use_cuda = True
        self.num_inputs = num_inputs

        self.tree_convolution = nn.Sequential(
            BinaryTreeConv(self.input_channels, 256),
            TreeLayerNorm(),
            TreeActivation(nn.LeakyReLU()),
            BinaryTreeConv(256, 128),
            TreeLayerNorm(),
            TreeActivation(nn.LeakyReLU()),
            BinaryTreeConv(128, 64),
            TreeLayerNorm(),
            DynamicPooling()
        )

        self.self_attention = SelfAttention(hidden_size=64, attention_size=64)
        self.mlp = MLP(input_dim=64 * 3, hidden_dims=[128, 64, 32], output_dim=1)

    def forward(self, *inputs):
        if len(inputs) != self.num_inputs:
            raise ValueError(f"Expected {self.num_inputs} inputs, but got {len(inputs)}")

        embeddings = [
            self.tree_convolution(
                prepare_trees(x, extract_features, get_left_child, get_right_child, cuda=self.use_cuda)
            )
            for x in inputs
        ]

        dif = embeddings[0] - embeddings[1]
        combined_embedding = torch.cat((embeddings[0], embeddings[1], dif), dim=-1)
        return self.mlp(combined_embedding)

    def enable_cuda(self):
        self.use_cuda = True
        return super().cuda()
