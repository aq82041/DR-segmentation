import sys
import os
from optparse import OptionParser
import numpy as np

import torch
import torch.backends.cudnn as cudnn
import torch.nn as nn
import torch.nn.functional as F
from torch import optim

from torch.optim import lr_scheduler
from dice_loss import dice_coeff
from unet import UNet
from utils import get_images
from dataset import IDRIDDataset
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader, Dataset
import copy

def eval_model(model):
    model.eval()
    tot = 0
    for inputs, true_masks in eval_loader:
        masks_pred = model(inputs)
        mask_pred = (F.sigmoid(masks_pred) > 0.5).float()
        tot += dice_coeff(mask_pred, true_mask).item()
    return tot / len(eval_dataset)

def train_model(model, train_loader, eval_loader, criterion, optimizer, scheduler, batch_size, num_epochs=5):
    best_model = copy.deepcopy(model.state_dict())
    best_acc = 0.
    for epoch in range(num_epochs):
        print('Starting epoch {}/{}.'.format(epoch + 1, num_epochs))
        scheduler.step()
        model.train()
        epoch_loss = 0
        all_steps = len(train_dataset)/batch_size
        for inputs, true_masks in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            masks_pred = model(imgs)
            masks_probs = F.sigmoid(masks_pred)
            masks_probs_flat = masks_probs.view(-1)

            true_masks_flat = true_masks.view(-1)

            loss = criterion(masks_probs_flat, true_masks_flat)
            epoch_loss += loss.item()

            print('{0:.4f} --- loss: {1:.6f}'.format(i * batch_size / N_train, loss.item()))

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print('Epoch finished ! Loss: {}'.format(epoch_loss / i))

        val_dice = eval_model(model)
        print('Validation Dice Coeff: {}'.format(val_dice))

        if save_cp:
            torch.save(net.state_dict(),
                       dir_checkpoint + 'CP{}.pth'.format(epoch + 1))
            print('Checkpoint {} saved !'.format(epoch + 1))



def get_args():
    parser = OptionParser()
    parser.add_option('-e', '--epochs', dest='epochs', default=5, type='int',
                      help='number of epochs')
    parser.add_option('-b', '--batch-size', dest='batchsize', default=10,
                      type='int', help='batch size')
    parser.add_option('-l', '--learning-rate', dest='lr', default=0.1,
                      type='float', help='learning rate')
    parser.add_option('-c', '--load', dest='load',
                      default=False, help='load file model')

    (options, args) = parser.parse_args()
    return options

if __name__ == '__main__':
    args = get_args()

    model = UNet(n_channels=3, n_classes=4)

    if args.load:
        model.load_state_dict(torch.load(args.load))
        print('Model loaded from {}'.format(args.load))
    
    image_dir = '/media/hdd1/qiqix/IDRID/Sub1'
    train_image_paths, train_mask_paths = get_images(image_dir, 'train')
    eval_image_paths, eval_mask_paths = get_images(image_dir, 'eval')

    train_dataset = IDRIDDataset(train_image_paths, train_mask_paths, 4, transform=
                                transforms.Compose([
                                transforms.ToTensor(),
                                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
                    ]))
    eval_dataset = IDRIDDataset(eval_image_paths, eval_mask_paths, 4, transform=
                                transforms.Compose([
                                transforms.ToTensor(),
                                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
                    ]))

    train_loader = DataLoader(train_dataset, args.batchsize, shuffle=True)
    eval_loader = DataLoader(eval_dataset, args.batchsize, shuffle=False)

    optimizer = optim.SGD(model.parameters(),
                              lr=args.lr,
                              momentum=0.9,
                              weight_decay=0.0005)
    scheduler = lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    criterion = nn.BCELoss()
    train_model(model, train_loader, eval_loader, criterion, optimizer, scheduler, args.batchsize, num_epochs=args.epochs)
