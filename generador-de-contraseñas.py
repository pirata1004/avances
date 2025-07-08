import tkinter as tk
import random, string

def generar():
    contraseña = ""
    for _ in range(11):
        if random.randint(1, 2) == 1:
            contraseña += str(random.randint(1, 9))
        else:
            contraseña += random.choice(string.ascii_letters)
    contraseña_var.set(contraseña)

# ✅ Crear primero la ventana
app = tk.Tk()
app.geometry('500x300')
app.title('GENERADOR DE CONTRASEÑAS')

# ✅ Luego crear variables asociadas a esa ventana
contraseña_var = tk.StringVar()
contraseña_var.set("Aquí aparecerá tu contraseña")

tk.Label(app, text="GENERADOR DE CONTRASEÑAS POR PIRATA1004").pack(pady=10)
tk.Entry(app, textvariable=contraseña_var, font=("Arial", 14)).pack(pady=10)
tk.Button(app, text="GENERAR", command=generar).pack()

app.mainloop()
