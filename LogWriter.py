import datetime
import json
import os
import re

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

    def flush(self, number_of_entries = 0, inverse = False):
        """
        Flush the log file of a certain number of entries
        0 = all of them, by default
        inverse : by default, deletes oldest entries, but inverse makes it delete the newest ones
        """
        if number_of_entries: # if the number of entries to delete is specified, flush the corresponding ones
            with open(self.log_file, 'r') as log_file:
                lines = log_file.readlines()
                # Determine values for the for loop based on if we should loop in increasing or decreasing order :
                (start, stop, step) = (len(lines) - 1, -1, -1) if inverse else (0, len(lines), 1)
                # "Entry x :" where x is an int is the pattern to match to count the number of entries (to detect the number of lines to delete, which is inconsistent based on log type) :
                pattern = r"Entry \d+ :"
                number_of_entries_found = 0
                number_of_entries_index = number_of_entries if inverse else number_of_entries + 1
                # Find the line matching the pattern, starting from the end
                for i in range(start, stop, step):
                    if re.match(pattern, lines[i]):
                        number_of_entries_found += 1
                    if number_of_entries_found == number_of_entries_index:
                        # If the pattern is found, truncate lines accordingly
                        lines = lines[:i] if inverse else lines[i:]
                        break
                    if ((i == 0 and inverse) or (i == len(lines)-1 and (not inverse))):
                        # If the list has been completely seen (meaning the number of entries was bigger than what was in the file), delete everything
                        lines = []
        else: # if it isn't specified, i.e. 0, then delete everything
            lines = []
        # Move to the beginning and write the modified lines back :
        with open(self.log_file, 'w') as log_file:
            log_file.seek(0)
            log_file.writelines(lines)
            log_file.truncate()  # Remove any leftover content



# Example usage
if __name__ == "__main__":
    logger = LogWriter("log.txt")
    logger.write("DEBUG", {"message":"hey, LogWriter.py works !"})
# Example of logging commands for every type of events (to copy paste from so that arguments are already written)
"""
logger.write("COMMAND", {"command":"", "requires sudo":"", "invoker":"", "output (STDOUT stream)":"", "errors (STDERR Stream)":""})
logger.write("INFO", {"message":""})
logger.write("DEBUG", {"message":""})
logger.write("WARNING", {"message":"", "raised by":f"file : {os.path.basename(__file__)}\n    instance : {self}\n    called by : {inspect.stack()[1].function}"})
logger.write("EVENT", {"event":"","triggered by":f"file : {os.path.basename(__file__)}\n    instance : {self}\n    called by : {inspect.stack()[1].function}", "output":"0"})
logger.write("ACTION", {"action":"", "invoker":f"file : {os.path.basename(__file__)}\n    instance : {self}\n    called by : {inspect.stack()[1].function}", "output":"0"})
"""