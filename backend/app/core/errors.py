import logging

logger = logging.getLogger("anonify.errors")

class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
        logger.error(f"ValidationError: {message}")



class ServiceError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
        logger.error(f"ServiceError: {message}")
