
class TmComponent:
    def __init__(self, name, types, attrs = {}):
        self.name = name
        self.types = types
        self.attr = attrs

class TmspecModel:

    def __init__(self):
        self.zones = set([])
        self.components = {}

    def add_zone(self, zone_name):
        self.zones.add(zone_name)

    def add_component(self, component_name, component_types, attributes):
        component = TmComponent(component_name, component_types, dict(attributes))
        self.components[component_name] = component

