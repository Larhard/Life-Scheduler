class SourceWrapper:
    def __init__(self, source, **kwargs):
        self.source = source

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def pull(self):
        raise NotImplementedError()
