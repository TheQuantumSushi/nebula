import datetime

class LogWriter:
    def __init__(self, log_file):
        """
        Initialize the LogWriter with the specified log file path.
        """
        self.log_file = log_file
        self.entry_number = 1  # Initialize entry count

    def _get_timestamp(self):
        """
        Get the current timestamp in ISO 8601 format with timezone info.
        """
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    def write(self, log_type, args):
        """
        Write a log entry of the specified type to the log file.
        
        Parameters:
        - log_type (str): Type of log entry (e.g., DEBUG, INFO, COMMAND).
        - args (dict): Dictionary containing relevant details for each log type.
        """
        with open(self.log_file, 'a') as file:
            # Common entry header
            file.write(f"Entry {self.entry_number} [timestamp : {self._get_timestamp()}]\n")
            file.write(f"  Type : {log_type}\n")

            # Format log entries based on type
            if log_type == "DEBUG":
                file.write(f"    Debug Message: {args.get('message', 'No message provided')}\n")
            elif log_type == "INFO":
                file.write(f"    Info Message: {args.get('message', 'No message provided')}\n")
            elif log_type == "WARNING":
                file.write(f"    Warning Message: {args.get('message', 'No message provided')}\n")
            elif log_type == "ERROR":
                file.write(f"    Error Message: {args.get('message', 'No message provided')}\n")
            elif log_type == "CRITICAL":
                file.write(f"    Critical Message: {args.get('message', 'No message provided')}\n")
            elif log_type == "COMMAND":
                file.write(f"    Command: {args.get('command', 'No command specified')}\n")
                file.write(f"    Requires sudo: {args.get('requires_sudo', 'False')}\n")
                file.write(f"    Invoker: {args.get('invoker', 'Unknown')}\n")
            elif log_type == "COMMAND_OUTPUT":
                file.write(f"    Command Output: {args.get('output', 'No output available')}\n")
            elif log_type == "COMMAND_ERROR":
                file.write(f"    Command Error: {args.get('error', 'No error message')}\n")
            elif log_type == "ACTION":
                file.write(f"    Action Description: {args.get('action_description', 'No description provided')}\n")
                file.write(f"    Action Status: {args.get('status', 'Unknown')}\n")
            elif log_type == "EVENT":
                file.write(f"    Event Name: {args.get('event_name', 'No event name provided')}\n")
                file.write(f"    Event Details: {args.get('event_details', 'No event details provided')}\n")
            else:
                file.write(f"    Unknown log type: {log_type}\n")

            file.write("\n")  # Newline between entries for readability
            self.entry_number += 1  # Increment entry number

# Example usage
if __name__ == "__main__":
    logger = LogWriter("log.txt")
    
    # Example log entries
    logger.write("DEBUG", {"message": "Debugging started"})
    logger.write("INFO", {"message": "Process initialized"})
    logger.write("COMMAND", {
        "command": "ls -la /root",
        "requires_sudo": "True",
        "invoker": "user123"
    })
    logger.write("COMMAND_OUTPUT", {"output": "Listing files in /root"})
    logger.write("COMMAND_ERROR", {"error": "Permission denied"})
    logger.write("EVENT", {"event_name": "UserLogin", "event_details": "User 'user123' logged in"})
    logger.write("ACTION", {"action_description": "File upload", "status": "Success"})
