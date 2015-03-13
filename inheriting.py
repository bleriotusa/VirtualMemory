__author__ = 'Michael'

class Hi:
    x = 5
    def __init__(self, p):
        self.z = 2
        print('hi')

class There(Hi):
    def __init__(self, s):
        print('there')
        self.s = 1
        Hi.__init__(self, s)

y = There(2)
print(y.x)
print(y.z)