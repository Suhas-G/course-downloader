import json

from constants import CONFIG_FILE


class Configuration(object):
    def __init__(self, application_context):
        """Configuration Object so that it doesnt read from file everywhere
        
        Arguments:
            application_context {ApplicationContext} -- Reference to application context
        """
        self.application_context = application_context
        with open(application_context.get_resource(CONFIG_FILE)) as file:
            self.data = json.load(file)

    def populate_website_chooser(self, combobox):
        """Util method to populate the UI website dropdown
        
        Arguments:
            combobox {QComboBox} -- The UI dropdown to use to add the websites to
        """
        websites = self.data["websites"]
        website_urls = {}
        for website in websites:
            combobox.addItem(website)
            website_urls[website] = websites[website]["urls"]["base_url"]

        return combobox, website_urls

    def get_website_urls(self, website_name):
        """Get all the urls for a website present in configuration
        
        Arguments:
            website_name {str} -- Name of the website
        """
        return self.data["websites"][website_name]["urls"]

    def get_website_headers(self, website_name):
        """Get header information for the websites.
        
        Arguments:
            website_name {str} -- Name of the website
        """
        return self.data["websites"][website_name]["headers"]
