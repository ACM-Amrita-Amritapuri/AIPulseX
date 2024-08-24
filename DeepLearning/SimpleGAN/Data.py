# data_module.py
import os
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

class DataModule:
    def __init__(self, batch_size=64, num_workers=4):
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.transform = transforms.Compose([transforms.ToTensor()])
        self.train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=self.transform)
        self.test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=self.transform)

    def get_train_loader(self):
        return DataLoader(dataset=self.train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=self.num_workers)

    def get_test_loader(self):
        return DataLoader(dataset=self.test_dataset, batch_size=self.batch_size, shuffle=False, num_workers=self.num_workers)
