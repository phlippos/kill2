from enum import Enum
from time import time

class LogType(Enum):
    CLIENT_INFO = "client_info"
    
class Logger:
    @staticmethod
    def send_log(log_type,message):
        if log_type not in LogType:
            print("[Error] Log type not found in LogType")
            return
        print(f"[{log_type}] - {time()} - {message}")
        
        