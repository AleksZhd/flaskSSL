import os


file = open("test.conf")
file_list = file.readlines()
file.close()
config_list = [['BEGINING']]
x = 0
block = 0
while x < len(file_list):
    if file_list[x].find('[') !=-1:
            # found a new block in cinfig file
        config_list.append([])
        block = block + 1
    
    config_list[block].append(file_list[x].strip())
    x = x + 1
print (block)    

x = 0
while x <= block:
    print(config_list[x])
    print('\n')
    x=x+1