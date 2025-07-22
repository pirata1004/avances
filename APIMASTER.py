import datetime

from tkinter.messagebox import showinfo
import requests
import customtkinter as ctk
from customtkinter import *





def futbolista(player):
    url = f'https://www.thesportsdb.com/api/v1/json/123/searchplayers.php?p={player}'
    response = requests.get(url).json()
    resultado = response['player']
    for coindencia in resultado:
        actualizar_textbox(coindencia["strPosition"])
        actualizar_textbox(("nacionalidad" + " " + coindencia["strNationality"]))
        actualizar_textbox(coindencia["strTeam"])
        actualizar_textbox(coindencia["strPlayer"])

def monetario():
    current_date = datetime.date.today()


    url = f'https://api.frankfurter.dev/v1/{current_date}'
    datos = requests.get(url).json()

    for coindencia in datos["rates"]:
        actualizar_textbox(("un euro son" , str(coindencia) , str(datos["rates"][coindencia])))

def monedas():
    url = 'https://api.frankfurter.dev/v1/currencies'
    response = requests.get(url).json()
    for coindencia in response:
        actualizar_textbox(((coindencia) , (response[coindencia])))

def comida(alimento):

    url = f' https://www.themealdb.com/api/json/v1/1/search.php?s={alimento}'
    response = requests.get(url).json()
    resultado = response["meals"]

    for coincidencia in resultado:
        actualizar_textbox(coincidencia["strInstructions"])
        actualizar_textbox(coincidencia["strArea"])
        actualizar_textbox(coincidencia["strMeal"])

def FULLRICK():
    URL = 'https://rickandmortyapi.com/api/character/'

    while URL:
        dato = requests.get(URL).json()
        info = dato["results"]
        for item in info:

            actualizar_textbox("------------")
            actualizar_textbox(item["species"])
            actualizar_textbox(item["origin"]["name"])
            actualizar_textbox(item["gender"])
            actualizar_textbox(item["name"])
        URL = dato["info"]["next"]

def RICK1(name):
    URL = f'https://rickandmortyapi.com/api/character/?name={name}'
    dato = requests.get(URL).json()
    info = dato["results"]
    for item in info:

        actualizar_textbox("------------")
        actualizar_textbox(item["species"])
        actualizar_textbox(item["origin"]["name"])
        actualizar_textbox(item["gender"])
        actualizar_textbox(item["name"])

def decision(valor):
    estado = switch.get()

    try:
        if valor == "POKEMON":
            if estado == 0:
                POKEFIND(entrada1.get())
            if estado == 1:
                FULLPOKEMON()

        elif valor == "STAR-WARS":
            if estado == 1:
                STARFIND()
            elif estado == 0:
                STAR1(entrada1.get())

            else:
                actualizar_textbox("algo no salio bien")
        elif valor == "RICK-AND-MORTY":
            if estado == 0:
                RICK1(entrada1.get())
            elif estado == 1:
                FULLRICK()
        elif valor == "COCTELES":
            if estado == 0:
                cocteles(entrada1.get())
            else:
                showinfo("ERROR BUSQUEDA","en el criterio de cocteles no esta disponible la opcion todos")
        elif valor == "COMIDA":
            if estado == 0:
                comida(entrada1.get())
            if estado == 1:
                showinfo("NO DISPONIBLE","OPCION TODOS NO DISPONIBLE EN ALIMENTOS")
        elif valor == "MONEDA":
            if estado == 0:
                monetario()
            if estado == 1:
                monedas()
        elif valor == "FUTBOLISTA":
            if estado == 0:
                futbolista(entrada1.get())
            if estado == 1:
                actualizar_textbox("no esta disponible la busqueda de todos los jugadores")

    except:
        showinfo("ERROR BUSQUEDA", "revise el nombre o el criterio de busqueda")

def POKEFIND(pokemon):
    POKEDEX = f'https://pokeapi.co/api/v2/pokemon/{pokemon.lower()}'
    pokedex = requests.get(POKEDEX).json()
    tipos = pokedex['types']
    ataques = pokedex["abilities"]
    mov = pokedex["moves"]

    habilidades = [ ]
    movimientos = [ ]
    for coincencia in tipos:
        salida1.set(coincencia["type"]["name"])
    for habilidad in ataques:

        habilidades.append(habilidad["ability"]["name"])

    for movimiento in mov :

        movimientos.append(movimiento["move"]["name"])

    salida1.set(habilidades)
    salida2.set(movimientos)
    actualizar_textbox(salida2.get())

