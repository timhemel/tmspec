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
            elif s[i] == 'b':
                r += '\b'
            elif s[i] == 'f':
                r += '\f'
            elif s[i] == 'n':
                r += '\n'
            elif s[i] == 'r':
                r += '\r'
            elif s[i] == 't':
                r += '\t'
            elif s[i] == 'u':
                codepoint = int(s[i+1:i+5],16)
                r += chr(codepoint)
                i += 4
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

def get_context_position(ctx):
    print(dir(ctx))
    return ctx.line, ctx.column

class TmspecModelVisitor(tmspecVisitor):

    def __init__(self):
        super(TmspecModelVisitor, self).__init__()
        self.model = TmspecModel()

    def visitStart(self, ctx):
        self.visitChildren(ctx)
        return self.model

    def visitZone(self, ctx):
        zone_name = ctx.identifier().getText()
        zone_ctx = parse_context_to_input_context(ctx)
        if self.model.has_identifier(zone_name):
            raise TmspecErrorDuplicateIdentifier(
                "identfier {} already in use.".format(zone_name),
                parse_context_to_input_context(ctx.identifier()))
        if ctx.attributes():
            attributes = dict(self.visitAttributes(ctx.attributes()))
        else:
            attributes = {}
        zone = TmZone(zone_name, zone_ctx, attributes)
        self.model.add_zone(zone)

    def visitTypedef(self, ctx):
        type_name, type_parents = self.visitNameAndType(ctx.name_and_type(), None)
        type_ctx = parse_context_to_input_context(ctx)
        if ctx.attributes():
            attributes = dict(self.visitAttributes(ctx.attributes()))
        else:
            attributes = {}
        new_type = TmType(type_name, type_ctx, type_parents, attributes)
        self.model.add_type(new_type)

    def visitComponent(self, ctx):
        component_name, component_types = self.visitNameAndType(ctx.name_and_type(), ['datastore', 'process', 'externalentity'])
        component_ctx = parse_context_to_input_context(ctx)
        if ctx.attributes():
            attributes = dict(self.visitAttributes(ctx.attributes()))
        else:
            attributes = {}
        component = TmComponent(component_name, component_ctx, component_types, attributes)
        try:
            component.get_attr('zone')
        except KeyError:
            raise TmspecErrorComponentWithoutZone("no zone defined for component {}".format(component.name), ctx.attributes())
        self.model.add_component(component)

    def _checkDataflowComponent(self, component, ctx):
        if not component:
            raise TmspecErrorUnknownIdentifier(
                "unknown identifier: {}".format(ctx.getText()),
                parse_context_to_input_context(ctx))
        base_types = [t.get_base_types() for t in component.get_types()]
        if 'dataflow' in base_types:
            raise TmspecErrorInvalidType(
                "element {} is not a dataflow instance"
                .format(ctx.getText()),
                parse_context_to_input_context(ctx))

    def visitFlow(self, ctx):
        name = ctx.identifier(0).getText()
        flow_ctx = parse_context_to_input_context(ctx)
        if self.model.has_identifier(name):
            raise TmspecErrorDuplicateIdentifier(
                "identifier {} already in use.".format(name),
                parse_context_to_input_context(ctx.identifier(0)))
        if ctx.typing() is not None:
            types = self.visitTyping(ctx.typing(), ['dataflow'])
        else:
            types = [self.model.get_identifier('dataflow')]
        component1 = self.model.get_identifier(ctx.identifier(1).getText())
        self._checkDataflowComponent(component1, ctx.identifier(1))
        component2 = self.model.get_identifier(ctx.identifier(2).getText())
        self._checkDataflowComponent(component2, ctx.identifier(2))
        # determine arrow direction
        if ctx.arrow().RARROW() is not None: # -->
            source = component1
            target = component2
        else:
            source = component2
            target = component1
        if ctx.attributes():
            attributes = self.visitAttributes(ctx.attributes())
        else:
            attributes = []
        flow = TmFlow(name, flow_ctx, source, target, types, dict(attributes))
        self.model.add_flow(flow)

    def visitNameAndType(self, ctx, type_restrictions):
        name = ctx.identifier().getText()
        if self.model.has_identifier(name):
            raise TmspecErrorDuplicateIdentifier(
                "identifier {} already in use.".format(name),
                parse_context_to_input_context(ctx.identifier()))
        types = self.visitTyping(ctx.typing(), type_restrictions)
        return (name, types)

    def visitTyping(self, ctx, type_restrictions):
        types = []
        base_types = set([])
        for c in ctx.identifier():
            obj = self.model.get_identifier(c.getText())
            if not obj:
                raise TmspecErrorUnknownIdentifier(
                    "unknown identifier: {}".format(c.getText()),
                    parse_context_to_input_context(c))
            if not isinstance(obj, TmType):
                raise TmspecErrorNotAType(
                    "{} is not a type".format(c.getText()),
                    parse_context_to_input_context(c))
            if len(base_types) == 0:
                base_types.update(obj.get_base_types())
                base_type = list(base_types)[0]
            else:
                base_type = list(base_types)[0]
                base_types.update(obj.get_base_types())
            if type_restrictions is not None and base_type not in type_restrictions:
                raise TmspecErrorInvalidType(
                    "type {} derived from {}, but must be derived from {}"
                    .format(c.getText(), base_type,
                        ", ".join(type_restrictions)),
                    parse_context_to_input_context(c))
            if len(base_types) > 1:
                raise TmspecErrorConflictingTypes(
                    "type {} conflicts with {}".format(c.getText(), base_type),
                    parse_context_to_input_context(c))
            types.append(obj)
        return types

    def visitAttributes(self, ctx):
        return [self.visitAttribute(c) for c in ctx.attribute()]

    def visitAttribute(self, ctx):
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
                raise TmspecErrorUnknownIdentifier(
                    "unknown identifier: {}".format(identifier),
                    parse_context_to_input_context(ctx.identifier()))
            return obj
        if ctx.QSTRING():
            return unquote_string(ctx.QSTRING().getText())
        if ctx.getText() == 'true':
            return True
        if ctx.getText() == 'false':
            return False
