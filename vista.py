#Vista

import tkinter as tk
import math
from utils import LambdaManager
from tkinter import simpledialog, Toplevel, Label, Entry, Button

class AutomataPaint:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Autómatas - Vista de Paint")

        # Configuración del lienzo
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Barra de herramientas
        self.toolbar = tk.Frame(root, bg="lightgray", width=200)
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)

        self.mode = tk.StringVar(value="Nodo")

        self.node_button = tk.Button(self.toolbar, text="Modo Nodo", bg="lightblue", command=self.set_node_mode)
        self.node_button.pack(pady=10, padx=10, fill=tk.X)

        self.link_button = tk.Button(self.toolbar, text="Modo Enlace", bg="lightgreen", command=self.set_link_mode)
        self.link_button.pack(pady=10, padx=10, fill=tk.X)

        self.acceptance_button = tk.Button(self.toolbar, text="Estado de Aceptación", bg="lightpink", command=self.set_acceptance_mode)
        self.acceptance_button.pack(pady=10, padx=10, fill=tk.X)

        self.delete_button = tk.Button(self.toolbar, text="Borrar", bg="salmon", command=self.set_delete_mode)
        self.delete_button.pack(pady=10, padx=10, fill=tk.X)

        self.convert_afn_lambda_button = tk.Button(self.toolbar, text="Convertir AFN-λ a AFN", bg="orange", command=self.convert_afn_lambda)
        self.convert_afn_lambda_button.pack(pady=10, padx=10, fill=tk.X)

        self.convert_afn_button = tk.Button(self.toolbar, text="Convertir AFN a AFD", bg="yellow", command=self.convert_afn)
        self.convert_afn_button.pack(pady=10, padx=10, fill=tk.X)

        self.clear_canvas_button = tk.Button(self.toolbar, text="Limpiar Canvas", bg="red", command=self.clear)
        self.clear_canvas_button.pack(pady=10, padx=10, fill=tk.X)

        # Estructuras internas
        self.controller = None
        self.current_node = None
        self.delete_mode = False
        self.acceptance_mode = False

        # Eventos
        self.canvas.bind("<Button-1>", self.on_click)

    def set_controller(self, controller):
        self.controller = controller

    def set_node_mode(self):
        self.mode.set("Nodo")
        self.delete_mode = False
        self.acceptance_mode = False

    def set_link_mode(self):
        self.mode.set("Enlace")
        self.delete_mode = False
        self.acceptance_mode = False

    def set_acceptance_mode(self):
        self.mode.set("Aceptación")
        self.delete_mode = False
        self.acceptance_mode = True

    def set_delete_mode(self):
        self.mode.set("Borrar")
        self.delete_mode = True
        self.acceptance_mode = False

    def on_click(self, event):
        if self.delete_mode:
            self.controller.delete_element(event.x, event.y)
        elif self.acceptance_mode:
            self.set_acceptance_state(event.x, event.y)
        elif self.mode.get() == "Nodo":
            self.controller.add_node(event.x, event.y)
        elif self.mode.get() == "Enlace":
            self.add_link(event.x, event.y)

    def draw_node(self, name, x, y):
        """Dibuja un nodo en el lienzo con tags separados para el óvalo y el texto."""
        self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="lightblue", outline="black", tags=(f"node_{name}", name))
        self.canvas.create_text(x, y, text=name, fill="black", tags=name)

    def add_link(self, x, y):
        """Conecta dos nodos con un enlace."""
        clicked_node = self.get_node_at_position(x, y)

        if clicked_node:
            if not self.current_node:
                self.current_node = clicked_node  # Guarda el objeto Node
            else:
                self.show_transition_dialog(self.current_node.name, clicked_node.name)
                self.current_node = None

    def show_transition_dialog(self, origin_name, destination_name):
        """Muestra un cuadro de diálogo personalizado para ingresar las transiciones."""
        dialog = Toplevel(self.root)
        dialog.title("Agregar Transiciones")
        dialog.geometry("350x200")

        Label(dialog, text=f"Agregar transiciones de {origin_name} a {destination_name}").pack(pady=10)
        Label(dialog, text="(Separe las transiciones por comas)").pack(pady=5)

        entry = Entry(dialog, width=30)
        entry.pack(pady=10)

        def insert_lambda():
            """Inserta el símbolo ʎ en el campo de entrada."""
            entry.insert(tk.END, "ʎ")

        def submit():
            """Procesa y agrega las transiciones ingresadas."""
            # Separar por comas y limpiar espacios
            transitions = [t.strip() for t in entry.get().split(",") if t.strip()]

            if transitions:  # Validar que haya al menos una transición
                self.controller.add_link(origin_name, destination_name, transitions)
            else:
                print("Error: No se ingresaron transiciones válidas.")

            dialog.destroy()

        # Botones para insertar ʎ y confirmar
        Button(dialog, text="ʎ", command=insert_lambda).pack(side=tk.LEFT, padx=10, pady=10)
        Button(dialog, text="Aceptar", command=submit).pack(side=tk.RIGHT, padx=10, pady=10)

    def get_node_at_position(self, x, y):
        """Busca un nodo en la posición dada."""
        for node in self.controller.model.nodes:
            if (node.x - 20 <= x <= node.x + 20) and (node.y - 20 <= y <= node.y + 20):
                return node  # Devuelve el objeto Node
        return None

    def draw_link(self, origin, destination, transitions):
        """Dibuja un enlace entre dos nodos en el lienzo con transiciones concatenadas por comas."""
        import math

        # Buscar el objeto Link correspondiente
        link = next(l for l in self.controller.model.links if l.origin.name == origin and l.destination.name == destination)

        # Recuperar las transiciones desde el objeto Link
        transitions = link.get_transitions()

        # Buscar los objetos Node correspondientes
        origin_node = next(node for node in self.controller.model.nodes if node.name == origin)
        dest_node = next(node for node in self.controller.model.nodes if node.name == destination)

        x1, y1 = origin_node.x, origin_node.y
        x2, y2 = dest_node.x, dest_node.y

        # Dibujar la línea del enlace
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, tags=f"link_{origin}_{destination}")

        # Calcular el punto medio de la línea
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        # Concatenar las transiciones separadas por comas
        transitions_text = ", ".join(LambdaManager.replace_lambda_for_print(t) for t in transitions)

        # Dibujar las transiciones centradas en el gráfico
        self.canvas.create_text(
            mid_x, mid_y,  # Centrado en el enlace
            text=transitions_text,
            fill="red",
            font=("Arial", 10, "bold"),
            tags=f"text_{origin}_{destination}"
        )

    def set_acceptance_state(self, x, y):
        """Alterna el estado de aceptación de un nodo."""
        clicked_node = self.get_node_at_position(x, y)
        if clicked_node:
            # Alternar el estado de aceptación en el modelo
            is_acceptance = not clicked_node.is_acceptance
            self.controller.set_acceptance_state(clicked_node.name, is_acceptance)
            
            # Actualizar visualización solo para el óvalo
            oval_tag = f"node_{clicked_node.name}"
            if is_acceptance:
                self.canvas.itemconfig(oval_tag, outline="gold", width=3)  # Estado de aceptación
            else:
                self.canvas.itemconfig(oval_tag, outline="black", width=1)  # Estado normal

    def update_links(self):
        """Limpia y redibuja todos los nodos y enlaces desde el modelo."""
        self.clear()
        for node in self.controller.model.nodes:
            self.draw_node(node.name, node.x, node.y)
        for link in self.controller.model.links:
            for transition in link.transitions:
                self.draw_link(link.origin.name, link.destination.name, transition)

    def delete_element(self, x, y):
        """Elimina un nodo o enlace en la posición clicada."""
        self.controller.delete_element(x, y)

    def convert_afn_lambda(self):
        self.controller.convert_afn_lambda_to_afn()

    def convert_afn(self):
        self.controller.convert_afn_to_afd()

    def clear(self):
        self.canvas.delete("all")
        self.controller.model.nodes = []
        self.controller.model.links = []

    def update_links(self):
        self.clear()
        for node, x, y in self.controller.model.nodes:
            self.draw_node(node, x, y)
        for origin, destination, transition in self.controller.model.links:
            self.draw_link(origin, destination, transition)
