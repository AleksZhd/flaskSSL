class Weapon:
    category = 'sword'
    def __init__(self, name, power):
        self.name = name
        self.power = power

class Shiled:
    name = 'default'
    strenght = 100

class Loop_it:
    def __init__(self, amount):
        x = 0
        while x < amount:
            name = "line#" + str(x)
            self.name = name
            x = x + 1        
            ### POLNII BREEED
def main():
    blade = Weapon(name = 'Sword',power = '100')
    print (blade)

if __name__ == "__main__":
    main()