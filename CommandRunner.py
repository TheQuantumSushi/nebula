import subprocess
import threading
import time
import sys

class CommandError(Exception):
    """
    Custom error class that inherits from Exception, to raise errors with a message that also indicates which command was being run
    """
    def __init__(self, message, command):
        super().__init__(message)  # Initialize the base Exception with the message
        self.message = message
        self.command = command
    def display(self):
        """
        Print the formatted error message.
        """
        print(f"ERROR: {self.message}\nRaised trying to run command : {self.command}")

class CommandRunner:
    """
    Run commands inside a non-blocking separate thread and read stdout/stderr streams to print them and write them in log.txt
    """
    def __init__(self, command, sudo_required = False, sudo_password = None):
        self.command = command
        # If not provided as an argument, check if a sudo password is defined inside keyring (if necessary)
        if sudo_required:
            if sudo_password is None:
                try:
                    self.sudo_password = keyring.get_password("system", "sudo")
                except:
                    raise CommandError("No sudo password given as argument or defined in keyring", self.command)
                    sys.exit(1)
            else:
                self.sudo_password = sudo_password
        self.process = None
        self.stop_event = threading.Event()
        self.thread = None

        # Open the log file (write mode)
        self.log_file = open('log.txt', 'w')

    def _stream_reader(self, stream, stream_name):
        """
        Read lines from the specified stream and print/write them
        """
        while not self.stop_event.is_set():
            output = stream.readline()
            if output:
                log_message = f"{stream_name} : {output.strip()}"
                print(log_message)
                self.log_file.write(log_message + '\n')
                self.log_file.flush()  # Ensure it is written to the file immediately
            elif self.process.poll() is not None:  # Check if the process has finished
                break

    def run(self):
        """
        Run the command in a background thread and capture both stdout and stderr output streams
        """
        def target():
            """
            Define the target for the main thread: the subprocess, and two threads for capturing stdout and stderr
            """
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines = True,
                bufsize = 1
            )

            # Create and start separate threads for capturing stdout and stderr using _stream_reader:
            stdout_thread = threading.Thread(target = self._stream_reader, args = (self.process.stdout, "STDOUT"))
            stderr_thread = threading.Thread(target = self._stream_reader, args = (self.process.stderr, "STDERR"))
            stdout_thread.start()
            stderr_thread.start()

            # Join both threads:
            stdout_thread.join()
            stderr_thread.join()

        # Start the main thread as a daemon:
        self.thread = threading.Thread(target = target)
        self.thread.daemon = True  # Make the thread a daemon
        self.thread.start()

    def stop(self):
        """
        Stop the command and the background thread
        """
        # Terminate the subprocess:
        if self.process:
            self.process.terminate()
            self.process.wait()  # Wait for the process to terminate properly

        # Trigger the stop event to stop the thread and join it :
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()

        # Close the log file :
        self.log_file.close()


# Example usage :
if __name__ == "__main__":
    try:
        command_runner = CommandRunner(["/bin/ping", "google.com"])
        command_runner.run()
        time.sleep(10)
        command_runner.stop()
    except CommandError as e:
        e.display()