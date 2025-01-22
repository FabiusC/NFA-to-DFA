from collections import defaultdict
from classes.node import Node
from classes.link import Link
import matplotlib.pyplot as plt
import networkx as nx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class AutomataModel:
    def __init__(self):
        self.nodes = []
        self.links = []
        self.transitions = defaultdict(lambda: defaultdict(list))  # Matriz de transiciones
        self.accept_states = set()

    def add_node(self, name, x, y):
        self.nodes.append(Node(name, x, y))

    def get_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def add_link(self, origin_name, destination_name, transitions):
        origin = self.get_node(origin_name)
        destination = self.get_node(destination_name)
        if not origin or not destination:
            return

        link = self.get_link(origin, destination)
        if not link:
            link = Link(origin, destination)
            self.links.append(link)
        link.add_transitions(transitions)

        # Actualizar matriz de transiciones
        for transition in transitions:
            self.transitions[origin_name][transition].append(destination_name)

    def get_link(self, origin, destination):
        for link in self.links:
            if link.origin == origin and link.destination == destination:
                return link
        return None

    def delete_element(self, x, y):
        for node in self.nodes:
            if (node.x - 20 <= x <= node.x + 20) and (node.y - 20 <= y <= node.y + 20):
                self.nodes.remove(node)
                self.links = [link for link in self.links if link.origin != node and link.destination != node]
                return

        for link in self.links:
            origin_x, origin_y = link.origin.x, link.origin.y
            dest_x, dest_y = link.destination.x, link.destination.y
            if self._is_point_on_line(x, y, origin_x, origin_y, dest_x, dest_y):
                self.links.remove(link)
                return

    def _is_point_on_line(self, x, y, x1, y1, x2, y2):
        """Check if a point (x, y) is near a line between (x1, y1) and (x2, y2)."""
        distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / ((y2 - y1)**2 + (x2 - x1)**2)**0.5
        return distance < 5

    def set_acceptance_state(self, node_name, is_acceptance):
        node = self.get_node(node_name)
        if node:
            node.is_acceptance = is_acceptance
            if is_acceptance:
                self.accept_states.add(node_name)

    def print_transitions(self):
        """Imprime la matriz de transiciones en consola."""
        for state, paths in self.transitions.items():
            for symbol, next_states in paths.items():
                print(f"Estado {state} --[{symbol}]--> {next_states}")

    # Convertir AFN-λ a AFD
    def convert_afn_to_afd(self):
        """
        Convierte un AFN con transiciones lambda a un AFD.
        """
        import copy

        def lambda_closure(state, transitions):
            """Calcula el cierre lambda de un estado."""
            closure = set([state])
            stack = [state]

            while stack:
                current = stack.pop()
                for next_state in transitions.get(current, {}).get('ʎ', []):
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)

            return closure

        # Crear copias de datos para no modificar los originales
        original_transitions = copy.deepcopy(self.transitions)
        original_accept_states = copy.deepcopy(self.accept_states)

        # Verificar si hay transiciones lambda
        has_lambda = any('ʎ' in original_transitions[state] for state in original_transitions)

        if has_lambda:
            print("Detectadas transiciones lambda. Convirtiendo AFN-λ a AFN...")
            new_transitions = {}

            # Calcular el cierre lambda para todos los estados
            all_states = set(original_transitions.keys())
            for paths in original_transitions.values():
                for next_states in paths.values():
                    all_states.update(next_states)

            lambda_closures = {state: lambda_closure(state, original_transitions) for state in all_states}

            # Generar las nuevas transiciones eliminando las lambdas
            for state in original_transitions:
                new_transitions[state] = {}
                for symbol in original_transitions[state]:
                    if symbol == 'ʎ':
                        continue

                    # Determinar los estados alcanzables mediante este símbolo
                    reachable_states = set()
                    for closure_state in lambda_closures[state]:
                        reachable_states.update(original_transitions.get(closure_state, {}).get(symbol, []))

                    # Expandir los estados alcanzables por sus cierres lambda
                    final_reachable = set()
                    for reachable_state in reachable_states:
                        final_reachable.update(lambda_closures[reachable_state])

                    if final_reachable:
                        new_transitions[state][symbol] = list(final_reachable)

            # Identificar los nuevos estados de aceptación
            new_accept_states = set()
            for state in original_accept_states:
                for closure_state in lambda_closures[state]:
                    new_accept_states.add(closure_state)

            # Actualizar el modelo con las transiciones sin lambda
            self.transitions = new_transitions
            self.accept_states = new_accept_states

            print("Conversión de AFN-λ a AFN completada.")
        else:
            print("No se detectaron transiciones lambda. Continuando con la conversión AFN a AFD...")

        # Continuar con la conversión AFN a AFD
        print("Convirtiendo AFN a AFD...")
        new_states = {}  # Mapea conjuntos de estados del AFN a estados únicos del AFD
        new_transitions = {}  # Transiciones del AFD
        initial_state = frozenset(lambda_closure("q0", self.transitions))  # Cierre lambda del estado inicial
        queue = [initial_state]  # Cola para procesar conjuntos de estados
        new_states[initial_state] = "k0"  # Mapear el conjunto inicial al estado 'k0'

        while queue:
            current = queue.pop(0)  # Procesar el siguiente conjunto de estados
            new_transitions[new_states[current]] = {}

            for symbol in {s for state in current for s in self.transitions.get(state, {}) if s != 'ʎ'}:
                # Determinar el conjunto de estados alcanzables para este símbolo
                next_states = frozenset(
                    dest for sub_state in current for dest in self.transitions[sub_state].get(symbol, [])
                )
                if not next_states:
                    continue

                if next_states not in new_states:
                    # Asignar un nuevo nombre al subconjunto de estados
                    new_state_name = f"k{len(new_states)}"
                    new_states[next_states] = new_state_name
                    queue.append(next_states)

                # Actualizar la tabla de transiciones del AFD
                new_transitions[new_states[current]][symbol] = new_states[next_states]

        # Identificar los estados de aceptación en el AFD
        afd_accept_states = set(
            new_states[state] for state in new_states if any(s in self.accept_states for s in state)
        )

        # Actualizar las transiciones y estados del modelo
        self.transitions = new_transitions
        self.accept_states = afd_accept_states

        # Asegurarse de que todos los estados estén en el grafo antes de graficar
        all_states = set(new_transitions.keys())
        for paths in new_transitions.values():
            all_states.update(paths.values())

        self.all_states = all_states  # Guardar estados del AFD

        # Imprimir la tabla de transiciones resultante
        logging.info("Tabla de transiciones final del AFD:")
        for state, transitions in self.transitions.items():
            is_acceptance = "(Estado de aceptación)" if state in self.accept_states else ""
            for symbol, next_state in transitions.items():
                logging.info(f"Estado {state} --[{symbol}]--> {next_state} {is_acceptance}")

        print(f"Estados de aceptación del AFD: {self.accept_states}")
        print("Conversión de AFN a AFD completada.")
        self.print_transitions()
        self.display_graph()


    def display_graph(self):
        """Muestra el autómata como un grafo usando matplotlib y networkx, e imprime la tabla de transiciones."""
        import pandas as pd  # Para crear una tabla de transiciones legible
        graph = nx.DiGraph()

        # Calcular todos los estados si no se definieron previamente
        if not hasattr(self, 'all_states') or not self.all_states:
            self.all_states = set(self.transitions.keys())
            for paths in self.transitions.values():
                for next_states in paths.values():
                    if isinstance(next_states, list):
                        self.all_states.update(",".join(sorted(next_states)) for next_states in paths.values())
                    else:
                        self.all_states.add(next_states)

        # Convertir todos los estados a cadenas para garantizar que sean hashables
        self.all_states = {",".join(sorted(state)) if isinstance(state, list) else state for state in self.all_states}

        # Agregar nodos para todos los estados del AFD
        for state in self.all_states:
            graph.add_node(state)

        # Preparar datos para la tabla de transiciones
        transition_table = []

        # Agregar aristas al grafo con etiquetas únicas
        for state, paths in self.transitions.items():
            # Asegurar que los estados sean hashables
            state = ",".join(sorted(state)) if isinstance(state, list) else state
            for symbol, next_state in paths.items():
                next_state = ",".join(sorted(next_state)) if isinstance(next_state, list) else next_state
                if graph.has_edge(state, next_state):
                    # Concatenar símbolos en una única etiqueta si ya existe una arista
                    current_label = graph[state][next_state]['label']
                    if symbol not in current_label.split(', '):
                        graph[state][next_state]['label'] = f"{current_label}, {symbol}"
                else:
                    graph.add_edge(state, next_state, label=symbol)
                
                # Agregar datos a la tabla de transiciones
                transition_table.append({'State': state, 'Input': symbol, 'Next State': next_state})

        # Mostrar la tabla de transiciones
        df = pd.DataFrame(transition_table)
        print("\nTabla de transiciones:")
        print(df)

        # Generar posiciones para todos los nodos
        pos = nx.spring_layout(graph)

        # Dibujar nodos y aristas
        nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10)

        # Ajustar etiquetas para aristas
        edge_labels = nx.get_edge_attributes(graph, 'label')

        for (source, target), label in edge_labels.items():
            x_mid = (pos[source][0] + pos[target][0]) / 2
            y_mid = (pos[source][1] + pos[target][1]) / 2

            # Ajustar la posición de las etiquetas para que no queden sobre los nodos o aristas
            if source == target:
                # Transiciones recursivas (bucle): ajustar la posición de la etiqueta
                x_mid += 0.15
                y_mid += 0.15
            else:
                # Desplazar etiquetas en transiciones normales
                x_mid += 0.05 if pos[source][0] < pos[target][0] else -0.05
                y_mid += 0.05 if pos[source][1] < pos[target][1] else -0.05

            # Dibujar etiqueta ajustada
            plt.text(x_mid, y_mid, label, fontsize=8, color='red', ha='center',
                    bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.3'))

        # Dibujar aristas con curvas para evitar solapamientos
        drawn_edges = set()
        for source, target in graph.edges():
            if (source, target) not in drawn_edges:
                if source == target:
                    print(f"Transición recursiva: {source} -> {target}")
                    # Dibujar arista recursiva
                    nx.draw_networkx_edges(
                        graph, pos,
                        edgelist=[(source, target)],
                        connectionstyle='arc3,rad=0.5',
                        arrowsize=15
                    )
                else:
                    print(f"Enlace unidireccional: {source} -> {target}")
                    # Dibujar enlace individual con curvatura ligera
                    nx.draw_networkx_edges(
                        graph, pos,
                        edgelist=[(source, target)],
                        arrowsize=15
                    )
                # Añadir la arista al conjunto
                drawn_edges.add((source, target))

        # Marcar estados de aceptación
        if self.accept_states:
            nx.draw_networkx_nodes(
                graph, pos,
                nodelist=self.accept_states,
                node_color='lightgreen',
                node_size=2000
            )

        plt.show()

