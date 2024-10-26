import keyring
from argon2 import PasswordHasher
import inspect
import os

class Encrypter:
  """
  Handle sudo passwords by hashing them through Argon2 (with parameters adaptated from machine specs) and safely storing the through keyring
  """
  def __init__(self, logger):
    # Initialize logger and PasswordHasher :
    self.logger = logger
    self.ph = PasswordHasher()
    # Write to log file :
    self.logger.write("ACTION", {"action":"initialize Encrypter instance", "invoker":f"file : {os.path.basename(__file__)}\ninstance : {self}\ncalled by : {inspect.stack()[1].function}", "output":"0"})

  def adjust_argon2_parameters(self):
    """
    Retrieve system specifications and user parameters (maximum values allowed) to adjust Argon2 parameters dynamically
    """

    # Get system specifications :
    cpu_cores = psutil.cpu_count(logical = False)  # Number of cpu physical cores
    total_memory = psutil.virtual_memory().total // (1024 * 1024)  # Memory ammount in MB
    cpu_freq = psutil.cpu_freq().current  # Current CPU frequency in MHz

    # Get user parameters from config.json :
    with open("config.json") as config_file:
      config = json.load(config_file)
    memory_cost_cap = config["hash_parameters"]["memory_cost_cap"]
    time_cost_cap = config["hash_parameters"]["time_cost_cap"]
    parallelism_cost_cap = config["hash_parameters"]["parallelism_cost_cap"]

    # Adjust Argon2 parameters :
    # Get the best system parameters, but do not exceed user cap (which is defined if different than 0)

    # Memory cost : 100MB by default, 4+GB RAM -> 250MB, 8+GB RAM-> 500MB
    system_based_memory_cost = 512000 if total_memory > 8192 else (256000 if total_memory > 4096 else 102400)
    memory_cost = min(system_based_memory_cost, memory_cost_cap) if memory_cost_cap else system_based_memory_cost
    # Time cost : 1 iteration by default, frequency>1500GHz -> 2, frequency>2500GHz -> 3
    system_based_time_cost = 3 if cpu_freq > 2500 else (2 if cpu_freq > 1500 else 1)
    time_cost = min(system_based_time_cost, time_cost_cap) if time_cost_cap else system_based_time_cost
    # Parralelism : at most 8 threads, but not more than the system has
    parallelism = min(min(cpu_cores, 8), parallelism_cost_cap) if parallelism_cost_cap else min(cpu_cores, 8)

    # Update hasher :
    self.ph = PasswordHasher(time_cost = time_cost, memory_cost = memory_cost, parallelism = parallelism)
    # Write to log file :
    logger.write("ACTION", {"action":"adjust Argon2 parameters to machine specs", "invoker":f"file : {os.path.basename(__file__)}\n    instance : {self}\n    called by : {inspect.stack()[1].function}", "output":"0"})

  def encrypt_password(self, password):
    """
    Encrypt the password using Argon2 hashing and store it through keyring
    """
    self.adjust_argon2_parameters()
    hashed_password = self.ph.hash(password)
    keyring.set_password("system", "sudo_hashed", "hashed_password")
    # Write to log file :
    logger.write("ACTION", {"action":"hash and encrypt sudo password", "invoker":f"file : {os.path.basename(__file__)}\n    instance : {self}\n    called by : {inspect.stack()[1].function}", "output":"0"})

  def check_password(self, checked_password):
    """
    Check if the provided password is correct
    """
    hashed_password = keyring.get_password("system", "sudo_hashed")
    is_valid = self.ph.verify(hashed_password, checked_password)
    # Write to log file :
    logger.write("ACTION", {"action":"check if provided sudo password is valid", "invoker":f"file : {os.path.basename(__file__)}\n    instance : {self}\n    called by : {inspect.stack()[1].function}", "output":str(is_valid)})
    return is_valid