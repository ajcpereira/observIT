import fabric2
import logging
import tempfile
import time
import threading

class Secure_Connect():
    existing_sessions = []
    global_lock = threading.Lock()

    @staticmethod 
    def manage_sessions(session_key: list):
        timestamp = time.time()
        keep_sessions = []
        valid_session = []
        logging.debug(f"Managing sessions for this session keys:{session_key} and this content for existing_sessions {Secure_Connect.existing_sessions}")

        if not len(Secure_Connect.existing_sessions) == 0:
            logging.debug(f"Existing sessions are not empty {Secure_Connect.existing_sessions}")
            for value in Secure_Connect.existing_sessions:
                if (timestamp - value[5]) <= 55:
                    logging.debug(f"Still a valid session with time below 55s {timestamp - value[5]}")
                    keep_sessions.append(value)
                    logging.debug(f"keeping session {value}")
                    if session_key:
                        logging.debug(f"The value is {value[:4]} and the session_key is {session_key[:4]} will check if they are equal")
                        if value[:4] == session_key[:4]:
                            logging.debug(f"This is the object to keep {value[4]}")
                            valid_session = value[4]
                            logging.debug(f"The object type for valid_session is {type(valid_session)}")
                else:
                    logging.debug(f"will close sessions not longer valid {value}")
                    mysession=value[4]
                    if hasattr(mysession,'ssh'):
                        mysession.ssh.close()
                        del mysession.ssh
                        logging.debug("Closed session on Class Secure_connect - %s" % mysession)
                    if hasattr(mysession, 'ssh_bastion'):
                        mysession.ssh_bastion.close()
                        del mysession.ssh_bastion
                        logging.debug("Closed bastion session on Class Secure_connect - %s" % mysession)
            Secure_Connect.existing_sessions = keep_sessions
            if valid_session:
                logging.debug(f"will pass session {valid_session}")
                return valid_session
        else:
            logging.debug(f"No Secure_Connect.existing sessions found")
            return None

    def __init__(self, param_ip, bastion, user, host_keys):

        session_key = [param_ip, bastion, user, host_keys, self, time.time()]

        logging.debug(f"my session_key is {session_key[:4]}")
        logging.debug(f"my existing sessions are {Secure_Connect.existing_sessions}")
        
        with Secure_Connect.global_lock:
            ret_value = Secure_Connect.manage_sessions(session_key)
            logging.debug(f"Returned value from function is {ret_value}")
            if ret_value:
                logging.debug(f"Will return value:{ret_value}")
                self.ssh = ret_value.ssh
            else:
                logging.debug("Class Secure_connect Started - No value was returned so let's run all the process")
                self.bastion = bastion
                if bastion:
                    logging.debug("Class Secure_connect with bastion Started")
                    cmd_pkey_bastion = "cat $HOME/.ssh/id_rsa"
                    # Open connection to bastion
                    try:
                        logging.debug("Values ip %s, bastion %s, user %s and host_keys %s" % (param_ip, bastion, user, host_keys))
                        self.ssh_bastion = fabric2.Connection(host=str(bastion), user=user, port=22, connect_timeout=12, connect_kwargs={"key_filename": host_keys, "banner_timeout":12, "auth_timeout":12, "channel_timeout":12,})
                        self.ssh_bastion.open()
                        logging.debug("Got session for bastion")
                    except Exception as msgerror:
                        logging.error("Failed fabric2 - %s" % msgerror)
                        if hasattr(self,'ssh'):
                            self.ssh.close()
                            del self.ssh
                        if hasattr(self, 'ssh_bastion'):
                            self.ssh_bastion.close()
                            del self.ssh_bastion
                        del self
                    # Get pkey on bastion
                    try:
                        logging.debug("Will get pkey")
                        pkey_bastion = self.ssh_bastion.run(cmd_pkey_bastion, hide=True).stdout.strip()
                        pkey_trunk = pkey_bastion[0:50]
                        logging.debug("Got the pkey %s" % pkey_trunk)
                    except Exception as msgerror:
                        logging.error("Failed to get pkey form bastion - %s" % msgerror)
                        if hasattr(self,'ssh'):
                            self.ssh.close()
                            del self.ssh
                        if hasattr(self, 'ssh_bastion'):
                            self.ssh_bastion.close()
                            del self.ssh_bastion
                        del self
                    # Write the private key contents to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, buffering=- 1) as f:
                        f.write(pkey_bastion.encode())
                        private_key_file = f.name
                    logging.debug("Wrote the key in temp file")
                    # connection to host using pkey
                    try:
                        self.ssh = fabric2.Connection(host=str(param_ip), user=user, port=22, connect_timeout=12, connect_kwargs={"key_filename": private_key_file,"banner_timeout":12, "auth_timeout":12, "channel_timeout":12,}, gateway=self.ssh_bastion)
                        logging.debug("Created ssh connection with hostname - %s - through bastion - %s" % (param_ip, bastion))
                    except Exception as msgerror:
                        logging.error("Class Secure_Connect with bastion FAILED - %s" % msgerror)
                        if hasattr(self,'ssh'):
                            self.ssh.close()
                            del self.ssh
                        if hasattr(self, 'ssh_bastion'):
                            self.ssh_bastion.close()
                            del self.ssh_bastion
                        del self
                    # open connection through bastion to host
                    try:
                        logging.debug("will open session")
                        self.ssh.open()
                        logging.debug("Class Secure_connect open ok with bastion, will return session - %s" % self)
                    except Exception as msgerror:
                        logging.error("Class Secure_Connect with bastion FAILED - %s - for ip %s" % (msgerror, param_ip))
                        if hasattr(self,'ssh'):
                            self.ssh.close()
                            del self.ssh
                        if hasattr(self, 'ssh_bastion'):
                            self.ssh_bastion.close()
                            del self.ssh_bastion
                        del self
                    Secure_Connect.existing_sessions.append(session_key)
                else:
                    logging.debug("Class Secure_connect without bastion Started")
                    try:
                        self.ssh = fabric2.Connection(host=param_ip, user=user, port=22, connect_timeout=12, connect_kwargs={"key_filename": host_keys,"banner_timeout":12, "auth_timeout":12, "channel_timeout":12,})
                        self.ssh.open()
                        logging.debug("Class Secure_connect open ok with bastion, will return session - %s" % self)
                    except Exception as msgerror:
                        logging.error("Class Secure FAILED - %s - for ip %s" % (msgerror, param_ip))
                        if hasattr(self,'ssh'):
                            self.ssh.close()
                            del self.ssh
                        del self
                    Secure_Connect.existing_sessions.append(session_key)
                     

    def ssh_run(self, cmd):
        try:
            logging.debug("Execute command with session %s" % self)
            stdout = self.ssh.run(cmd, hide=True, timeout=30, warn=True)
            return stdout
        except Exception as msgerror:
            logging.error("Class Secure_Connect failed to exec cmd in function ssh_run %s" % msgerror)
            if hasattr(self,'ssh'):
                self.ssh.close()
                del self.ssh
            if hasattr(self, 'ssh_bastion'):
                self.ssh_bastion.close()
                del self.ssh_bastion
            del self
    
    def ssh_del(self):
        with Secure_Connect.global_lock:
            Secure_Connect.manage_sessions(None)
