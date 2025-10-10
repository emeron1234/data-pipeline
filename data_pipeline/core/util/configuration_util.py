import functools

class SubparserBuilder:
    """
    Class as Decorator.

    When a function is decorated, it is added to `_decoratees`
    and can be enumerated later by the `decoratees()` function.
    Ref: https://realpython.com/primer-on-python-decorators/#classes-as-decorators

    ```python
        @SubparserBuilder
        def build_subparser(parser):
            subparsers = []
            ...
            return subparsers
    ```
    """

    # Keep track of the decorated functions
    _decoratees = set()

    def __init__(self, func):
        self._decoratees.add(func)
        functools.update_wrapper(self, func)
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    @classmethod
    def decoratees(cls):
        return list(cls._decoratees)