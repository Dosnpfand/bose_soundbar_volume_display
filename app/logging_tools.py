
import logging

import requests


class RestHandler(logging.Handler):
    def __init__(self, url, token):
        self.url = url
        self.token = token
        super().__init__()

    def emit(self, record):
        log_entry = self.format(record)
        response = requests.post(self.url, json={'identifier': self.token, 'payload': log_entry})
        print(response)
        return response


if __name__ == '__main__':
    # formatter = logging.Formatter(json.dumps({
    #     'time': '%(asctime)s',
    #     'pathname': '%(pathname)s',
    #     'line': '%(lineno)d',
    #     'logLevel': '%(levelname)s',
    #     'message': '%(message)s'
    # }))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    http_handler = RestHandler('https://logs.wombatbau.de/log', 'stef')
    http_handler.setLevel(logging.DEBUG)
    http_handler.setFormatter(formatter)

    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    logger.addHandler(http_handler)
    logger.info("Hello Propello")
