from typing import Any


class UnknownArgument(Exception):
    argument: Any
    
    def __init__(self, argument: Any):
        super().__init__()
        self.argument = argument
