class Link:
    def __init__(self, origin, destination):
        self.origin = origin
        self.destination = destination
        self.transitions = set()

    def add_transitions(self, new_transitions):
        self.transitions.update(new_transitions)

    def get_transitions(self):
        return list(self.transitions)

    def add_transition(self, transition):
        """Agrega una transición al enlace."""
        if transition not in self.transitions:
            self.transitions.append(transition)

    def remove_transition(self, transition):
        """Elimina una transición del enlace."""
        if transition in self.transitions:
            self.transitions.remove(transition)

    def get_transitions_as_string(self):
        """Devuelve las transiciones como una cadena separada por comas."""
        return ", ".join(self.transitions)


