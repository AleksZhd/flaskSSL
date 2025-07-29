def function(file_path: str) -> tuple:
    error = ''
    file_list = []
    try:
        file = open(file_path)

    except Exception as error:
        return error, file_list    
    file_list = file.readlines()
    file.close()
    if len(file_list) == 0:
        error = 'Empty File'
    return error, file_list

error, list = function('/home/aleks/flaskSSL/test.conf')
if error == '':
    print ('No errors')
else:
    print(error)    
print ('\n')
print (list)