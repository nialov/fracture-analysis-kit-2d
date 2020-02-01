import time
from pathlib import Path
import logging

class DebugLogger:

    def __init__(self):
        self.plotting_directory = None
        self.log_file = None
        self.debug_file = None
        self.text_mem = ""

    def reset_logging(self):
        manager = logging.root.manager
        manager.disabled = logging.NOTSET
        for logger in manager.loggerDict.values():
            if isinstance(logger, logging.Logger):
                logger.setLevel(logging.NOTSET)
                logger.propagate = True
                logger.disabled = False
                logger.filters.clear()
                handlers = logger.handlers.copy()
                for handler in handlers:
                    # Copied from `logging.shutdown`.
                    try:
                        handler.acquire()
                        handler.flush()
                        handler.close()
                    except (OSError, ValueError):
                        pass
                    finally:
                        handler.release()
                    logger.removeHandler(handler)

    def initialize_logging(self, plotting_directory):
        self.plotting_directory = plotting_directory
        self.log_file = Path(f'{plotting_directory}/debug.log')
        self.debug_file = Path(f'{plotting_directory}/debug_full.log')
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
            # Initialize python logger
            self.reset_logging()

            logger = logging.getLogger('logging_tool')
            logger.setLevel(logging.DEBUG)

            fh = logging.FileHandler(self.log_file)
            fh.setLevel(logging.INFO)

            fh2 = logging.FileHandler(self.debug_file, mode='x')
            fh2.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

            fh.setFormatter(formatter)
            fh2.setFormatter(formatter)

            logger.addHandler(fh)
            logger.addHandler(fh2)
            logger.info('-----------------Python logging tool initialized.-----------------')


    def write_to_log_mem(self, text: str):
        if self.log_file is None:
            self.text_mem = self.text_mem + text
        else:
            logging.warning(text)
            # with open(self.log_file, mode='a') as logfile:
            #     logfile.write('\n' + text + '\n')

    def write_to_log_mem_time(self, text: str):
        if self.log_file is None:
            self.text_mem = self.text_mem + '\n----' + time.asctime() + '----\n' + '\n' + text + '\n'
        else:
            logging.warning(text)

# class DebugLogger:
#
#     def __init__(self):
#         self.plotting_directory = None
#         self.log_file = None
#         self.text_mem = ""
#
#     def initialize_logging(self, plotting_directory):
#         self.plotting_directory = plotting_directory
#         self.log_file = Path(self.plotting_directory + '/log.txt')
#         start_time = time.asctime()
#         try:
#             with open(self.log_file, mode='x') as logfile:
#                 logfile.write('START OF LOG\n')
#                 logfile.write(str(start_time) + '\n')
#                 logfile.write('---------------------------------------------\n')
#         except FileExistsError:
#             with open(self.log_file, mode='a') as logfile:
#                 logfile.write('---------------------------------------------\n')
#                 logfile.write('---------------------------------------------\n')
#                 logfile.write('-----------APPENDING TO OLD LOG---------\n')
#                 logfile.write('START OF LOG\n')
#                 logfile.write(str(start_time) + '\n')
#                 logfile.write('---------------------------------------------\n')
#         finally:
#             with open(self.log_file, mode='a') as logfile:
#                 logfile.write('\n-----------------TEMP MEM DUMP START------------------------\n')
#                 logfile.write(self.text_mem)
#                 logfile.write('\n-----------------TEMP MEM DUMP END------------------------\n')
#
#     def write_to_log(self, text: str):
#         if self.log_file is None:
#             self.text_mem = self.text_mem + text
#         else:
#             with open(self.log_file, mode='a') as logfile:
#                 logfile.write('\n' + text + '\n')
#
#     def write_to_log_time(self, text: str):
#         if self.log_file is None:
#             self.text_mem = self.text_mem + '\n----' + time.asctime() + '----\n' + '\n' + text + '\n'
#         else:
#             with open(self.log_file, mode='a') as logfile:
#                 logfile.write('\n----' + time.asctime() + '----\n')
#                 logfile.write('\n' + text + '\n')
#
