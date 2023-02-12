def handle_failure():
    def decorate(function):
        def applicator(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                print(f'Error was thrown in function {function.__name__}(): "{e}"')

        return applicator

    return decorate
