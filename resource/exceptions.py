class InvalidRequestError(Exception):
    """
    Raised when checked a request with invalid parameters.

    Attributes:
        params -- which param is invalid
        place -- where did this error happen
        message -- which type this param should be
    """
    def __init__(self, params, place, message):
        self.params = params
        self.place = place
        self.message = message


class QnaireParserError(Exception):
    def __init__(self, message):
        self.message = message
