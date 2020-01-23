import time
from pathlib import Path


class DebugLogger:

    def __init__(self):
        self.plotting_directory = None
        self.log_file = None
        self.text_mem = ""

    def initialize_logging(self, plotting_directory):
        self.plotting_directory = plotting_directory
        self.log_file = Path(self.plotting_directory + '/log.txt')
        start_time = time.asctime()
        try:
            with open(self.log_file, mode='x') as logfile:
                logfile.write('START OF LOG\n')
                logfile.write(str(start_time) + '\n')
                logfile.write('---------------------------------------------\n')
        except FileExistsError:
            with open(self.log_file, mode='a') as logfile:
                logfile.write('---------------------------------------------\n')
                logfile.write('---------------------------------------------\n')
                logfile.write('-----------APPENDING TO OLD LOG---------\n')
                logfile.write('START OF LOG\n')
                logfile.write(str(start_time) + '\n')
                logfile.write('---------------------------------------------\n')
        finally:
            with open(self.log_file, mode='a') as logfile:
                logfile.write('\n-----------------TEMP MEM DUMP START------------------------\n')
                logfile.write(self.text_mem)
                logfile.write('\n-----------------TEMP MEM DUMP END------------------------\n')

    def write_to_log(self, text: str):
        if self.log_file is None:
            self.text_mem = self.text_mem + text
        else:
            with open(self.log_file, mode='a') as logfile:
                logfile.write('\n' + text + '\n')

    def write_to_log_time(self, text: str):
        if self.log_file is None:
            self.text_mem = self.text_mem + '\n----' + time.asctime() + '----\n' + '\n' + text + '\n'
        else:
            with open(self.log_file, mode='a') as logfile:
                logfile.write('\n----' + time.asctime() + '----\n')
                logfile.write('\n' + text + '\n')
