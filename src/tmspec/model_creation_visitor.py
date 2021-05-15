from .tmspecVisitor import tmspecVisitor
from .model import *
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
        self._check_unique_identifier(ctx.identifier())
        if ctx.attributes():
            logging.debug('visitZone: has attributes')
            attributes = dict(self.visitAttributes(ctx.attributes()))
        else:
            logging.debug('visitZone: has no attributes')
            attributes = {}
        zone_ctx = parse_context_to_input_context(self.filename, ctx)
        zone = TmZone(zone_name, zone_ctx, attributes)
        self.model.add_zone(zone)

    def visitTypedef(self, ctx):
        logging.debug('visitTypedef')
        type_name, type_parents = self.visitNameAndType(ctx.name_and_type(), None)
        if ctx.attributes():
            logging.debug('visitTypedef: has attributes')
            attributes = dict(self.visitAttributes(ctx.attributes()))
        else:
            logging.debug('visitTypedef: has no attributes')
            attributes = {}
        type_ctx = parse_context_to_input_context(self.filename, ctx)
        new_type = TmType(type_name, type_ctx, type_parents, attributes)
        self.model.add_type(new_type)

    def visitComponent(self, ctx):
        logging.debug('visitComponent')
        component_name, component_types = self.visitNameAndType(ctx.name_and_type(), ['datastore', 'process', 'externalentity'])
        if ctx.attributes():
            logging.debug('visitComponent: has attributes')
            attributes = dict(self.visitAttributes(ctx.attributes()))
        else:
            logging.debug('visitComponent: has no attributes')
            attributes = {}
        component_ctx = parse_context_to_input_context(self.filename, ctx)
        component = TmComponent(component_name, component_ctx, component_types, attributes)
        self.model.add_component(component)

    def visitFlow(self, ctx):
        logging.debug('visitFlow')
        logging.debug('visitFlow: identifier(0): %s', ctx.identifier(0).getText())
        name = ctx.identifier(0).getText()
        self._check_unique_identifier(ctx.identifier(0))
        if ctx.typing() is not None:
            logging.debug('visitFlow: has explicit type')
            types = self.visitTyping(ctx.typing(), ['dataflow'])
        else:
            logging.debug('visitFlow: has implicit type')
            types = [self.model.get_identifier('dataflow')]
        component1 = self._resolve_object(ctx.identifier(1))
        component1 = self._as_component(component1)
        component2 = self._resolve_object(ctx.identifier(2))
        component2 = self._as_component(component2)
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
            attributes = dict(self.visitAttributes(ctx.attributes()))
        else:
            logging.debug('visitFlow: no attributes')
            attributes = {}
        flow_ctx = parse_context_to_input_context(self.filename, ctx)
        flow = TmFlow(name, flow_ctx, source, target, types, attributes)
        self.model.add_flow(flow)

    def visitNameAndType(self, ctx, type_restrictions):
        logging.debug('visitNameAndType')
        logging.debug('visitNameAndType: identifier: %s', ctx.identifier().getText())
        name = ctx.identifier().getText()
        self._check_unique_identifier(ctx.identifier())
        types = self.visitTyping(ctx.typing(), type_restrictions)
        return (name, types)

    def _check_unique_identifier(self, identifier):
        name = identifier.getText()
        if self.model.has_identifier(name):
            raise TmspecErrorDuplicateIdentifier(f'identifier {name} already in use.',
                parse_context_to_input_context(self.filename, identifier))

    def _resolve_object(self, identifier, force_identifier_resolution = False):
        obj = self.model.get_identifier(identifier.getText())
        if obj is None:
            if force_identifier_resolution:
                raise TmspecErrorUnknownIdentifier(
                    f'unknown identifier: {identifier.getText()}',
                    parse_context_to_input_context(self.filename, identifier))
            return identifier.getText()
        return obj

    def _as_type(self, obj):
        if not isinstance(obj, TmType):
            raise TmspecErrorNotAType(f'{obj.name} is not a type', obj.input_ctx)
        return obj

    def _as_component(self, obj):
        if not isinstance(obj, TmComponent):
            raise TmspecErrorInvalidType(
                f'element {obj.name} is not a component instance', obj.input_ctx)
        return obj

    def visitTyping(self, ctx, type_restrictions):
        logging.debug('visitTyping')
        types = []
        base_types = set()
        for c in ctx.identifier():
            logging.debug('visitTyping: identifier: %s', c.getText())
            obj = self._resolve_object(c, True)
            obj = self._as_type(obj)
            if len(base_types) == 0:
                base_types.update(obj.base_types)
                base_type = list(base_types)[0]
            else:
                base_type = list(base_types)[0]
                base_types.update(obj.base_types)
            if type_restrictions is not None and base_type not in type_restrictions:
                raise TmspecErrorInvalidType(
                    f'type {obj.name} derived from {base_type}, but must be derived from {", ".join(type_restrictions)}',
                    obj.input_ctx)
            if len(base_types) > 1:
                raise TmspecErrorConflictingTypes(
                    f'type {obj.name} conflicts with {base_type}', obj.input_ctx)
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
            return self._resolve_object(ctx.identifier(), force_identifier_resolution)
        if ctx.QSTRING():
            logging.debug('visitValue: QSTRING: %s', ctx.QSTRING().getText())
            return unquote_string(ctx.QSTRING().getText())
        if ctx.getText() == 'true':
            logging.debug('visitValue: \'true\'')
            return True
        if ctx.getText() == 'false':
            logging.debug('visitValue: \'false\'')
            return False
