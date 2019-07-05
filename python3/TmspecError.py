
class TmspecInputContext:
    def __init__(self, line, column):
        # TODO: filename?
        self.line = line
        self.column = column
    def get_position(self):
        return self.line, self.column

def parse_context_to_input_context(ctx):
    return TmspecInputContext(ctx.start.line, ctx.start.column)

class TmspecError(Exception):
    def __init__(self, msg, ctx):
        self.msg = msg
        self.context = ctx
    def get_line(self):
        return self.context.line
    def get_column(self):
        return self.context.column

    def __str__(self):
        return "ERROR:%d:%d:%s" % (self.context.line, self.context.column, self.msg)

class TmspecErrorDuplicateIdentifier(TmspecError):
    pass

class TmspecErrorUnknownIdentifier(TmspecError):
    pass

class TmspecErrorNotAType(TmspecError):
    pass

class TmspecErrorConflictingTypes(TmspecError):
    pass

class TmspecErrorInvalidType(TmspecError):
    pass

class TmspecErrorParseError(TmspecError):
    pass

class TmspecErrorComponentWithoutZone(TmspecError):
    pass
