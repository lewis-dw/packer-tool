import os
import pathlib
from datetime import datetime

# generate root_dir for outputting debug files
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))



def file_exists(file_path):
    # check if file exists and if not then create it
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("")



def create_log_line(file_name, message):
    # define which log file to write to
    log_file = os.path.join(debug_dir, 'logs', f'{file_name}.txt')

    # create the log line
    cur_time = datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')
    log_line = f'{cur_time} - {message}\n'

    # update the log
    file_exists(log_file)
    with open(log_file, 'a') as f:
        f.write(log_line)