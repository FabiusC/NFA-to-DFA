#Controlador

class AutomataController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def add_node(self, x, y):
        node_name = f"q{len(self.model.nodes)}"
        self.model.add_node(node_name, x, y)
        self.view.draw_node(node_name, x, y)

    def add_link(self, origin_name, destination_name, transitions):
        """Agrega un enlace al modelo y la vista con múltiples transiciones."""
        link = self.model.add_link(origin_name, destination_name, transitions)
        if link:
            for transition in transitions:
                self.view.draw_link(origin_name, destination_name, transition)

    def set_acceptance_state(self, node_name, is_acceptance):
        """Establece el estado de aceptación de un nodo en el modelo."""
        self.model.set_acceptance_state(node_name, is_acceptance)

    def convert_afn_lambda_to_afn(self):
        self.model.convert_afn_lambda_to_afn()
        self.update_view()

    def convert_afn_to_afd(self):
        self.model.convert_afn_to_afd()
        self.update_view()

    def update_view(self):
        self.view.clear()
        for node, x, y in self.model.nodes:
            self.view.draw_node(node, x, y)
        for origin, destination, transition in self.model.links:
            self.view.draw_link(origin, destination, transition)

    def delete_element(self, x, y):
        """Elimina un nodo o enlace basándose en las coordenadas."""
        # Verificar si el clic corresponde a un nodo
        for node in self.model.nodes:
            if (node.x - 20 <= x <= node.x + 20) and (node.y - 20 <= y <= node.y + 20):
                self.model.delete_node(node.name)
                self.view.update_links()
                return

        # Verificar si el clic corresponde a un enlace
        for link in self.model.links:
            if self.is_click_on_link(x, y, link):
                self.model.delete_link(link.origin.name, link.destination.name)
                self.view.update_links()
                return

    def is_click_on_link(self, x, y, link):
        """Comprueba si un clic ocurre cerca de un enlace."""
        x1, y1 = link.origin.x, link.origin.y
        x2, y2 = link.destination.x, link.destination.y

        # Fórmula para calcular la distancia de un punto a una línea
        distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / ((y2 - y1)**2 + (x2 - x1)**2)**0.5
        return distance <= 5


