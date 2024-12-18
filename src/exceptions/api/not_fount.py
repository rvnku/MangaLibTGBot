from . import ApiException


class NotFoundError(ApiException):
    def __init__(self, type: str):
        super().__init__(type, 'Not Found')
