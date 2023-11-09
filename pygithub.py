import requests, json, base64, time
class GithubClient:
    def __init__(self, user, repo, token, version, base_url):
        self.user = user
        self.repo = repo
        self.token = token
        self.version = version
        self.base_url = base_url
        self.session = requests.Session()
        self.target_sha = None
        self.recipient_sha = None

    def request(self, url, data=None, method='get'):
        _headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer "+self.token,
            "X-GitHub-Api-Version": self.version
        }
        if method.lower() == 'put':
            try:
                response = self.session.put(url, headers=_headers, data=data)
            except Exception as e:
                print(" Error:",e)
                return {}
        else:
            try:
                response = self.session.get(url, headers=_headers, data=data)
            except Exception as e:
                print(" Error:",e)
                return {}
        try:
            data = json.loads(response.content)
        except Exception as e:
            print(" Error:",e)
            data = {}
        if response.ok:
            if data: return data
            return response.content
        else:
            error_message = data.get('message')
            if error_message: print(" error:",error_message)
            print(data)
        return {}

    def get_content(self, path):
        url = "{}/repos/{}/{}/contents/{}".format(self.base_url, self.user, self.repo, path)
        return self.request(url)

    def get_targets(self):
        response = self.get_content('targets')
        if response:
            self.target_sha = response['sha']
            content_decode = base64.b64decode(response['content']).decode()
            return [x.strip() for x in content_decode.splitlines() if x]
        return []

    def save_targets(self, content):
        data = {"message":str(int(time.time())),"content": base64.b64encode(content.encode()).decode(), "sha":self.target_sha}
        url = "{}/repos/{}/{}/contents/targets".format(self.base_url, self.user, self.repo)
        response = self.request(url, json.dumps(data), 'put')
        if response.get('sha'):
            self.target_sha = response['sha']

    def get_recipients(self):
        response = self.get_content('recipients')
        if response:
            self.recipient_sha = response['sha']
            content_decode = base64.b64decode(response['content']).decode()
            return [x.strip() for x in content_decode.splitlines() if x]
        return []
        
    def save_recipients(self, content):
        data = {"message":str(int(time.time())),"content": base64.b64encode(content.encode()).decode(), "sha":self.recipient_sha}
        url = "{}/repos/{}/{}/contents/recipients".format(self.base_url, self.user, self.repo)
        response = self.request(url, json.dumps(data), 'put')
        if response.get('sha'):
            self.recipient_sha = response['sha']






























#
