import torchvision.transforms as transforms
from torchvision.datasets import MNIST, CIFAR10, FashionMNIST
from torch.utils.data import DataLoader
from torch.optim import lr_scheduler
import torch

from ContrastiveSampler import ContrastiveSampler
from BaseData import BaseData
from ContrastiveLoss import ContrastiveLoss
from networks import MNISTEmbeddingNet, CIFAREmbeddingNet, SiameseNet

from train import train
from metrics import mean_average_precision
import utils
from config import device

dataset = "FashionMNIST"
n_epochs = 30
data_path = utils.make_directory("../datasets/")
experiment_name = "32D"
batch_size = 32
num_workers = 4
lr = 1e-3
step_size = 8
margin = 1.0
embedding_dim=32

experiment_name = dataset + "_" + experiment_name
data_transforms = transforms.Compose([transforms.ToTensor()])

if dataset == "MNIST":
    embedding_net = MNISTEmbeddingNet()
    train_data = MNIST(root=data_path, train=True, transform=data_transforms)
    test_data = MNIST(root=data_path, train=False, transform=data_transforms)
if dataset == "FashionMNIST":
    embedding_net = MNISTEmbeddingNet()
    train_data = FashionMNIST(root=data_path, train=True, transform=data_transforms, download=True)
    test_data = FashionMNIST(root=data_path, train=False, transform=data_transforms, download=True)
elif dataset == "CIFAR10":
    embedding_net = CIFAREmbeddingNet(embedding_dim)
    train_data = CIFAR10(root=data_path, train=True, transform=data_transforms)
    test_data = CIFAR10(root=data_path, train=False, transform=data_transforms)

sampler = ContrastiveSampler(train_data)
train_dataset = BaseData(train_data, sampler)
test_dataset = BaseData(test_data, sampler)

train_dataloader = DataLoader(
    train_dataset, batch_size=batch_size, num_workers=num_workers)
test_dataloader = DataLoader(
    test_dataset, batch_size=batch_size, num_workers=num_workers)


model = SiameseNet(embedding_net).to(device)

criterion = ContrastiveLoss(margin=margin)
optimizer = torch.optim.Adam(model.parameters(), lr=lr)
scheduler = lr_scheduler.StepLR(optimizer, step_size=step_size)



train(model, criterion, train_dataloader, test_dataloader, optimizer, scheduler, experiment_name, n_epochs=n_epochs)
# model = utils.load_model(model, experiment_name)

# mAP = mean_average_precision(model, test_dataloader, train_dataloader,k=100)
# print(mAP)


# embeddings_matrix, targets_vector = utils.get_dataset_embeddings(
#     model, train_dataloader)
# train_dataset.plot_ND_embeddings(embeddings_matrix, targets_vector)
