
class Job:
    def __init__(self):
        self.pipeline = []

    def add(self, component, *args, **kwargs):
        self.pipeline.append((component, args, kwargs))

    def exec(self):
        df = None
        i = 0
        for component, args, kwargs in self.pipeline:
            i += 1
            if i == 1:
                df = component(*args, **kwargs)
                self.data = df
                continue
            df = component(df, *args, **kwargs)
        return df
