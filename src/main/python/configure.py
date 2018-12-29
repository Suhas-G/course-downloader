import json

from constants import CONFIG_FILE


class Configuration(object):
    def __init__(self, application_context):
        self.application_context = application_context
        with open(application_context.get_resource(CONFIG_FILE)) as file:
            self.data = json.load(file)

    def populate_website_chooser(self, combobox):
        websites = self.data["websites"]
        website_urls = {}
        for website in websites:
            combobox.addItem(website)
            website_urls[website] = websites[website]["urls"]["base_url"]

        return combobox, website_urls

    def get_website_urls(self, website_name):
        return self.data["websites"][website_name]["urls"]

    def get_website_headers(self, website_name):
        return self.data["websites"][website_name]["headers"]
