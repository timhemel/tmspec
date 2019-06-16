
class TmspecError(Exception):
    def __init__(self, msg, ctx):
        self.msg = msg
        self.context = ctx
    pass

class TmspecErrorDuplicateIdentifier(TmspecError):
    pass

class TmspecErrorUnknownIdentifier(TmspecError):
    pass

class TmspecErrorNotAType(TmspecError):
    pass

class TmspecErrorConflictingTypes(TmspecError):
    pass
