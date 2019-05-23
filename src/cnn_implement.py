import numpy as np
import os
from torch.autograd import Variable
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
from torchvision import datasets
from torch.utils.data import DataLoader, Sampler
import torch.optim as optim
import cv2
from PIL import Image
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn import svm
import time
import pickle
import filters


dataset = pickle.load(open("dataset.pickle","rb"))
train,test = train_test_split(dataset,test_size = 0.2, random_state = 0)

pickle_out = open("test.pickle","wb")
pickle.dump(test,pickle_out)
pickle_out.close()


class SimpleCNN(nn.Module):

	def __init__(self):
		super(SimpleCNN, self).__init__()

		#Input channels 3 output channels 30
		self.conv1 = nn.Conv2d( 3, 30, kernel_size = 5, stride = 1, padding = 0 )
		#self.conv1.weight = nn.Parameter(filters.get_filters())
		self.conv2 = nn.Conv2d( 30, 30, kernel_size = 5, stride = 2, padding = 0 )
		self.pool1 = nn.MaxPool2d(kernel_size = 2, stride = 2, padding = 0)
		self.conv3 = nn.Conv2d( 30, 16, kernel_size = 3, stride = 1, padding = 0 )
		self.conv4 = nn.Conv2d( 16, 16, kernel_size = 3, stride = 1, padding = 0 )
		self.conv5 = nn.Conv2d( 16, 16, kernel_size = 3, stride = 1, padding = 0 )
		self.pool2 = nn.MaxPool2d( kernel_size = 2, stride = 2, padding = 0 )
		self.conv6 = nn.Conv2d( 16, 16, kernel_size = 3, stride = 1, padding = 0 )
		self.conv7 = nn.Conv2d( 16, 16, kernel_size = 3, stride = 1, padding = 0 )
		self.conv8 = nn.Conv2d( 16, 16, kernel_size = 3, stride = 1, padding = 0 )
		self.conv9 = nn.Conv2d( 16, 16, kernel_size = 3, stride = 1, padding = 0 )
		self.fc1 = nn.Linear(16*5*5, 1000)
		self.drop1 = nn.Dropout(p=0.5)
		self.fc2 = nn.Linear(1000,2)
		
	def forward(self,x):
		#print("x", x.size())
		x = x.unsqueeze(0)
		print("x-initial", x.size())
		x = F.relu(nn.init.xavier_uniform(self.conv1(x)))
		print("x-2", x.size())
		x = F.relu(nn.init.xavier_uniform(self.conv2(x)))
		print("x-3", x.size())
		lrn = nn.LocalResponseNorm(2)
		x = lrn(x)
		print("x-n", x)
		x = self.pool1(x)
		print("x-4", x.size())
		x = F.relu(nn.init.xavier_uniform(self.conv3(x)))
		print("x-5", x.size())
		x = F.relu(nn.init.xavier_uniform(self.conv4(x)))
		print("x-6", x.size())
		x = F.relu(nn.init.xavier_uniform(self.conv5(x)))
		print("x-7", x.size())
		x = F.relu(nn.init.xavier_uniform(self.conv6(x)))
		print("x-8", x.size())
		x = lrn(x)
		x = self.pool2(x)
		print("x-9", x.size())
		x = F.relu(nn.init.xavier_uniform(self.conv7(x)))
		print("x-10", x.size())
		x = F.relu(nn.init.xavier_uniform(self.conv8(x)))
		x = F.relu(nn.init.xavier_uniform(self.conv9(x)))
		print("x-final",x.size())
		x = x.view(-1, 16*5*5) #(16*22*22)
		x = F.relu(self.fc1(x))
		x = self.drop1(x)
		x = self.fc2(x)
		
		return(x)

def outputSize(in_size, kernel_size, stride, padding):

	output = int((in_size-kernel_size+2*(padding))/stride) + 1

	return output

def createLossandOptimizer(net, learning_rate = 0.001):
		loss = nn.CrossEntropyLoss()
		optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
		return(loss,optimizer)
def trainNet(net, n_epochs, learning_rate):

	print("===Hyperparameters===")
	print("epochs=", n_epochs)
	print("learning_rate=", learning_rate)
	

	loss,optimizer = createLossandOptimizer(net, learning_rate)
    
	training_start_time = time.time()

	for epoch in range(n_epochs):

		running_loss = 0.0
		start_time = time.time()
		total_train_loss = 0.0
		for i,data in enumerate(train,0):
			inputs,labels = data
			optimizer.zero_grad()

			outputs = net(inputs)
			labels = [labels]
			labels = torch.from_numpy(np.array(labels))
			loss_size = loss(outputs,labels)
			loss_size.backward()
			optimizer.step()

			#Print statistics
			running_loss += loss_size.item()
			if i % 2000 == 1999:    # print every 2000 mini-batches
				print('[%d, %5d] loss: %.3f' %
				   (epoch + 1, i + 1, running_loss / 2000))
				running_loss = 0.0

	print('Finished Training')

CNN = SimpleCNN()
trainNet(CNN, n_epochs = 1, learning_rate = 0.001)

torch.save(CNN.state_dict(),'/Users/arkajitbhattacharya/Documents/Pytorch_Project/Simple_Cnn.pt')
