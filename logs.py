import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


# Custom logging setup
mylogger = logging.getLogger("Custome")
mylogger.setLevel(logging.INFO)

# time format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

file_handler = RotatingFileHandler("logs.log", maxBytes=10000, backupCount=1)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

mylogger.addHandler(file_handler)
mylogger.debug("This message should go to the log file")


# function to fetch logs for past N hours
def get_logs(hours: int) -> list[str]:
    logs: list[str] = []
    with open("logs.log", "r") as file:
        lines = file.readlines()
        current_time = datetime.now()
        for line in lines:
            time = datetime.strptime(line.split(" - ")[0], "%Y-%m-%d %H:%M:%S")
            if (current_time - time).seconds / 3600 < hours:
                logs.append(line.strip())

    return logs
