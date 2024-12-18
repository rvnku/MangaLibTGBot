class ApiException(Exception):
    type: str
    message: str

    def __init__(self, type: str, message: str) -> None:
        super().__init__()
        self.type = type
        self.message = message
