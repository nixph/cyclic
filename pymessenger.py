import requests
class MessengerClient:
    def __init__(self, token, page_id, graph_version):
        self.token = token
        self.page_id = page_id
        self.graph_version = graph_version
        self.session = requests.Session()

    def send_message(self, _id, _message):
        url = "https://graph.facebook.com/{}/{}/messages".format(self.graph_version,self.page_id)
        data = {
            'recipient':{'id':_id},
            'messaging_type':'RESPONSE',
            'message':{'text':_message},
            'access_token':self.token
        }
        try:
            response = self.session.post(url, json=data)
            if response.ok: return True
        except Exception as e:
            print(" Error Sending Message:",e)
