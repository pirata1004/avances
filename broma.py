import tkinter as tk
from tkinter import messagebox

def mostrar_error():
    messagebox.showerror("HOUSTON TENEMOS UN PROBLEMA", "HAS SIDO HACKEADO")
    root.after(10, mostrar_error)  # Vuelve a llamar a la función después de 10 ms

root = tk.Tk()
root.withdraw()  # Oculta la ventana principal
root.after(0, mostrar_error)  # Empieza de inmediato
root.mainloop()
