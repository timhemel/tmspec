
class TmspecError(Exception):
    def __init__(self, msg, ctx):
        self.msg = msg
        self.context = ctx
    def get_line(self):
        return self.context.start.line
    def get_column(self):
        return self.context.start.column

class TmspecErrorDuplicateIdentifier(TmspecError):
    pass

class TmspecErrorUnknownIdentifier(TmspecError):
    pass

class TmspecErrorNotAType(TmspecError):
    pass

class TmspecErrorConflictingTypes(TmspecError):
    pass
