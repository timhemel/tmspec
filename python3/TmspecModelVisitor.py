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
        self.model.add_zone(zone_name)

    def visitComponent(self, ctx):
        # self.visitChildren(ctx)
        component_name, component_types = self.visitNameAndType(ctx.name_and_type())
        if ctx.attributes():
            attributes = self.visitAttributes(ctx.attributes())
        else:
            attributes = []
        self.model.add_component(component_name, component_types, attributes)

    def visitNameAndType(self, ctx):
        self.visitChildren(ctx)
        name = ctx.identifier().getText()
        types = self.visitTyping(ctx.typing())
        return (name, types)

    def visitTyping(self, ctx):
        types = [ self.model.get_identifier(c.getText()) for c in ctx.identifier() ]
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
            return self.model.get_identifier(identifier)
        if ctx.QSTRING():
            return unquote_string(ctx.QSTRING().getText())
        if ctx.getText() == 'true':
            return True
        if ctx.getText() == 'false':
            return False
