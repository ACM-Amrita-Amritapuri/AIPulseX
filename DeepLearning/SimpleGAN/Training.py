# training_module.py
import torch
from Network import NetworkModule

class TrainingModule:
    def __init__(self, network_module, data_module, device='cpu'):
        self.device = device
        self.network_module = network_module
        self.data_module = data_module
        self.train_loader = data_module.get_train_loader()
        self.z_size = network_module.z_size

    def real_loss(self, predicted_logits):
        batch_size = predicted_logits.size(0)
        targets = torch.ones(batch_size, 1).to(self.device)
        return self.network_module.get_loss_fn()(predicted_logits, targets)

    def fake_loss(self, predicted_logits):
        batch_size = predicted_logits.size(0)
        targets = torch.zeros(batch_size, 1).to(self.device)
        return self.network_module.get_loss_fn()(predicted_logits, targets)

    def train(self, num_epochs):
        d_losses, g_losses = [], []

        for epoch in range(num_epochs):
            self.network_module.get_discriminator().train()
            self.network_module.get_generator().train()

            d_running_loss, g_running_loss = 0.0, 0.0

            for real_images, _ in self.train_loader:
                real_images = real_images.view(real_images.size(0), -1).to(self.device)
                real_images = (real_images * 2) - 1 

                self.network_module.get_d_optimizer().zero_grad()
                real_logits = self.network_module.get_discriminator()(real_images)
                d_real_loss = self.real_loss(real_logits)

                z = torch.randn(real_images.size(0), self.z_size).to(self.device)
                fake_images = self.network_module.get_generator()(z)
                fake_logits = self.network_module.get_discriminator()(fake_images.detach())
                d_fake_loss = self.fake_loss(fake_logits)

                d_loss = d_real_loss + d_fake_loss
                d_loss.backward()
                self.network_module.get_d_optimizer().step()
                d_running_loss += d_loss.item()

                self.network_module.get_g_optimizer().zero_grad()
                fake_logits = self.network_module.get_discriminator()(fake_images)
                g_loss = self.real_loss(fake_logits)
                g_loss.backward()
                self.network_module.get_g_optimizer().step()
                g_running_loss += g_loss.item()

            d_losses.append(d_running_loss / len(self.train_loader))
            g_losses.append(g_running_loss / len(self.train_loader))

            print(f"Epoch [{epoch+1}/{num_epochs}] - Discriminator Loss: {d_losses[-1]:.4f}, Generator Loss: {g_losses[-1]:.4f}")

        return d_losses, g_losses