def FULLPOKEMON():
    fullurl = 'https://pokeapi.co/api/v2/pokemon/'
    while fullurl:
        datos = requests.get(fullurl).json()
        nombre = datos["results"]

        for coindencia in nombre:

            actualizar_textbox(coindencia["name"])
        fullurl = datos["next"]

def STARFIND():
    STARURL = 'https://swapi.py4e.com/api/people/?format=json'

    while STARURL:
        datos = requests.get(STARURL).json()
        for Names  in datos["results"]:
            actualizar_textbox(Names["name"])
        STARURL = datos["next"]

def cocteles(name):

    coctelurl = f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}'

    request = requests.get(coctelurl).json()
    request = request["drinks"]

    for item in request:

        actualizar_textbox(item["strInstructionsES"])
        actualizar_textbox("-------------------------")
        actualizar_textbox(item["strDrink"])
        actualizar_textbox("-")

def STAR1(nombre):
    url = f"https://swapi.py4e.com/api/people/?search={nombre}"
    response = requests.get(url)

    if response.status_code == 200:
        datos = response.json()
        resultados = datos.get("results", [])
        if resultados:

            for personaje in resultados:
                actualizar_textbox(f"Nombre: {personaje['name']}")
                actualizar_textbox(f"Altura: {personaje['height']} cm")
                actualizar_textbox(f"Peso: {personaje['mass']} kg")
                actualizar_textbox(f"Color de cabello: {personaje['hair_color']}")
                actualizar_textbox(f"Color de piel: {personaje['skin_color']}")
                actualizar_textbox(f"Color de ojos: {personaje['eye_color']}")
                actualizar_textbox(f"Nacimiento: {personaje['birth_year']}")
                actualizar_textbox(f"Género: {personaje['gender']}")
                actualizar_textbox("-" * 40)
            else:
                actualizar_textbox("INFORMACION")
        else:
            actualizar_textbox("Error al consultar la API.")

    # Ejemplo de uso:

def mostrar_valor():
    valor = combo.get()
    decision(valor)


ctk.set_appearance_mode("dark")  # Opciones: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # También puedes probar: "green", "dark-blue", etc.





app = ctk.CTk()
app.geometry('800x800')

app.resizable(False, False)

salida1 = ctk.StringVar()
salida2 = ctk.StringVar()
salida3 = ctk.StringVar()
entrada1 = ctk.StringVar()
entrada2 = ctk.StringVar()

app.title("API MASTER")
label = ctk.CTkLabel(master=app,text="API MASTER",font=("Arial", 90)).pack()



combo = ctk.CTkComboBox(master=app, values=["POKEMON", "STAR-WARS", "RICK-AND-MORTY","COCTELES","COMIDA","MONEDA","FUTBOLISTA"])
combo.pack(pady=10)

# Obtener valor seleccionado

CTkEntry(master = app,textvariable=entrada1,placeholder_text="Inserte el personaje que desea buscar").pack(pady=10)
CTkButton(master=app,text="busqueda",command= lambda : decision( mostrar_valor() ) ).pack(pady=10)


ctk.CTkLabel(master=app,textvariable=salida1,font=("Arial", 15)).pack()
# ctk.CTkLabel(master=app,textvariable=salida2,font=("Arial", 15)).pack()


textbox = ctk.CTkTextbox(app, width=600, height=300)
textbox.pack(pady=20)

CTkButton(master=app,text="borrar",command= lambda: borrar_textbox()  ).pack(pady=10)

switch = ctk.CTkSwitch(master=app, text="TODOS", command= lambda :actualizar_textbox("cuando este seleccionado TODOS y FUTBOLISTA se hara una busqueda de equipos \n puede dar parones la busqueda completa" ) )
switch.pack(pady=10,side="right")
# Obtener estado: 1 o 0


def actualizar_textbox(texto):
    textbox.configure(state="normal")
    textbox.insert("0.0", str(texto) + "\n")
    textbox.configure(state="disabled")
def borrar_textbox():
    textbox.configure(state="normal")     # Permitir edición
    textbox.delete("0.0", "end")
    textbox.configure(state="normal")     # Dejar editable o usa "disabled" si querés bloquear




app.mainloop()

