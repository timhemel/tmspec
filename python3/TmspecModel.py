from TmspecError import *

class TmComponent:
    def __init__(self, name, types, attrs = {}):
        self.name = name
        self.types = types
        self.attr = attrs

class TmspecModel:

    def __init__(self):
        self.zones = set([])
        self.components = {}
        self.identifiers = {
                'process' : 'process',
                'datastore' : 'datastore',
                'dataflow' : 'dataflow',
                'externalentity' : 'externalentity',
        }

    def get_identifier(self, identifier):
        try:
            return self.identifiers[identifier]
        except KeyError:
            raise TmspecErrorUnknownIdentifier

    def add_zone(self, zone_name):
        print("add zone", zone_name)
        if zone_name in self.identifiers:
            raise TmspecErrorDuplicateIdentifier("identifier {} already in use."
                            .format(zone_name))
        self.zones.add(zone_name)
        self.identifiers[zone_name] = zone_name

    def add_component(self, component_name, component_types, attributes):
        component = TmComponent(component_name, component_types, dict(attributes))
        self.components[component_name] = component

