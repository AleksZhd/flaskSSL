import sys

def file_2_list(file_name)->list:
    error = 'NONE'
    file_list = []
    try:
        file = open(file_name)
    except FileNotFoundError:
        error = "File "+ file_name + " was not found"    
    except PermissionError:
        error = "Permission Error at opening file: " + file_name
    except:
        error = "Unexpected error at opening file: "+ file_name
    else:
        file_list = file.readlines()
        file.close()
        if len(file_list) == 0:
            error = "EMPTY FILE"
        else:
            x=0
            while x<len(file_list):
                file_list[x] = file_list[x][:file_list[x].find('\n')]
                x=x+1
    return [error, file_list]

def main():
    if len(sys.argv) == 2:
        list_of_file = file_2_list (sys.argv[1])
        print (list_of_file)
    else:
        print ("No file name prvided")
    

if __name__ == "__main__":
    main()