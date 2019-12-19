from torchvision.datasets import MNIST, CIFAR10
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np

from ContrastiveSampler import ContrastiveSampler
from utils import make_directory


data_path = make_directory("../datasets/")


class BaseData(Dataset):
    def __init__(self, data, sampler):
        self.is_train = data.train
        self.sampler = sampler
        self.data = data
        self.data_length = len(data)
        self.n_groundtruths = self.groundtruths_per_class()

    def groundtruths_per_class(self):
        n_groundtruths = dict()
        for class_id, class_idxs in self.sampler.class_idxs.items():
            n_groundtruths[class_id] = len(class_idxs)
        return n_groundtruths

    def __getitem__(self, idx):
        data_items = dict()
        anchor, anchor_target = self.data[idx]
        data_items["anchor"] = anchor
        data_items["anchor_target"] = anchor_target
        if self.is_train:
            duplet_id, is_pos = self.sampler.sample_data(idx, anchor_target)
            duplet, _ = self.data[duplet_id]
            data_items["duplet"] = duplet
            data_items["is_pos"] = is_pos

        return data_items

    def __len__(self):
        return self.data_length

    def show_image(self, idx):
        im = self.data.data[idx]
        trans = transforms.ToPILImage()
        im = trans(im)
        im.show()

    def plot_2D_embeddings(self, embeddings, targets, colors, classes, xlim=None, ylim=None):
        plt.figure(figsize=(10, 10))
        for i in range(10):
            inds = np.where(targets == i)[0]
            plt.scatter(embeddings[inds, 0], embeddings[inds,
                                                        1], alpha=0.5, color=colors[i])
        if xlim:
            plt.xlim(xlim[0], xlim[1])
        if ylim:
            plt.ylim(ylim[0], ylim[1])
        plt.legend(classes)
        plt.show()


if __name__ == "__main__":
    from networks import CIFAREmbeddingNet

    net = CIFAREmbeddingNet()

    data_transforms = transforms.Compose([transforms.ToTensor()])
    train_data = CIFAR10(root=data_path, train=True, transform=data_transforms)
    sampler = ContrastiveSampler(train_data)
    train_dataset = BaseData(train_data, sampler)
    
    dataloader = DataLoader(train_dataset, batch_size=4)
    # for data_items in dataloader:
        # print(data_items["anchor"].size())
        # out = net(data_items["anchor"])
        # print(out.size())
        # print(data_items["duplet"].size())
        # print(data_items["is_pos"].size())
        # print(data_items["anchor_target"].size())
        # break
