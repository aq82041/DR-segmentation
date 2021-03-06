import numpy as np
from torchvision import datasets, models, transforms
import torchvision
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import cv2

class IDRIDDataset(Dataset):

    def __init__(self, image_paths, mask_paths=None, class_number=0, transform=None):
        """
        Args:
            image_paths: paths to the original images []
            mask_paths: paths to the mask images, [[]]
        """
        assert len(image_paths) == len(mask_paths)
        self.image_paths = image_paths
        if mask_paths is not None:
            self.mask_paths = mask_paths
        self.class_number = class_number
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def pil_loader(self, image_path):
        with open(image_path, 'rb') as f:
            img = Image.open(f)
            return img.convert('RGB')

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        mask_path4 = self.mask_paths[idx]
        item = self.pil_loader(image_path)
        info = [item]
        w, h = item.size
        if self.mask_paths is not None:
            for i, mask_path in enumerate(mask_path4):
                if mask_path is None:
                    info.append(Image.fromarray(np.zeros((h, w, 3), dtype=np.uint8)))
                else:
                    info.append(self.pil_loader(mask_path))
        if self.transform:
            info = self.transform(info)
        inputs = np.array(info[0])
        if inputs.shape[2] == 3:
            inputs = np.transpose(np.array(info[0]), (2, 0, 1))
            inputs = inputs / 255.
        
        if len(info) > 1:
            masks = np.array([np.array(maskimg)[:, :, 0] for maskimg in info[1:]])/255.0
            masks_sum = np.sum(masks, axis=0)
            empty_mask = 1 - masks_sum
            masks = np.concatenate((empty_mask[None, :, :], masks), axis=0)
            return inputs, masks
        else:
            return inputs

class DiaretDataset(Dataset):

    def __init__(self, image_paths, class_number=0, transform=None):
        """
        Args:
            image_paths: paths to the original images []
        """
        self.image_paths = image_paths
        self.class_number = class_number
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def pil_loader(self, image_path):
        with open(image_path, 'rb') as f:
            img = Image.open(f)
            return img.convert('RGB')

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        item = self.pil_loader(image_path)
        info = [item]
        w, h = item.size
        if self.transform:
            info = self.transform(info)
        inputs = np.array(info[0])
        if inputs.shape[2] == 3:
            inputs = np.transpose(np.array(info[0]), (2, 0, 1))
            inputs = inputs / 255.
        
        return inputs

class DiaretALDataset(Dataset):
    def __init__(self, image_paths, mask_paths=None, class_number=0, transform=None):
        """
        Args:
            image_paths: paths to the original images []
            mask_paths: paths to the mask images, [[]]
        """
        assert len(image_paths) == len(mask_paths)
        self.image_paths = image_paths
        if mask_paths is not None:
            self.mask_paths = mask_paths
        self.class_number = class_number
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def pil_loader(self, image_path):
        with open(image_path, 'rb') as f:
            img = Image.open(f)
            return img.convert('RGB')

    def cv2_loader(self, image_path):
        return cv2.imread(image_path)
    
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        mask_path4 = self.mask_paths[idx]
        item = self.pil_loader(image_path)
        info = [item]
        w, h = item.size
        if self.mask_paths is not None:
            for i, mask_path in enumerate(mask_path4):
                if mask_path is None:
                    info.append(Image.fromarray(np.zeros((h, w, 3), dtype=np.uint8)))
                else:
                    maskimg = self.cv2_loader(mask_path)
                    info.append(Image.fromarray(maskimg))
        if self.transform:
            info = self.transform(info)
        inputs = np.array(info[0])
        if inputs.shape[2] == 3:
            inputs = np.transpose(np.array(info[0]), (2, 0, 1))
            inputs = inputs / 255.

        if len(info) > 1:
            masks = np.array([np.array(maskimg)[:, :, 0] for maskimg in info[1:]]) / 255.
            masks_sum = np.sum(masks, axis=0)
            empty_mask = 1 - masks_sum
            masks = np.concatenate((empty_mask[None, :, :], masks), axis=0)
            return inputs, masks
        else:
            return inputs
