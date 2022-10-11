import os

class FileParser:
    '''Parsing class of the file with module readings'''

    @staticmethod
    def reduce_readings(file_path : str) -> str:
        '''Optimizing the file with readings, deleting unnecessary lines'''
        last_header = ""
    
        REDUCED_FILE_NAME = os.path.splitext(file_path)[0] + "_reduced.txt";

        if (len(os.path.dirname(file_path)) == 0):
            result_path = REDUCED_FILE_NAME
        else:
            result_path = os.path.join(os.path.dirname(file_path), REDUCED_FILE_NAME)

        file_w = open(result_path, 'w', encoding='UTF-8')

        with open(file_path, 'r', encoding='UTF-8') as file_r:
            while True:
                line = file_r.readline()

                if not line:
                    break
                
                elif line[1] == "H":
                    if last_header == "" or last_header != line:
                        file_w.write(line)
                    last_header = line
                
                else:
                    file_w.write(line)

        file_w.close()
