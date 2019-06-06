# -*- coding: utf-8 -*-

# @Time    : 19-5-27 下午1:34
# @Author  : zj

import numpy as np
from abc import ABCMeta, abstractmethod
from nn.im2row import *
from nn.pool2row import *
from nn.layer_utils import *
from nn.layers import *


class Net(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def forward(self, inputs):
        pass

    @abstractmethod
    def backward(self, grad_out):
        pass

    @abstractmethod
    def update(self, lr=1e-3, reg=1e-3):
        pass

    @abstractmethod
    def get_params(self):
        pass

    @abstractmethod
    def set_params(self, params):
        pass


class TwoLayerNet(Net):
    """
    实现2层神经网络
    """

    def __init__(self, num_in, num_hidden, num_out):
        super(TwoLayerNet, self).__init__()
        self.fc1 = FC(num_in, num_hidden)
        self.relu = ReLU()
        self.fc2 = FC(num_hidden, num_out)

    def __call__(self, inputs):
        return self.forward(inputs)

    def forward(self, inputs):
        # inputs.shape = [N, D_in]
        assert len(inputs.shape) == 2
        a1 = self.relu(self.fc1(inputs))
        z2 = self.fc2(a1)

        return z2

    def backward(self, grad_out):
        da1 = self.fc2.backward(grad_out)
        dz1 = self.relu.backward(da1)
        da0 = self.fc1.backward(dz1)

    def update(self, lr=1e-3, reg=1e-3):
        self.fc2.update(lr, reg)
        self.fc1.update(lr, reg)

    def get_params(self):
        return {'fc1': self.fc1.get_params(), 'fc2': self.fc2.get_params()}

    def set_params(self, params):
        self.fc1.set_params(params['fc1'])
        self.fc2.set_params(params['fc2'])


class ThreeLayerNet(Net):
    """
    实现3层神经网络
    """

    def __init__(self, num_in, num_h_one, num_h_two, num_out, momentum=0, p_h=1.0):
        super(ThreeLayerNet, self).__init__()
        self.fc1 = FC(num_in, num_h_one, momentum=momentum)
        self.relu1 = ReLU()
        self.fc2 = FC(num_h_one, num_h_two, momentum=momentum)
        self.relu2 = ReLU()
        self.fc3 = FC(num_h_two, num_out, momentum=momentum)
        self.p_h = p_h

    def __call__(self, inputs):
        return self.forward(inputs)

    def forward(self, inputs):
        # inputs.shape = [N, D_in]
        assert len(inputs.shape) == 2
        a1 = self.relu1(self.fc1(inputs))
        U1 = np.random.ranf(a1.shape) < self.p_h
        a1 *= U1

        a2 = self.relu2(self.fc2(a1))
        U2 = np.random.ranf(a2.shape) < self.p_h
        a2 *= U2

        z3 = self.fc3(a2)

        return z3

    def backward(self, grad_out):
        da2 = self.fc3.backward(grad_out)
        dz2 = self.relu2.backward(da2)
        da1 = self.fc2.backward(dz2)
        dz1 = self.relu1.backward(da1)
        da0 = self.fc1.backward(dz1)

    def update(self, lr=1e-3, reg=1e-3):
        self.fc3.update(learning_rate=lr, regularization_rate=reg)
        self.fc2.update(learning_rate=lr, regularization_rate=reg)
        self.fc1.update(learning_rate=lr, regularization_rate=reg)

    def predict(self, inputs):
        # inputs.shape = [N, D_in]
        assert len(inputs.shape) == 2
        a1 = self.relu1(self.fc1(inputs))
        a1 *= self.p_h

        a2 = self.relu2(self.fc2(a1))
        a2 *= self.p_h

        z3 = self.fc3(a2)

        return z3

    def get_params(self):
        return {'fc1': self.fc1.get_params(), 'fc2': self.fc2.get_params(), 'fc3': self.fc3.get_params(),
                'p_h': self.p_h}

    def set_params(self, params):
        self.fc1.set_params(params['fc1'])
        self.fc2.set_params(params['fc2'])
        self.fc3.set_params(params['fc3'])
        self.p_h = params['p_h']


class LeNet5(Net):
    """
    LeNet-5网络
    """

    def __init__(self, momentum=0):
        super(LeNet5, self).__init__()
        self.conv1 = Conv2d(1, 5, 5, 6, stride=1, padding=0, momentum=momentum)
        self.conv2 = Conv2d(6, 5, 5, 16, stride=1, padding=0, momentum=momentum)
        self.conv3 = Conv2d(16, 5, 5, 120, stride=1, padding=0, momentum=momentum)

        self.maxPool1 = MaxPool(2, 2, 6, stride=2)
        self.maxPool2 = MaxPool(2, 2, 16, stride=2)
        self.fc1 = FC(120, 84, momentum=momentum)
        self.fc2 = FC(84, 10, momentum=momentum)

        self.relu1 = ReLU()
        self.relu2 = ReLU()
        self.relu3 = ReLU()
        self.relu4 = ReLU()

    def __call__(self, inputs):
        return self.forward(inputs)

    def forward(self, inputs):
        # inputs.shape = [N, C, H, W]
        assert len(inputs.shape) == 4
        x = self.relu1(self.conv1(inputs))
        x = self.maxPool1(x)
        x = self.relu2(self.conv2(x))
        x = self.maxPool2(x)
        x = self.relu3(self.conv3(x))
        # (N, C, 1, 1) -> (N, C)
        x = x.reshape(x.shape[0], -1)
        x = self.relu4(self.fc1(x))
        x = self.fc2(x)

        return x

    def backward(self, grad_out):
        da6 = self.fc2.backward(grad_out)

        dz6 = self.relu4.backward(da6)
        da5 = self.fc1.backward(dz6)
        # [N, C] -> [N, C, 1, 1]
        N, C = da5.shape[:2]
        da5 = da5.reshape(N, C, 1, 1)

        dz5 = self.relu3.backward(da5)
        da4 = self.conv3.backward(dz5)

        dz4 = self.maxPool2.backward(da4)

        dz3 = self.relu2.backward(dz4)
        da2 = self.conv2.backward(dz3)

        da1 = self.maxPool1.backward(da2)
        dz1 = self.relu1.backward(da1)

        self.conv1.backward(dz1)

    def update(self, lr=1e-3, reg=1e-3):
        self.fc2.update(learning_rate=lr, regularization_rate=reg)
        self.fc1.update(learning_rate=lr, regularization_rate=reg)
        self.conv3.update(learning_rate=lr, regularization_rate=reg)
        self.conv2.update(learning_rate=lr, regularization_rate=reg)
        self.conv1.update(learning_rate=lr, regularization_rate=reg)

    def get_params(self):
        out = dict()
        out['conv1'] = self.conv1.get_params()
        out['conv2'] = self.conv2.get_params()
        out['conv3'] = self.conv3.get_params()

        out['fc1'] = self.fc1.get_params()
        out['fc2'] = self.fc2.get_params()

        return out

    def set_params(self, params):
        self.conv1.set_params(params['conv1'])
        self.conv2.set_params(params['conv2'])
        self.conv3.set_params(params['conv3'])

        self.fc1.set_params(params['fc1'])
        self.fc2.set_params(params['fc2'])
