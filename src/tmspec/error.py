
class TmspecInputContext:
    def __init__(self, filename, line, column):
        self._filename = filename
        self._line = line
        self._column = column

    @property
    def position(self):
        return self._line, self._column

    @property
    def line(self):
        return self._line

    @property
    def column(self):
        return self._column

    @property
    def filename(self):
        return self._filename

def parse_context_to_input_context(filename, ctx):
    return TmspecInputContext(filename, ctx.start.line, ctx.start.column)

class TmspecError(Exception):
    def __init__(self, msg, ctx):
        self.msg = msg
        self._context = ctx

    @property
    def line(self):
        return self._context.line

    @property
    def column(self):
        return self._context.column

    def __str__(self):
        return "%s:%d:%d:ERROR %s" % (self._context.filename, self._context.line, self._context.column, self.msg)

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
