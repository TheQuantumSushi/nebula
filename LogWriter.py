import datetime
import json

class LogWriter:
    def __init__(self, log_file):
        """
        Initialize the log file and entry/error numbers
        """
        self.log_file = log_file
        with open("config.json") as config_file:
            self.config = json.load(config_file)
        self.entry_number = self.config["log"]["entry_number"]
        self.error_number = self.config["log"]["error_number"]

    def _get_timestamp(self):
        """
        Get the current timestamp in ISO 8601 format with timezone info
        """
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    def _increment_entry_number(self, log_type):
        """
        Increment the number of entries and errors in config.json and for the script
        """
        self.config["log"]["entry_number"] += 1
        if log_type == "ERROR":
            self.config["log"]["error_number"] += 1
        with open("config.json", 'w') as config_file:
            json.dump(self.config, config_file, indent=2)
        self.entry_number = self.config["log"]["entry_number"]
        self.error_number = self.config["log"]["error_number"]

    def write(self, log_type, args):
        """
        Write a prettified log entry of the specified type to the log file using config.json for argument specification
        """
        self._increment_entry_number(log_type)
        with open(self.log_file, 'a') as file:
            file.write(f"Entry {self.entry_number} :\n")
            file.write(f"├── Timestamp : {self._get_timestamp()}\n")
            file.write(f"└── Type : {log_type}\n")
            for entry_line in self.config["log"]["types"][log_type][:-1]:
                file.write(f"    ├── {entry_line} : {args[entry_line]}\n")
            file.write(f"    └── {self.config["log"]["types"][log_type][-1]} : {args[self.config["log"]["types"][log_type][-1]]}\n")

# Example usage
if __name__ == "__main__":
    logger = LogWriter("log.txt")
    # Example of logging commands for every type of events (to copy paste from so that arguments are already written)
    logger.write("COMMAND", {"command":"", "requires sudo":"", "invoker":"", "output (STDOUT stream)":"", "errors (STDERR Stream)":""})
    logger.write("INFO", {"message":""})
    logger.write("DEBUG", {"message":""})
    logger.write("ERROR", {"message":"", "raised by":""})
    logger.write("WARNING", {"message":"", "raised by":""})
    logger.write("EVENT", {"event":"","output":""})
    logger.write("ACTION", {"action":"", "invoker":"", "output":""})