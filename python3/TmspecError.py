
class TmspecErrorContext:
    def __init__(self, line, column):
        # TODO: filename?
        self.line = line
        self.column = column

def parse_context_to_error_context(ctx):
    return TmspecErrorContext(ctx.start.line, ctx.start.column)

class TmspecError(Exception):
    def __init__(self, msg, ctx):
        self.msg = msg
        self.context = ctx
    def get_line(self):
        return self.context.line
    def get_column(self):
        return self.context.column

class TmspecErrorDuplicateIdentifier(TmspecError):
    pass

class TmspecErrorUnknownIdentifier(TmspecError):
    pass

class TmspecErrorNotAType(TmspecError):
    pass

class TmspecErrorConflictingTypes(TmspecError):
    pass

class TmspecErrorParseError(TmspecError):
    pass

