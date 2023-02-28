import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch
import pandas as pd
import json


def pram(cont):
    return [j for i in cont for j in i]


def depram(cont, s1, s2):
    return [[cont[s2 * x + y] for y in range(s2)] for x in range(s1)]


class Sap_alt(nn.Module): # на вход 1 * кол - во элементов в самом глубок списке * количество самых глубоких списков
    def __init__(self, s1, s2):
        super(Sap_alt, self).__init__()
        self.fc1 = nn.Linear(480, 480)
        self.fc2 = nn.Linear(480, 480)
        self.fc3 = nn.Linear(480, 480)
        self.fc4 = nn.Linear(1440, 480)
        self.ls = 1000

    def forward(self, x):
        x = x.view(3, 480)
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)
        x = x.view(1, 1440)[0]
        x = self.fc4(x)
        return F.softmax(x, -1)


    def Saptr(self, cont): # список списков на вход
        criterion = nn.CrossEntropyLoss()
        learning_rate = 0.15
        optimizer = optim.SGD(self.parameters(), lr=learning_rate)
        for epoch in range(len(cont)):
            optimizer.zero_grad()
            mod = cont.iloc[epoch]
            x_t = [json.loads(i) for i in mod[:-1]]
            y_t = json.loads(mod[-1])
            predictions = self(torch.FloatTensor(x_t))
            loss = criterion(predictions, torch.FloatTensor(y_t))
            if self.ls > loss:
                self.ls = loss
                print(self.ls)
                loss.backward()
                optimizer.step()


    def z_ontr(self, cont, tc, n): # список списков на вход, кол - во желаемых результатов
        derp = tc
        a = [derp[i] if cont[i] != 1 else 0 for i in range(len(derp))]
        a = sorted(a, key=float) if n > len(a) else sorted(a, key=float)[-n:]
        return [cont[i] if derp[i] not in a else 2 for i in range(len(cont))]


    def z_on(self, cont, n): # список списков на вход, кол - во желаемых результатов
        s1, s2 = len(cont[1]), len(cont[1][0])
        """cont = [j for i in cont for j in i]"""
        derp = self(torch.FloatTensor(cont))
        a = [derp[i] if pram(cont[1])[i] != 1 else 0 for i in range(len(derp))]
        a = sorted(a, key=float) if n > len(a) else sorted(a, key=float)[-n:]
        cont = [pram(cont[1])[i] if derp[i] not in a else 2 for i in range(len(pram(cont[1])))]
        return [[cont[s2 * x + y] for y in range(s2)] for x in range(s1)]