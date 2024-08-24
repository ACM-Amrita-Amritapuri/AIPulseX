import torch
from Network import NetworkModule
from Data import DataModule
from Training import TrainingModule
from Testing import TestingModule

def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    data_module = DataModule(batch_size=64, num_workers=4)
    network_module = NetworkModule(z_size=100, device=device)
    training_module = TrainingModule(network_module, data_module, device=device)
    testing_module = TestingModule(network_module, z_size=100, device=device)

    num_epochs = 10
    d_losses, g_losses = training_module.train(num_epochs=num_epochs)

    generated_images = testing_module.generate_images_for_digits(num_images=10)
    testing_module.display_generated_images(generated_images, n_cols=5, figsize=(15, 6))
    testing_module.save_generated_images(generated_images, filename='generated_images_digits.png')

if __name__ == "__main__":
    main()
