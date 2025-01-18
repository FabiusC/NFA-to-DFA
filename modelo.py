#Modelo

from classes.node import Node
from classes.link import Link

class AutomataModel:
    def __init__(self):
        self.nodes = []  # Lista de nodos (objetos Node)
        self.links = []  # Lista de enlaces (objetos Link)

    def add_node(self, name, x, y):
        """Crea y agrega un nodo al modelo."""
        node = Node(name, x, y)
        print("Node added: ", node.name, node.x, node.y)
        self.nodes.append(node)

    def add_link(self, origin_name, destination_name, transitions):
        """Crea y agrega un enlace al modelo."""
        origin = self.get_node_by_name(origin_name)
        destination = self.get_node_by_name(destination_name)
        if origin and destination:
            link = Link(origin, destination, transitions)
            self.links.append(link)
            # Imprimir las transiciones del enlace en formato de arreglo
            print(f"Link Created: {origin_name} -> {destination_name}, Transitions: {transitions}")
            return link
        return None

    def delete_node(self, name):
        """Elimina un nodo y todos sus enlaces asociados."""
        node = self.get_node_by_name(name)
        if node:
            for link in list(node.links):
                self.delete_link(link.origin.name, link.destination.name)
            self.nodes.remove(node)

    def set_acceptance_state(self, node_name, is_acceptance=True):
        """Establece el estado de aceptación de un nodo."""
        node = self.get_node_by_name(node_name)
        if node:
            node.set_acceptance(is_acceptance)

    def delete_link(self, origin_name, destination_name):
        """Elimina un enlace específico."""
        link = self.get_link_by_nodes(origin_name, destination_name)
        if link:
            link.origin.remove_link(link)
            link.destination.remove_link(link)
            self.links.remove(link)

    def get_node_by_name(self, name):
        """Busca un nodo por su nombre."""
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def get_link_by_nodes(self, origin_name, destination_name):
        """Busca un enlace por los nombres de sus nodos."""
        for link in self.links:
            if link.origin.name == origin_name and link.destination.name == destination_name:
                return link
        return None

    def convert_afn_lambda_to_afn(self):
        """Convierte un AFN-λ a un AFN."""
        lambda_closure = self.compute_lambda_closures()
        new_links = []

        for origin, destination, transition in self.links:
            if transition == "λ":
                continue
            origins = lambda_closure[origin]
            destinations = lambda_closure[destination]

            for o in origins:
                for d in destinations:
                    new_links.append((o, d, transition))

        self.links = new_links

    def compute_lambda_closures(self):
        """Calcula el cierre lambda de cada estado."""
        closures = {node[0]: set([node[0]]) for node in self.nodes}

        for origin, destination, transition in self.links:
            if transition == "λ":
                closures[origin].add(destination)

        changed = True
        while changed:
            changed = False
            for node in closures:
                current_closure = set(closures[node])
                for reachable in list(current_closure):
                    if reachable in closures:
                        new_states = closures[reachable] - closures[node]
                        if new_states:
                            closures[node].update(new_states)
                            changed = True
        return closures

    def convert_afn_to_afd(self):
        """Convierte un AFN a un AFD."""
        dfa_states = []
        dfa_links = []
        state_map = {}

        initial_state = frozenset([self.nodes[0][0]])
        dfa_states.append(initial_state)
        state_map[initial_state] = f"D0"

        unprocessed_states = [initial_state]

        while unprocessed_states:
            current_state = unprocessed_states.pop()
            current_state_name = state_map[current_state]

            transitions = {}
            for afn_state in current_state:
                for origin, destination, transition in self.links:
                    if origin == afn_state:
                        if transition not in transitions:
                            transitions[transition] = set()
                        transitions[transition].add(destination)

            for symbol, destinations in transitions.items():
                destination_set = frozenset(destinations)

                if destination_set not in dfa_states:
                    dfa_states.append(destination_set)
                    state_map[destination_set] = f"D{len(dfa_states) - 1}"
                    unprocessed_states.append(destination_set)

                dfa_links.append((current_state_name, state_map[destination_set], symbol))

        self.nodes = [(state_map[state], 0, 0) for state in dfa_states]
        self.links = dfa_links
