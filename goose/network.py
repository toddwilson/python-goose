import requests


def get_html(url, config):
    headers = {'User-Agent': config.browserUserAgent}
    response = requests.get(url, headers=headers)
    return response.text
