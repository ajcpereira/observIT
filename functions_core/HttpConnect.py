import requests, logging, time, threading

class HttpConnect:
    active_sessions = []
    global_lock = threading.Lock()

    @staticmethod 
    def manage_sessions(session_key: list, session_timeout=55):
        timestamp_now = time.time()
        keep_sessions = []
        valid_session = None
        logging.debug(f"Managing HTTP sessions for session key: {session_key} with current active sessions {HttpConnect.active_sessions}")

        for value in HttpConnect.active_sessions:
            if abs(timestamp_now - value[3]) <= session_timeout:
                logging.debug(f"Valid session found with session time {abs(timestamp_now - value[3])} for session {value}")
                keep_sessions.append(value)
                if session_key and value[:2] == session_key[:2]:
                    valid_session = value[2]
            else:
                logging.debug(f"Session expired or invalid: {value}")

        HttpConnect.active_sessions = keep_sessions
        return valid_session

    def __init__(self, base_url, headers=None):
        session_key = [base_url, headers, self, time.time()]
        logging.debug(f"Session key: {session_key[:2]}")

        with HttpConnect.global_lock:
            ret_value = HttpConnect.manage_sessions(session_key)
            if ret_value:
                self.session = ret_value.session
            else:
                self._create_new_session(base_url, headers)
                HttpConnect.active_sessions.append(session_key)

    def _create_new_session(self, base_url, headers):
        self.session = requests.Session()
        self.session.headers.update(headers or {})
        self.base_url = base_url
        logging.debug(f"Created new HTTP session for {self.base_url}")

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
