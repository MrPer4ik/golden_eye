from api import _Api


class Api(_Api):
    def __init__(self):
        super().__init__('TestApi')

    def _update_rate(self, xrate):
        xrate.rate += 0.01
        return xrate.rate
