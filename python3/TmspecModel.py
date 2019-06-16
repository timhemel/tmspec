from TmspecError import *

class TmElement:
    def __init__(self, name):
        self.name = name

class TmComponent:
    def __init__(self, name, types, attrs = {}):
        self.name = name
        self.types = types
        self.attr = attrs

class TmType(TmElement):
    pass

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

    def get_identifier(self, identifier):
        try:
            return self.identifiers[identifier]
        except KeyError:
            raise TmspecErrorUnknownIdentifier

    def is_type(self, obj):
        return isinstance(obj, TmType)

    def add_zone(self, zone_name):
        if zone_name in self.identifiers:
            raise TmspecErrorDuplicateIdentifier("identifier {} already in use."
                            .format(zone_name))
        zone = TmZone(zone_name)
        self.zones.add(zone)
        self.identifiers[zone_name] = zone

    def add_component(self, component_name, component_types, attributes):
        if component_name in self.identifiers:
            raise TmspecErrorDuplicateIdentifier("identifier {} already in use."
                            .format(component_name))
        for t in component_types:
            if not self.is_type(t):
                raise TmspecErrorNotAType("identifier {} is not a type.", t.name)
        component = TmComponent(component_name, component_types, dict(attributes))
        self.components[component_name] = component

