class AlertException(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message
