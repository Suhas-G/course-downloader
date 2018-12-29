import requests


class EdXDownloader(object):
    def __init__(self, configuration):
        self.configuration = configuration
        self.website_urls = self.configuration.get_website_urls("edX")
        self.session = requests.Session()
        self.session.headers = self.configuration.get_website_headers("edX")
        self.courses = {}

    def login(self, username, password):
        login_successful = False
        print(username, password, flush=True)
        login_request = self.session.get(self.website_urls["first_url"])
        if(login_request.status_code == 200):
            csrf_token = login_request.cookies["csrftoken"]
            login_request = self.session.post(self.website_urls["login_url"], data={
                                              "email": username, "password": password}, headers={"X-CSRFToken": csrf_token})
            if (login_request.status_code == 200):
                login_successful = True
            else:
                print(login_request.status_code, login_request.reason)
                print(login_request.text)

        return login_successful
