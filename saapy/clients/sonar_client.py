import requests


class SonarClient:
    def __init__(self, sonar_url, auth_token):
        self.sonar_url = sonar_url
        self.auth_token = auth_token

    def get(self, api_path, params={}, pages=1):
        url = "{0}/{1}".format(self.sonar_url, api_path)
        auth = (self.auth_token, "")
        r = requests.get(url, params=params, auth=auth, verify=False)
        return r.json()
