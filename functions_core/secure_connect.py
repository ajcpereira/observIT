import fabric2
import logging
import tempfile
import random
import time

class Secure_Connect():
    def __init__(self, param_ip, bastion, user, host_keys):
        time.sleep(round(random.uniform(0.50, 14.99),2))
        logging.debug("Class Secure_connect Started")
        self.bastion = bastion

        if bastion:
            logging.debug("Class Secure_connect with bastion Started")

            cmd_pkey_bastion = "cat $HOME/.ssh/id_rsa"

            try:
                logging.debug("Values ip %s, bastion %s, user %s and host_keys %s" % (param_ip, bastion, user, host_keys))
                self.ssh_bastion = fabric2.Connection(host=str(bastion), user=user, port=22, connect_timeout=12, connect_kwargs={"key_filename": host_keys, "banner_timeout":12, "auth_timeout":12, "channel_timeout":12,})
                self.ssh_bastion.open()
                logging.debug("Got session for bastion")
            except Exception as msgerror:
                logging.error("Failed fabric2 - %s" % msgerror)
                if self.ssh:
                    self.ssh.close()

            try:
                logging.debug("Will get pkey")
                pkey_bastion = self.ssh_bastion.run(cmd_pkey_bastion, hide=True).stdout.strip()
                pkey_trunk = pkey_bastion[0:50]
                logging.debug("Got the pkey %s" % pkey_trunk)
            except Exception as msgerror:
                logging.error("Failed to get pkey form bastion - %s" % msgerror)
                if self.ssh_bastion:
                    self.ssh_bastion.close()

            # Write the private key contents to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, buffering=- 1) as f:
                f.write(pkey_bastion.encode())
                private_key_file = f.name
        
            logging.debug("Wrote the key in temp file")

            try:
                self.ssh = fabric2.Connection(host=str(param_ip), user=user, port=22, connect_timeout=12, connect_kwargs={"key_filename": private_key_file,"banner_timeout":12, "auth_timeout":12, "channel_timeout":12,}, gateway=self.ssh_bastion)
                logging.debug("Created ssh connection with hostname - %s - through bastion - %s" % (param_ip, bastion))
            except Exception as msgerror:
                logging.error("Class Secure_Connect with bastion FAILED - %s" % msgerror)
                if self.ssh:
                    self.ssh.close()

            try:
                logging.debug("will open session")
                self.ssh.open()
                logging.debug("Class Secure_connect open ok, will return session - %s" % self)
            except Exception as msgerror:
                logging.error("Class Secure_Connect with bastion FAILED - %s - for ip %s" % (msgerror, param_ip))
                if self.ssh:
                    self.ssh.close()

        else:
            logging.debug("Class Secure_connect without bastion Started")
            try:
                time.sleep(round(random.uniform(0.50, 14.99),2))
                self.ssh = fabric2.Connection(host=param_ip, user=user, port=22, connect_timeout=12, connect_kwargs={"key_filename": host_keys,"banner_timeout":12, "auth_timeout":12, "channel_timeout":12,})
                self.ssh.open()
                logging.debug("Class Secure_connect ended, will return session - %s - for ip %s" % (self,param_ip))
            except Exception as msgerror:
                logging.error("Class Secure FAILED - %s" % msgerror)
                if self.ssh:
                    self.ssh.close()
                 

    def ssh_run(self, cmd):
        try:
            stdout = self.ssh.run(cmd, hide=True, timeout=30)
            return stdout
        except Exception as msgerror:
            logging.error("Class Secure_Connect failed to exec cmd in function ssh_run %s" % msgerror)
            if self.ssh:
                self.ssh.close()
    
    def ssh_del(self):
         logging.debug("Will close ssh sessions on Class Secure_connect")
         self.ssh.close()
         del self.ssh
         logging.debug("Closed session on Class Secure_connect")
         if self.bastion:
            self.ssh_bastion.close()
            del self.ssh_bastion
            logging.debug("Closed bastion session on Class Secure_connect")