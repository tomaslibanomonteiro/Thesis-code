class MyClass():
    def __init__(self, name):
        self.name = name
        self.a = 1
        self.b = 2
        self.c = 3
        self.list = [self.a, self.b, self.c]
        
    def method(self, list):
        for i in list:
            i+=1

obj = MyClass("name")
print(obj.list)
obj.method(obj.list)
print(obj.list)