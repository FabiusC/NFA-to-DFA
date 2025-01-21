#Controlador
class AutomataController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)

    def add_node(self, x, y):
        name = f"q{len(self.model.nodes)}"
        self.model.add_node(name, x, y)
        self.view.draw_node(name, x, y)

    def add_link(self, origin_name, destination_name, transitions):
        self.model.add_link(origin_name, destination_name, transitions)
        self.view.draw_link(origin_name, destination_name, transitions)

    def set_acceptance_state(self, node_name, is_acceptance):
        self.model.set_acceptance_state(node_name, is_acceptance)

    def convert_afn_to_afd(self):
        self.model.convert_afn_to_afd()