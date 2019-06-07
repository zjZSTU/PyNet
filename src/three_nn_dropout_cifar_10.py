# -*- coding: utf-8 -*-

# @Time    : 19-6-7 下午12:23
# @Author  : zj

from data.load_cifar_10 import *
from nn.nets import *
from nn.net_utils import *
import matplotlib.pyplot as plt
import time

# 批量大小
batch_size = 256
# 输入维数
D = 3072
# 隐藏层大小
H1 = 2000
H2 = 800
# 输出类别
K = 40

# 学习率
lr = 1e-3
# 正则化强度
reg_rate = 1e-3


def compute_accuracy(x, y, net, batch_size=128):
    total_accuracy = 0.0
    num = 0
    range_list = np.arange(0, x.shape[0] - batch_size, step=batch_size)
    for i in range_list:
        data = x[i:i + batch_size]
        labels = y[i:i + batch_size]

        scores = net.predict(data)
        predicted = np.argmax(scores, axis=1)
        total_accuracy += np.mean(predicted == labels)
        num += 1
    return total_accuracy / num


def draw(loss_list, title='损失图', ylabel='损失值', xlabel='迭代/100次'):
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.plot(loss_list)
    plt.show()


if __name__ == '__main__':
    x_train, x_test, y_train, y_test = load_cifar_10_data(shuffle=True)

    x_train = x_train / 255 - 0.5
    x_test = x_test / 255 - 0.5

    net = ThreeLayerNet(D, H1, H2, K, p_h=0.5)
    criterion = CrossEntropyLoss()

    loss_list = []
    train_accuracy_list = []
    best_train_accuracy = 0.995
    best_test_accuracy = 0

    range_list = np.arange(0, x_train.shape[0] - batch_size, step=batch_size)
    for i in range(200):
        start = time.time()
        total_loss = 0
        for j in range_list:
            data = x_train[j:j + batch_size]
            labels = y_train[j:j + batch_size]

            scores = net.forward(data)
            loss = criterion.forward(scores, labels)
            # print(loss)
            total_loss += loss
            dout = criterion.backward()
            net.backward(dout)
            net.update(lr=lr, reg=reg_rate)
        end = time.time()

        avg_loss = total_loss / len(range_list)
        loss_list.append(float('%.4f' % avg_loss))
        print('epoch: %d time: %f loss: %.4f' % (i + 1, end - start, avg_loss))

        # 计算训练数据集检测精度
        train_accuracy = compute_accuracy(x_train, y_train, net, batch_size=batch_size)
        train_accuracy_list.append(float('%.4f' % train_accuracy))
        if best_train_accuracy < train_accuracy:
            best_train_accuracy = train_accuracy

            test_accuracy = compute_accuracy(x_test, y_test, net, batch_size=batch_size)
            if best_test_accuracy < test_accuracy:
                best_test_accuracy = test_accuracy
                save_params(net.get_params(), path='./three-nn-dropout-epochs-%d.pkl' % (i + 1))

        print('best train accuracy: %.2f %%   best test accuracy: %.2f %%' % (
            best_train_accuracy * 100, best_test_accuracy * 100))
        print(loss_list)
        print(train_accuracy_list)

        if i % 50 == 49:
            lr /= 2

    draw(loss_list, title='损失图', xlabel='迭代/次')
    draw(train_accuracy_list, title='训练图', ylabel='检测精度', xlabel='迭代/次')
