class Node:
    def __init__(self, name, x, y, is_acceptance=False):
        self.name = name
        self.x = x
        self.y = y
        self.is_acceptance = is_acceptance  # Estado de aceptación
        self.links = []  # Enlaces conectados a este nodo

    def add_link(self, link):
        """Agrega un enlace conectado al nodo."""
        if link not in self.links:
            self.links.append(link)

    def remove_link(self, link):
        """Elimina un enlace conectado al nodo."""
        if link in self.links:
            self.links.remove(link)

    def set_acceptance(self, is_acceptance):
        """Establece si el nodo es un estado de aceptación."""
        self.is_acceptance = is_acceptance
