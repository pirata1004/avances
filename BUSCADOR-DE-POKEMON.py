import tkinter as tk
from tkinter import messagebox
import requests


def busqueda():
    pokemon = entrada_var.get().lower()
    if not pokemon:
        messagebox.showwarning("Error", "Debes escribir el nombre de un Pokémon")
        return

    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon}"

    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        datos = respuesta.json()

        tipos = [t["type"]["name"] for t in datos["types"]]
        movimientos = [m["move"]["name"] for m in datos["moves"][:5]]  # solo los primeros 5

        salida_var.set(f"Tipo(s): {', '.join(tipos)}")
        salida_var2.set("Movimientos: " + ", ".join(movimientos))

    except requests.exceptions.HTTPError:
        salida_var.set("")
        salida_var2.set("")
        messagebox.showerror("No encontrado", f"No se encontró el Pokémon '{pokemon}'")


# --- Interfaz gráfica ---

app = tk.Tk()
app.title("Buscador de Pokémon")
app.geometry("500x300")
app.configure(bg="lightblue")

entrada_var = tk.StringVar()
salida_var = tk.StringVar()
salida_var2 = tk.StringVar()

# Título
tk.Label(app, text="BUSCADOR DE POKÉMON POR PIRATA1004", bg="SteelBlue", fg="white",
         font=("Helvetica", 14, "bold")).pack(pady=10)

# Entrada de texto
frame = tk.Frame(app, bg="lightblue")
frame.pack(pady=5)

tk.Label(frame, text="Nombre del Pokémon:", bg="lightblue", font=("Helvetica", 12)).pack(side="left")
tk.Entry(frame, textvariable=entrada_var, width=20, font=("Helvetica", 12)).pack(side="left", padx=5)

# Botón de búsqueda
tk.Button(app, text="Buscar", command=busqueda, bg="green", fg="white", font=("Helvetica", 12)).pack(pady=10)

# Resultados
tk.Label(app, textvariable=salida_var, bg="lightblue", font=("Helvetica", 12)).pack(pady=5)
tk.Label(app, textvariable=salida_var2, bg="lightblue", font=("Helvetica", 12)).pack(pady=5)

# Ejecutar la app
app.mainloop()
