class Link:
    def __init__(self, origin, destination, transitions=None):
        self.origin = origin          # Nodo de origen (objeto Node)
        self.destination = destination  # Nodo de destino (objeto Node)
        self.transitions = transitions or []  # Lista de cadenas de transición

        # Agregar enlace a los nodos correspondientes
        origin.add_link(self)
        destination.add_link(self)

    def add_transition(self, transition):
        """Agrega una transición al enlace."""
        if transition not in self.transitions:
            self.transitions.append(transition)

    def remove_transition(self, transition):
        """Elimina una transición del enlace."""
        if transition in self.transitions:
            self.transitions.remove(transition)

    def get_transitions(self):
        """Devuelve las transiciones del enlace como una lista."""
        return self.transitions

    def get_transitions_as_string(self):
        """Devuelve las transiciones como una cadena separada por comas."""
        return ", ".join(self.transitions)


