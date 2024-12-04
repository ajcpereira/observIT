import requests, logging, time, threading

# Will be used for a multi-thread environment to manage http connections
class HttpConnect:
    
    # Will keep track of http sessions, if parameters are the same will not open new, avoiding exhausting http sessions in servers
    active_sessions = []
    # Since this class will be used in a multi-thread environment to avoid race conditions we need to lock resources like the method manage_sessions() and the tuple active_sessions
    global_lock = threading.Lock()
    # After this time, sessions should be removed
    session_timeout=55 

    @staticmethod 
    def manage_sessions(session_key: list):
        timestamp_now = time.time()
        keep_sessions = []
        valid_session = None
        logging.debug(f"Managing HTTP sessions for session key: {session_key} with current active sessions {HttpConnect.active_sessions}")
        if not len(HttpConnect.active_sessions) == 0:
            logging.debug(f"Existing sessions are not empty {SshConnect.active_sessions}")
            for value in HttpConnect.active_sessions:
                if abs(timestamp_now - value[6]) <= HttpConnect.session_timeout:
                    logging.debug(f"Valid session found with session time {abs(timestamp_now - value[6])} for session {value}")
                    keep_sessions.append(value)
                    if session_key and value[:5] == session_key[:5]:
                        logging.debug(f"This is the instance to be returned {value[5]}")
                        valid_session = value[5]
                else:
                    logging.debug(f"Will close sessions not longer valid {value}")
                    invalid_session=value[5]
                    if hasattr(invalid_session,'http'):
                        invalid_session.http.close()
                        del invalid_session.ssh
                        logging.debug("Closed session on Class HttpConnect - %s" % invalid_session)
            HttpConnect.active_sessions = keep_sessions
            logging.debug(f"The active sessions are:\n{HttpConnect.active_sessions}")
            if valid_session:
                logging.debug(f"will pass session {valid_session}")
                return valid_session
        else:
            logging.debug(f"No HttpConnect.existing sessions found")
            return None

    def __init__(self, url, proxy, user, pwd64, unsecured):
        
        session_key = [url, proxy, user, pwd64, unsecured, self, time.time()]
        
        logging.debug(f"Session key: {session_key[:4]}")
        logging.debug(f"my existing sessions are {HttpConnect.active_sessions}")
        
        with HttpConnect.global_lock:
            ret_value = HttpConnect.manage_sessions(session_key)
            logging.debug(f"Returned value from function is {ret_value}")
            if ret_value:
                logging.debug(f"Will return value:{ret_value}")
                self.http = ret_value.http
            else:
                # No active sessions available will create
                logging.debug("Class HttpConnect Started - No value was returned so let's run all the process")
                self.proxy = proxy
                try:
                    self.http = requests.Session()
                    # Open connection with proxy
                    if proxy:
                        logging.debug("Class HttpConnect with proxy Started")
                        self.http.proxies.update(proxy)
                except Exception as msgerror:
                    logging.error("Failed to create HttpConnection - %s" % msgerror)
                    if hasattr(self,'http'):
                        self.http.close()
                        del self.http
                    del self
                    raise Exception(f"Failed open HttpConnection with msg: {msgerror}")    
                HttpConnect.active_sessions.append(session_key)

    def _create_new_session(self, base_url, headers):
        self.session = requests.Session()
        self.session.headers.update(headers or {})
        self.base_url = base_url
        logging.debug(f"Created new HTTP session for {self.base_url}")
    
    # (endpoint)
    def http_get(self, endpoint, params=None):
        with HttpConnect.global_lock:
            url = f"{self.base_url}{endpoint}"
            try:
                logging.debug(f"Performing GET request to {url} with params {params}")
                response = self.session.get(url, params=params)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logging.error(f"GET request failed: {e}")
                raise

    def http_post(self, endpoint, data=None, json=None):
        with HttpConnect.global_lock:
            url = f"{self.base_url}{endpoint}"
            try:
                logging.debug(f"Performing POST request to {url} with data {data} or json {json}")
                response = self.session.post(url, data=data, json=json)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logging.error(f"POST request failed: {e}")
                raise

    def http_delete(self, endpoint, data=None):
        with HttpConnect.global_lock:
            url = f"{self.base_url}{endpoint}"
            try:
                logging.debug(f"Performing DELETE request to {url} with data {data}")
                response = self.session.delete(url, data=data)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logging.error(f"DELETE request failed: {e}")
                raise

    def close(self):
        with HttpConnect.global_lock:
            logging.debug(f"Closing HTTP session for {self.base_url}")
            self.session.close()
            HttpConnect.manage_sessions(None)
