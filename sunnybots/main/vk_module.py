import requests
from django.http import HttpResponse, request

CONF = {
    'service_key' : '983f2be7983f2be7983f2be78e9b19482b9983f983f2be7ff62baa794815f9e7aaa713a'
}

class VkServiceApi:
    def __init__(self):
        self.service_key = CONF['service_key']
        self.api_base = 'https://api.vk.com/method/'
        self.v_api = 5.199

    def groupGet(self, group_id):
        post_data = {
            'group_id': group_id,
            'access_token': self.service_key,
            'v' :self.v_api
        }
        try:
            response = requests.post(self.api_base + 'groups.getById', data=post_data)
        except Exception as e:
            print('Error with request: ' + str(e))
        return response.json()