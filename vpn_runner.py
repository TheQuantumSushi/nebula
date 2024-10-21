import subprocess

class VPNRunner:
    def __init__(self, address):
        self.sudo_password = keyring.get_password("system", "sudo")
        self.address = address
        self.process = None

    def run_openvpn(self, address):
        config_file = f'/etc/openvpn/{address}'
        try:
            command = ['echo', self.sudo_password, '|', '/bin/sudo', '-S', 'openvpn', '--config', config_file]
            self.process = subprocess.Popen(command, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
            while True:
                output = self.process.stdout.readline()
                error = self.process.stderr.readline()
                if output == '' and error == '' and self.process.poll() is not None:
                    break
                if output:
                    print(f"OUTPUT: {output.strip()}")
                if error:
                    print(f"ERROR: {error.strip()}")
        except Exception as e:
            print(f"Exception: {e}")
        finally:
            if self.process:
                self.process.stdout.close()
                self.process.stderr.close()
                self.process.wait()

    def kill_process(self):
        if self.process:
            self.process.kill()
            print("Process killed successfully")
