import fabric2, logging, tempfile, time, threading, paramiko

# Will be used for a multi-thread environment to manage ssh connections
class Secure_Connect():

    # Will keep track of ssh sessions, if parameters are the same will not open new, avoiding exhausting ssh sessions in servers
    active_sessions = []
    # Since this class will be used in a multi-thread environment to avoid race conditions we need to lock resources like the method manage_sessions() and the tuple active_sessions
    global_lock = threading.Lock()

    @staticmethod 
    def manage_sessions(session_key: list):
        timestamp_now = time.time()
        keep_sessions = []
        valid_session = []
        logging.debug(f"Managing sessions for this session keys:{session_key} and this content for active_sessions {Secure_Connect.active_sessions}")
        if not len(Secure_Connect.active_sessions) == 0:
            logging.debug(f"Existing sessions are not empty {Secure_Connect.active_sessions}")
            for value in Secure_Connect.active_sessions:
                if abs(timestamp_now - value[5]) <= 55 and value[4].ssh.is_connected:
                    logging.debug(f"Still a valid session with time below 55s {abs(timestamp_now - value[5])} and is_connected for session {value}")
                    keep_sessions.append(value)
                    if session_key and value[:4] == session_key[:4]:
                        logging.debug(f"This is the instance to be returned {value[4]}")
                        valid_session = value[4]
                else:
                    logging.debug(f"Will close sessions not longer valid {value}")
                    invalid_session=value[4]
                    if hasattr(invalid_session, 'ssh_bastion'):
                        invalid_session.ssh_bastion.close()
                        del invalid_session.ssh_bastion
                        logging.debug("Closed bastion session on Class Secure_connect - %s" % invalid_session)
                    if hasattr(invalid_session,'ssh'):
                        invalid_session.ssh.close()
                        del invalid_session.ssh
                        logging.debug("Closed session on Class Secure_connect - %s" % invalid_session)
            Secure_Connect.active_sessions = keep_sessions
            logging.debug(f"The active sessions are:\n{Secure_Connect.active_sessions}")
            if valid_session:
                logging.debug(f"will pass session {valid_session}")
                return valid_session
        else:
            logging.debug(f"No Secure_Connect.existing sessions found")
            return None

    def __init__(self, param_ip, bastion, user, host_keys):

        session_key = [param_ip, bastion, user, host_keys, self, time.time()]

        logging.debug(f"my session_key is {session_key[:4]}")
        logging.debug(f"my existing sessions are {Secure_Connect.active_sessions}")
        
        with Secure_Connect.global_lock:
            ret_value = Secure_Connect.manage_sessions(session_key)
            logging.debug(f"Returned value from function is {ret_value}")
            if ret_value:
                logging.debug(f"Will return value:{ret_value}")
                self.ssh = ret_value.ssh
                if hasattr(ret_value, 'ssh_bastion'):
                        self.ssh_bastion = ret_value.ssh_bastion
            else:
                # No active sessions available will create
                logging.debug("Class Secure_connect Started - No value was returned so let's run all the process")
                self.bastion = bastion
                # Open connection with bastion
                if bastion:
                    logging.debug("Class Secure_connect with bastion Started")
                    cmd_pkey_bastion = "cat $HOME/.ssh/id_rsa"
                    # Open connection to bastion
                    try:

                        #Configure SSH options to support both legacy and modern systems.
                        paramiko.Transport._preferred_ciphers = (
                            'aes128-ctr', 'aes256-ctr',   # Modern ciphers
                            'aes128-cbc', 'aes256-cbc'    # Legacy CBC ciphers
                        )

                        #paramiko.Transport._preferred_kex = (
                        #    'diffie-hellman-group14-sha256',  # Modern SHA-256 DH
                        #    'ecdh-sha2-nistp256',             # Modern elliptic curve DH
                        #    'diffie-hellman-group14-sha1'     # Legacy SHA-1 DH
                        #)

                        paramiko.Transport._preferred_keys = (
                            'rsa-sha2-256', 'rsa-sha2-512',  # Modern RSA with SHA-2
                            'ssh-rsa'                        # Legacy RSA with SHA-1
                        )

                        logging.debug("Values ip %s, bastion %s, user %s and host_keys %s" % (param_ip, bastion, user, host_keys))
                        self.ssh_bastion = fabric2.Connection(
                            host=str(bastion), 
                            user=user, 
                            port=22, 
                            connect_timeout=12, 
                            connect_kwargs={
                                "key_filename": host_keys, 
                                "banner_timeout":12, 
                                "auth_timeout":12, 
                                "channel_timeout":12,
                                "reject_unknown_hosts": False,
                                }
                            )
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
                        raise Exception(f"Failed the connection to bastion srv with msg: {msgerror}")
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
                        raise Exception(f"Failed to get PKEY in bastion srv with msg: {msgerror}")
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
                        raise Exception(f"Failed the connection to srv through bastion with msg: {msgerror}")
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
                        raise Exception(f"Failed to open connection through bastion with msg: {msgerror}")
                    Secure_Connect.active_sessions.append(session_key)
                # open connection without bastion
                else:
                    logging.debug("Class Secure_connect without bastion Started")
                    try:
                        #Configure SSH options to support both legacy and modern systems.
                        paramiko.Transport._preferred_ciphers = (
                            'aes128-ctr', 'aes256-ctr',   # Modern ciphers
                            'aes128-cbc', 'aes256-cbc'    # Legacy CBC ciphers
                        )
                        
                        #paramiko.Transport._preferred_kex = (
                        #    'diffie-hellman-group14-sha256',  # Modern SHA-256 DH
                        #    'ecdh-sha2-nistp256',             # Modern elliptic curve DH
                        #    'diffie-hellman-group14-sha1'     # Legacy SHA-1 DH
                        #)
                        
                        paramiko.Transport._preferred_keys = (
                            'rsa-sha2-256', 'rsa-sha2-512',  # Modern RSA with SHA-2
                            'ssh-rsa'                        # Legacy RSA with SHA-1
                        )
                        
                        self.ssh = fabric2.Connection(
                            host=param_ip, 
                            user=user, 
                            port=22, 
                            connect_timeout=12, 
                            connect_kwargs=
                            {
                                "key_filename": host_keys,
                                "banner_timeout":12, 
                                "auth_timeout":12, 
                                "channel_timeout":12,
                                "reject_unknown_hosts": False,
                            }
                        )
                        self.ssh.open()
                        logging.debug("Class Secure_connect open ok with bastion, will return session - %s" % self)
                    except Exception as msgerror:
                        logging.error("Class Secure FAILED - %s - for ip %s" % (msgerror, param_ip))
                        if hasattr(self,'ssh'):
                            self.ssh.close()
                            del self.ssh
                        del self
                        raise Exception(f"Failed the connection for srv (no bastion) with msg: {msgerror}")
                    Secure_Connect.active_sessions.append(session_key)
                     

    def ssh_run(self, cmd):
        with Secure_Connect.global_lock:
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
                raise Exception(f"Failed the cmd execution with msg: {msgerror}")
                # after run the caller should call the ssh_del() method so we can check which connections are still valid
    def ssh_del(self):
        with Secure_Connect.global_lock:
            Secure_Connect.manage_sessions(None)