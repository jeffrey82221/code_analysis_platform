import logging

def log_method(method):
    def wrapper(*args, **kwargs):
        logging.basicConfig(level=logging.INFO)
        logging.info("Calling method %s with arguments %s, %s" % (method.__name__, args, kwargs))
        result = method(*args, **kwargs)
        logging.info("Method %s returned %s" % (method.__name__, result))
        return result
    return wrapper

class MyClass:
    def __init__(self):
        self.value = 0

    @log_method
    def increment(self, amount):
        self.value += amount
        return self.value

my_obj = MyClass()
my_obj.increment(10)