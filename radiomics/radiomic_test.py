
myint = 200

def x():
    global myint
    myint = 100
    y()

def y():
    print(myint)

x()