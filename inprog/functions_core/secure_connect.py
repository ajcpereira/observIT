import fabric2
import logging
import tempfile

class Secure_Connect():
    def __init__(self, param_ip, bastion, user, host_keys):
        
        logging.debug("Class Secure_connect Started")

        if bastion:
            logging.debug("Class Secure_connect with bastion Started")

            cmd_pkey_bastion = "cat $HOME/.ssh/id_rsa"
            try:
                ssh_bastion = fabric2.Connection(host=bastion, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})

                logging.debug("Created ssh connection with bastion with session %s" % self)
                pkey_bastion = self.ssh.run(cmd_pkey_bastion, hide=True).stdout.strip()
                logging.debug("Got the key to make ssh to the host")

                # Write the private key contents to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, buffering=- 1) as f:
                    f.write(pkey_bastion.encode())
                    private_key_file = f.name
            
                logging.debug("Wrote the key in temp file")
                self.ssh = fabric2.Connection(param_ip, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": private_key_file,}, gateway=ssh_bastion)
                logging.debug("Created ssh connection with hostname - %s - through bastion - %s" % (param_ip, bastion))

                self.ssh.open()

                logging.debug("Class Secure_connect ended, will return session - %s" % self)

            except Exception as msgerror:
               logging.error("Class Secure_Connect FAILED - %s" % msgerror)

        else:
            logging.debug("Class Secure_connect without bastion Started")
            try:
                self.ssh = fabric2.Connection(host=param_ip, user=user, port=22, connect_timeout=10, connect_kwargs={"key_filename": host_keys,})

                self.ssh.open()
                
                logging.debug("Class Secure_connect ended, will return session - %s" % self)
                
            except Exception as msgerror:
                 logging.error("Class Secure FAILED - %s" % msgerror)

    def ssh_run(self, cmd):
         stdout = self.ssh.run(cmd)
         return stdout
    def ssh_del(self):
         print(self)
         self.ssh.close()