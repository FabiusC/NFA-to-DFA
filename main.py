import tkinter as tk
from modelo import AutomataModel
from vista import AutomataPaint
from controlador import AutomataController
import sys
import io

# Forzar la salida estándar a UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    root = tk.Tk()
    model = AutomataModel()
    view = AutomataPaint(root)
    controller = AutomataController(model, view)
    view.set_controller(controller)
    root.mainloop()
