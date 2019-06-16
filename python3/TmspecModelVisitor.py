from tmspecVisitor import tmspecVisitor
from TmspecModel import *

def unquote_string(s):
    i = 1
    r = ""
    quoted = False
    while i < len(s) - 1:
        if quoted:
            if s[i] == '\'' or s[i] == '\\':
                r += s[i]
            else:
                r += '\\' + s[i]
            quoted = False
        else: # not quoted
            if s[i] == '\\':
                quoted = True
            else:
                r += s[i]
        i += 1
    return r

class TmspecModelVisitor(tmspecVisitor):

    def __init__(self):
        self.model = TmspecModel()

    def visitStart(self, ctx):
        self.visitChildren(ctx)
        return self.model

    def visitZone(self, ctx):
        zone_name = ctx.identifier().getText()
        if self.model.has_identifier(zone_name):
            raise TmspecErrorDuplicateIdentifier("identfier {} already in use.".format(zone_name), parse_context_to_error_context(ctx.identifier()))
        zone = TmZone(zone_name)
        self.model.add_zone(zone)

    def visitComponent(self, ctx):
        component_name, component_types = self.visitNameAndType(ctx.name_and_type())
        if ctx.attributes():
            attributes = self.visitAttributes(ctx.attributes())
        else:
            attributes = []
        component = TmComponent(component_name, component_types, dict(attributes))
        self.model.add_component(component)

    def visitNameAndType(self, ctx):
        name = ctx.identifier().getText()
        if self.model.has_identifier(name):
            raise TmspecErrorDuplicateIdentifier("identifier {} already in use.".format(name), parse_context_to_error_context(ctx.identifier()))
        types = self.visitTyping(ctx.typing())
        return (name, types)

    def visitTyping(self, ctx):
        types = []
        base_types = set([])
        for c in ctx.identifier():
            obj = self.model.get_identifier(c.getText())
            if not obj:
                raise TmspecErrorUnknownIdentifier("unknown identifier: {}".format(c.getText()), parse_context_to_error_context(c))
            if not isinstance(obj, TmType):
                raise TmspecErrorNotAType("{} is not a type".format(c.getText()), parse_context_to_error_context(c))
            if len(base_types) == 0:
                base_types.update(obj.get_base_types())
                base_type = list(base_types)[0]
            else:
                base_type = list(base_types)[0]
                base_types.update(obj.get_base_types())
            if len(base_types) > 1:
                raise TmspecErrorConflictingTypes("type {} conflicts with {}".format(c.getText(), base_type), parse_context_to_error_context(c))
            types.append(obj)
        return types

    def visitAttributes(self, ctx):
        return [ self.visitAttribute(c) for c in ctx.attribute() ]

    def visitAttribute(self,ctx):
        attr_name = ctx.identifier().getText()
        if ctx.value():
            attr_value = self.visitValue(ctx.value())
        else:
            attr_value = True
        return attr_name, attr_value

    def visitValue(self, ctx):
        if ctx.number():
            return int(ctx.number().getText())
        if ctx.identifier():
            identifier = ctx.identifier().getText()
            obj = self.model.get_identifier(identifier)
            if obj is None:
                raise TmspecErrorUnknownIdentifier("unknown identifier: {}".format(identifier), parse_context_to_error_context(ctx.identifier()))
            return obj
        if ctx.QSTRING():
            return unquote_string(ctx.QSTRING().getText())
        if ctx.getText() == 'true':
            return True
        if ctx.getText() == 'false':
            return False
