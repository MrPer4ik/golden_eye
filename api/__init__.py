import traceback
import importlib

import requests

from config import logging, HTTP_TIMEOUT, LOGGING

from models import XRate, peewee_datetime, ApiLog, ErrorLog

logging.config.dictConfig(LOGGING)


def update_rate(from_currency, to_currency):
    xrate = XRate.select().where(XRate.from_currency == from_currency,
                                 XRate.to_currency == to_currency).first()

    module = importlib.import_module(f"api.{xrate.module}")
    module.Api().update_rate(xrate)


class _Api:
    def __init__(self, logger_name):
        self.log = logging.getLogger("Api")
        self.log.name = logger_name

    def update_rate(self, xrate):
        self.log.info("Started update for: %s" % xrate)
        self.log.debug("rate before: %s", xrate)
        xrate.rate = self._update_rate(xrate)
        xrate.updated = peewee_datetime.datetime.now()
        xrate.save()

        self.log.debug("rate after: %s", xrate)
        self.log.info("Finished update for: %s" % xrate)

    def _update_rate(self, xrate):
        raise NotImplementedError("_update_rate")

    def _send_request(self, url, method, data=None, headers=None):
        log = ApiLog(request_url=url, request_data=data, request_method=method,
                     request_headers=headers)
        try:
            response = self._send(method=method, url=url, headers=headers, data=data)
            log.response_text = response.text
            return response
        except Exception as ex:
            self.log.exception("Error during request sending")
            log.error = str(ex)
            ErrorLog.create(request_data=data, request_url=url, request_method=method,
                            error=str(ex), traceback=traceback.format_exc(chain=False))
            raise
        finally:
            log.finished = peewee_datetime.datetime.now()
            log.save()

    def _send(self, url, method, data=None, headers=None):
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Language": "en-US,en;q=0.5",
                   "Accept-Encoding": "gzip, deflate",
                   "DNT": "1",
                   "Connection": "close",
                   "Upgrade-Insecure-Requests": "1"}
        return requests.request(method=method, url=url, headers=headers, data=data, timeout=HTTP_TIMEOUT)
