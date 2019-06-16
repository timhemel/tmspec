from TmspecError import *

class TmElement:
    def __init__(self, name):
        self.name = name

class TmComponent(TmElement):
    def __init__(self, name, types, attrs = {}):
        self.name = name
        self.types = types
        self.attr = attrs

class TmType(TmElement):
    def __init__(self, name, parents = [], attrs = {}):
        self.name = name
        self.parents = parents
        self.attrs = attrs
    def get_base_types(self):
        if self.parents:
            base_types = set([])
            for t in self.parents:
                base_types.update(t.get_base_types())
            return base_types
        else:
            return set([self.name])

class TmZone(TmElement):
    pass

class TmspecModel:

    def __init__(self):
        self.zones = set([])
        self.components = {}
        self.identifiers = {
                'process' : TmType('process'),
                'datastore' : TmType('datastore'),
                'dataflow' : TmType('dataflow'),
                'externalentity' : TmType('externalentity'),
        }

    def has_identifier(self, identifier):
        return identifier in self.identifiers

    def get_identifier(self, identifier):
        try:
            return self.identifiers[identifier]
        except KeyError:
            raise TmspecErrorUnknownIdentifier("unknown identifier: {}".format(identifier))

    def is_type(self, obj):
        return isinstance(obj, TmType)

    def add_zone(self, zone):
        self.zones.add(zone)
        self.identifiers[zone.name] = zone

    def add_component(self, component_name, component_types, attributes):
        if component_name in self.identifiers:
            raise TmspecErrorDuplicateIdentifier("identifier {} already in use."
                            .format(component_name))
        for t in component_types:
            if not self.is_type(t):
                raise TmspecErrorNotAType("identifier {} is not a type.", t.name)
        base_types = set([])
        for t in component_types:
            base_types.update(t.get_base_types())
        if len(base_types) != 1:
            raise TmspecErrorConflictingTypes("conflicting types")
        component = TmComponent(component_name, component_types, dict(attributes))
        self.components[component_name] = component

