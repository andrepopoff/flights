def exc_handler(func):
    """
    Decorator function that handles exceptions
    """
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, OSError, TypeError, AttributeError, KeyError, IndexError, Exception, ValueError) as e:
            print('In func {}: {} {}'.format(func.__name__, e.__class__, e))
    return wrapped
