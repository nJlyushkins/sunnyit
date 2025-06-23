import requests

class VkServiceApi:
    def __init__(self):
        self.api_version = "5.199"
        self.base_url = "https://api.vk.com/method/"
        self.default_token = "vk1.a.MU-ccGdPVTQBG1PG7jsf41YF1qySzw_wuMlO3WAAoTREqq1fFSDF0Ur2PaqJbYCbnyW_3UFQKJafVixAZL8EdU7APTvJNr73zsbQ2p3kBbhULj6EpfFp9eUU73K2mVULFO6U9zmWmC1VojpxcScOB46O-ZKck9Q4kr7EgxDqep4_S0KaBEXeKYtzB5RnPZjyl0JxSgBx2sH6tPovZQ0GxQ"

    def groupGet(self, group_id, access_token=None):
        params = {
            "group_id": group_id,
            "v": self.api_version,
            "access_token": access_token if access_token else self.default_token
        }
        response = requests.get(f"{self.base_url}groups.getById", params=params)
        return response.json()

    def addCallbackServer(self, group_id, access_token, url, title, secret_key):
        params = {
            "group_id": group_id,
            "url": url,
            "title": title,
            "secret_key": secret_key,
            "access_token": access_token,
            "v": self.api_version
        }
        response = requests.get(f"{self.base_url}groups.addCallbackServer", params=params)
        return response.json()

    def getCallbackServers(self, group_id, access_token):
        params = {
            "group_id": group_id,
            "access_token": access_token,
            "v": self.api_version
        }
        response = requests.get(f"{self.base_url}groups.getCallbackServers", params=params)
        return response.json()

    def getCallbackConfirmationCode(self, group_id, access_token):
        params = {
            "group_id": group_id,
            "access_token": access_token,
            "v": self.api_version
        }
        response = requests.get(f"{self.base_url}groups.getCallbackConfirmationCode", params=params)
        return response.json()

class VkTokenValidator:
    def validate_token(self, group_id, access_token):
        vk_api = VkServiceApi()
        response = vk_api.getCallbackServers(group_id, access_token)
        if(not "error" in response):
            return True, "Token is valid"
        else:
            return False, "Error is happened: " + response.json