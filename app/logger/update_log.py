import os
import pathlib
from datetime import datetime

# generate root_dir for outputting debug files
cur_dir = pathlib.Path(__file__).parent
debug_dir = os.path.abspath(os.path.join(cur_dir, '..', '..', 'debugging'))

# main log
main_log = os.path.join(debug_dir, 'logs', 'log.txt')



def file_exists(file_path):
    # check if file exists and if not then create it
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write("")



def create_log_line(message):
    # create the log line
    cur_time = datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')
    log_line = f'{cur_time} - {message}\n'

    # update the log
    file_exists(main_log)
    with open(main_log, 'a') as f:
        f.write(log_line)