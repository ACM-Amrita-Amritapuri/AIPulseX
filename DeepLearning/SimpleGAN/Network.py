# network_module.py
import torch
import torch.nn as nn
import torch.optim as optim

class Discriminator(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(Discriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(32, output_dim)
        )

    def forward(self, x):
        return self.model(x)

class Generator(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(Generator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(32, 64),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(64, 128),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(128, output_dim),
            nn.Tanh()
        )

    def forward(self, x):
        return self.model(x)

class NetworkModule:
    def __init__(self, z_size=100, device='cpu'):
        self.device = device
        self.z_size = z_size
        self.discriminator = Discriminator(input_dim=784, output_dim=1).to(self.device)
        self.generator = Generator(input_dim=self.z_size, output_dim=784).to(self.device)
        self.d_optimizer = optim.Adam(self.discriminator.parameters(), lr=0.002)
        self.g_optimizer = optim.Adam(self.generator.parameters(), lr=0.002)
        self.loss_fn = nn.BCEWithLogitsLoss()

    def get_discriminator(self):
        return self.discriminator

    def get_generator(self):
        return self.generator

    def get_d_optimizer(self):
        return self.d_optimizer

    def get_g_optimizer(self):
        return self.g_optimizer

    def get_loss_fn(self):
        return self.loss_fn
