import logging
import requests
import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HttpConnect:
    def __init__(self, base_url, username, password, unsecured):
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.base_url = base_url
        if unsecured is True:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get(self, endpoint):
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url)
            response.raise_for_status()  # Raise an exception if status code indicates an error
            return response
        except requests.RequestException as e:
            logging.error(f"FUNC[{HttpConnect.get.__name__}]Error fetching data from {url}: {e}")
            return None

    def close(self):
        self.session.close()
