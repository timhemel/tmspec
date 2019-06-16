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
        # self.types = {}

    def has_identifier(self, identifier):
        return identifier in self.identifiers

    def get_identifier(self, identifier):
        return self.identifiers.get(identifier)

    def is_type(self, obj):
        return isinstance(obj, TmType)

    def add_zone(self, zone):
        self.zones.add(zone)
        self.identifiers[zone.name] = zone

    def add_component(self, component):
        self.components[component.name] = component
        self.identifiers[component.name] = component

    def add_type(self, tm_type):
        # self.types[tm_type.name] = tm_type
        self.identifiers[tm_type.name] = tm_type

