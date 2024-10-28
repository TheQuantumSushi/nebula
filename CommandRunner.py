import subprocess
import threading
import time
import sys
import shlex
import inspect
import os
import keyring

class CommandError(Exception):
    """
    Custom error class that inherits from Exception, to raise errors with a message that also indicates which command was being run
    """
    def __init__(self, message, command, logger):
        super().__init__(message)  # Initialize the base Exception with the message
        self.message = message
        self.command = command
        self.logger = logger

    def log(self):
        """
        Print the formatted error message.
        """
        # Write to log file :
        self.logger.write("ERROR", {"message":f"{self.message}", "raised by":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}", "running command":f"{self.command}"}})

class CommandRunner:
    """
    Run commands inside a non-blocking separate thread and read stdout/stderr streams to print them and write them in log.txt
    """
    def __init__(self, command, logger, sudo_required = False, sudo_password = None):
        self.logger = logger
        self.command = command
        self.sudo_required = sudo_required
        # If not provided as an argument, check if a sudo password is defined inside keyring (if necessary)
        if sudo_required:
            if sudo_password is None:
                try:
                    self.sudo_password = keyring.get_password("system", "sudo")
                    # Write to log file :
                    self.logger.write("ACTION", {"action":"retrieve sudo password from keyring", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
                except:
                    raise CommandError("no sudo password given as argument or defined in keyring", self.command, self.logger)
                    sys.exit(1)
            else:
                self.sudo_password = sudo_password
                # Write to log file :
                self.logger.write("INFO", {"message":f"sudo password provided manually while running command {self.command}"})
        self.process = None
        self.stop_event = threading.Event()
        self.thread = None
        # Write to log file :
        self.logger.write("ACTION", {"action":"initialize CommandRunner instance", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})

    def _stream_reader(self, stream, stream_name):
        """
        Read lines from the specified stream and print/write them
        """
        while not self.stop_event.is_set():
            output = stream.readline()
            if output:
                log_message = f"{stream_name} : {output.strip()}"
                print(log_message)
                #self.log_file.write(log_message + '\n')
                #self.log_file.flush()  # Ensure it is written to the file immediately
            elif self.process.poll() is not None:  # Check if the process has finished
                break

    def run(self):
        """
        Run the command in a background thread and capture both stdout and stderr output streams
        """

        # Write to log file :
        self.logger.write("ACTION", {"action":f"run command {self.command}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})

        def target():
            """
            Define the target for the main thread: the subprocess, and two threads for capturing stdout and stderr
            """

            # Format the command to a list usable by subprocess.Popen() and include sudo if required :
            self.formatted_command = shlex.split(f"/bin/echo {self.sudo_password} | sudo -S " + self.command) if self.sudo_required else shlex.split(self.command)
            # Create the command-executing process :
            self.process = subprocess.Popen(
                self.formatted_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines = True,
                bufsize = 1
            )
            # Write to log file :
            self.logger.write("ACTION", {"action":f"create subprocess {self.process} to run command {self.command}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
            # Create separate threads for capturing stdout and stderr using _stream_reader :
            stdout_thread = threading.Thread(target = self._stream_reader, args = (self.process.stdout, "STDOUT"))
            stderr_thread = threading.Thread(target = self._stream_reader, args = (self.process.stderr, "STDERR"))
            # Write to log file :
            self.logger.write("ACTION", {"action":f"create stdout and stderr threads {stdout_thread} and {stderr_thread} to read command {self.command}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
            # Start the threads :
            stdout_thread.start()
            stderr_thread.start()
            # Write to log file :
            self.logger.write("ACTION", {"action":f"start stdout and stderr threads {stdout_thread} and {stderr_thread} to read command {self.command}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
            # Join both threads :
            stdout_thread.join()
            stderr_thread.join()
            # Write to log file :
            self.logger.write("ACTION", {"action":f"join stdout and stderr threads {stdout_thread} and {stderr_thread} to read command {self.command}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})

        # Start the main thread as a daemon to ensure proper closing :
        self.thread = threading.Thread(target = target)
        self.thread.daemon = True  # Make the thread a daemon
        # Write to log file :
        self.logger.write("ACTION", {"action":f"create thread {self.thread} to run command {self.command}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        self.thread.start()
        # Write to log file :
        self.logger.write("ACTION", {"action":f"start thread {self.thread} to run command {self.command}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})

    def stop(self):
        """
        Stop the command and the background thread
        """

        # Write to log file :
        self.logger.write("ACTION", {"action":f"stop command {self.command}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        
        # Terminate the subprocess:
        if self.process:
            self.process.terminate()
            self.process.wait()  # Wait for the process to terminate properly
            # Write to log file :
            self.logger.write("ACTION", {"action":f"terminate subprocess {self.process} to run command {self.command}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        
        # Trigger the stop event to stop the thread and join it :
        self.stop_event.set()
        # Write to log file :
        self.logger.write("EVENT", {"event":"set stop_event","triggered by":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
        
        # Join the thread :
        if self.thread and self.thread.is_alive():
            self.thread.join()
            # Write to log file :
            self.logger.write("ACTION", {"action":f"join thread {self.thread} that ran command {self.command}", "invoker":{"file":f"{os.path.basename(__file__)}", "instance":f"{self}", "called by":f"{inspect.stack()[1].function}"}, "output":"0"})
            
# Example usage :
if __name__ == "__main__":
    try:
        from LogWriter import LogWriter
        logger = LogWriter("log.txt")
        command_runner = CommandRunner("/bin/ping google.com", logger)
        command_runner.run()
        time.sleep(10)
        command_runner.stop()
    except CommandError as e:
        e.log()