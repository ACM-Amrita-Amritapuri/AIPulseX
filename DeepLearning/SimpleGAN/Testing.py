import torch
import numpy as np
import matplotlib.pyplot as plt

class TestingModule:
    def __init__(self, network_module, z_size=100, device='cpu'):
        self.generator = network_module.get_generator().to(device)
        self.z_size = z_size
        self.device = device

    def generate_images_for_digits(self, num_images=10):
        self.generator.eval()
        with torch.no_grad():
            latent_vectors = torch.randn(num_images, self.z_size).to(self.device)
            generated_images = self.generator(latent_vectors).detach().cpu()
            generated_images = (generated_images + 1) / 2 
        return generated_images

    def display_generated_images(self, images, n_cols=5, n_rows=2, figsize=(15, 6)):
        plt.figure(figsize=figsize)
        for i in range(len(images)):
            plt.subplot(n_rows, n_cols, i + 1)
            plt.imshow(images[i].view(28, 28), cmap='gray')
            plt.axis('off')
            plt.title(f"Digit {i}", fontsize=10)
        plt.tight_layout()
        plt.show()

    def save_generated_images(self, images, filename='generated_images.png'):
        n_cols = 5
        n_rows = 2
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3, n_rows * 3))
        
        for i, ax in enumerate(axes.flat):
            if i < len(images):
                ax.imshow(images[i].view(28, 28), cmap='gray')
                ax.axis('off')
                ax.set_title(f"Digit {i}", fontsize=12)
            else:
                ax.axis('off')
        
        plt.subplots_adjust(wspace=0.2, hspace=0.2)
        plt.savefig(filename, bbox_inches='tight')
        plt.close(fig)
