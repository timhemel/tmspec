from .tmspecVisitor import tmspecVisitor
from .TmspecModel import *
import logging

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
    return ctx.line, ctx.column

class TmspecModelVisitor(tmspecVisitor):

    def __init__(self, filename):
        super(TmspecModelVisitor, self).__init__()
        self.model = TmspecModel()
        self.filename = filename

    def visitStart(self, ctx):
        logging.debug('visitStart')
        self.visitChildren(ctx)
        return self.model

    def visitZone(self, ctx):
        logging.debug('visitZone')
        logging.debug('visitZone: identifier(0): %s', ctx.identifier().getText())
        zone_name = ctx.identifier().getText()
        zone_ctx = parse_context_to_input_context(self.filename, ctx)
        if self.model.has_identifier(zone_name):
            raise TmspecErrorDuplicateIdentifier(
                "identfier {} already in use.".format(zone_name),
                parse_context_to_input_context(self.filename, ctx.identifier()))
        if ctx.attributes():
            logging.debug('visitZone: has attributes')
            attributes = dict(self.visitAttributes(ctx.attributes()))
        else:
            logging.debug('visitZone: has no attributes')
            attributes = {}
        zone = TmZone(zone_name, zone_ctx, attributes)
        self.model.add_zone(zone)

    def visitTypedef(self, ctx):
        logging.debug('visitTypedef')
        type_name, type_parents = self.visitNameAndType(ctx.name_and_type(), None)
        type_ctx = parse_context_to_input_context(self.filename, ctx)
        if ctx.attributes():
            logging.debug('visitTypedef: has attributes')
            attributes = dict(self.visitAttributes(ctx.attributes()))
        else:
            logging.debug('visitTypedef: has no attributes')
            attributes = {}
        new_type = TmType(type_name, type_ctx, type_parents, attributes)
        self.model.add_type(new_type)

    def visitComponent(self, ctx):
        logging.debug('visitComponent')
        component_name, component_types = self.visitNameAndType(ctx.name_and_type(), ['datastore', 'process', 'externalentity'])
        component_ctx = parse_context_to_input_context(self.filename, ctx)
        if ctx.attributes():
            logging.debug('visitComponent: has attributes')
            attributes = dict(self.visitAttributes(ctx.attributes()))
        else:
            logging.debug('visitComponent: has no attributes')
            attributes = {}
        component = TmComponent(component_name, component_ctx, component_types, attributes)
        #try:
        #    component.get_attr('zone')
        #except KeyError:
        #    raise TmspecErrorComponentWithoutZone("no zone defined for component {}".format(component.name), ctx.attributes())
        self.model.add_component(component)

    def _checkDataflowComponent(self, component, ctx):
        if not component:
            raise TmspecErrorUnknownIdentifier(
                "unknown identifier: {}".format(ctx.getText()),
                parse_context_to_input_context(self.filename, ctx))
        if not isinstance(component, TmComponent):
            raise TmspecErrorInvalidType(
                "element {} is not a component instance"
                .format(ctx.getText()),
                parse_context_to_input_context(self.filename, ctx))
        base_types = [t.get_base_types() for t in component.get_types()]

    def visitFlow(self, ctx):
        logging.debug('visitFlow')
        logging.debug('visitFlow: identifier(0): %s', ctx.identifier(0).getText())
        name = ctx.identifier(0).getText()
        flow_ctx = parse_context_to_input_context(self.filename, ctx)
        if self.model.has_identifier(name):
            raise TmspecErrorDuplicateIdentifier(
                "identifier {} already in use.".format(name),
                parse_context_to_input_context(self.filename, ctx.identifier(0)))
        if ctx.typing() is not None:
            logging.debug('visitFlow: has explicit type')
            types = self.visitTyping(ctx.typing(), ['dataflow'])
        else:
            logging.debug('visitFlow: has implicit type')
            types = [self.model.get_identifier('dataflow')]
        component1 = self.model.get_identifier(ctx.identifier(1).getText())
        self._checkDataflowComponent(component1, ctx.identifier(1))
        component2 = self.model.get_identifier(ctx.identifier(2).getText())
        self._checkDataflowComponent(component2, ctx.identifier(2))
        # determine arrow direction
        if ctx.arrow().RARROW() is not None: # -->
            logging.debug('visitFlow: -->')
            source = component1
            target = component2
        else:
            logging.debug('visitFlow: <--')
            source = component2
            target = component1
        if ctx.attributes():
            logging.debug('visitFlow: has attributes')
            attributes = self.visitAttributes(ctx.attributes())
        else:
            logging.debug('visitFlow: no attributes')
            attributes = []
        flow = TmFlow(name, flow_ctx, source, target, types, dict(attributes))
        self.model.add_flow(flow)

    def visitNameAndType(self, ctx, type_restrictions):
        logging.debug('visitNameAndType')
        logging.debug('visitNameAndType: identifier: %s', ctx.identifier().getText())
        name = ctx.identifier().getText()
        if self.model.has_identifier(name):
            raise TmspecErrorDuplicateIdentifier(
                "identifier {} already in use.".format(name),
                parse_context_to_input_context(self.filename, ctx.identifier()))
        types = self.visitTyping(ctx.typing(), type_restrictions)
        return (name, types)

    def visitTyping(self, ctx, type_restrictions):
        logging.debug('visitTyping')
        types = []
        base_types = set([])
        for c in ctx.identifier():
            logging.debug('visitTyping: identifier: %s', c.getText())
            obj = self.model.get_identifier(c.getText())
            if not obj:
                raise TmspecErrorUnknownIdentifier(
                    "unknown identifier: {}".format(c.getText()),
                    parse_context_to_input_context(self.filename, c))
            if not isinstance(obj, TmType):
                raise TmspecErrorNotAType(
                    "{} is not a type".format(c.getText()),
                    parse_context_to_input_context(self.filename, c))
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
                    parse_context_to_input_context(self.filename, c))
            if len(base_types) > 1:
                raise TmspecErrorConflictingTypes(
                    "type {} conflicts with {}".format(c.getText(), base_type),
                    parse_context_to_input_context(self.filename, c))
            types.append(obj)
        return types

    def visitAttributes(self, ctx):
        logging.debug('visitAttributes')
        return [self.visitAttribute(c) for c in ctx.attribute()]

    def visitAttribute(self, ctx):
        logging.debug('visitAttribute')
        if ctx.identifier():
            logging.debug('visitAttribute: identifier: %s', ctx.identifier().getText())
            attr_name = ctx.identifier().getText()
        else:
            logging.debug('visitAttribute: QSTRING: %s', ctx.QSTRING().getText())
            attr_name = unquote_string(ctx.QSTRING().getText())
        if ctx.value():
            logging.debug('visitAttribute: value')
            attr_value = self.visitValue(ctx.value(), force_identifier_resolution=attr_name == 'zone')
        else:
            logging.debug('visitAttribute: \'true\'')
            attr_value = True
        return attr_name, attr_value

    def visitValue(self, ctx, force_identifier_resolution=False):
        logging.debug('visitValue: force_identifier_resolution=%s', force_identifier_resolution)
        if ctx.number():
            logging.debug('visitValue: number: %s', ctx.number().getText())
            return int(ctx.number().getText())
        if ctx.identifier():
            logging.debug('visitValue: identifier: %s', ctx.identifier().getText())
            identifier = ctx.identifier().getText()
            obj = self.model.get_identifier(identifier)
            if obj is None:
                if force_identifier_resolution:
                    raise TmspecErrorUnknownIdentifier(
                        "unknown identifier: {}".format(identifier),
                        parse_context_to_input_context(self.filename, ctx.identifier()))
                return identifier
            return obj
        if ctx.QSTRING():
            logging.debug('visitValue: QSTRING: %s', ctx.QSTRING().getText())
            return unquote_string(ctx.QSTRING().getText())
        if ctx.getText() == 'true':
            logging.debug('visitValue: \'true\'')
            return True
        if ctx.getText() == 'false':
            logging.debug('visitValue: \'false\'')
            return False
