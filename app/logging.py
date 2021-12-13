import logging

import requests


class CustomHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        log_entry = self.format(record)
        # url = 'http://127.0.0.1:8000/log'
        url = 'https://logs.wombatbau.de/log'
        response = requests.post(url, json={'identifier': "stef", 'payload': log_entry})
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

    http_handler = CustomHandler()
    http_handler.setLevel(logging.DEBUG)
    http_handler.setFormatter(formatter)

    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    logger.addHandler(http_handler)
    logger.info("Hello Propello")
