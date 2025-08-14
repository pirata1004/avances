import customtkinter
import tksheet
import pyodbc
from customtkinter import *
import pandas as pd

# Conexión a base de datos
DRIVER_NAME = 'SQL Server'
SERVERNAME = 'PC-TIC01\\SQLEXPRESS'
DATABASENAME = 'AQUAPROMONTROIG'

connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVERNAME};
    DATABASE={DATABASENAME};
    Trusted_Connection=yes;
    Timeout=10;
"""

conn = pyodbc.connect(connection_string)
print("Conectado a la base de datos")

def MostrarTabla(df):
    global frametabla
    global info
    frametabla = CTkFrame(master=app, fg_color="white")
    frametabla.pack(fill="both", expand=True, padx=20, pady=20,side=BOTTOM)
    info = df
    sheet = tksheet.Sheet(frametabla,
                          data=df.values.tolist(),
                          headers=list(df.columns),
                          show_x_scrollbar=True,
                          show_y_scrollbar=True)

    sheet.enable_bindings((
        "single_select", "column_select", "row_select",
        "arrowkeys", "right_click_popup_menu", "rc_select",
        "copy", "paste", "delete", "edit_cell"
    ))

    sheet.pack(fill="both", expand=True)

def consultar():

    criterio = opciones.get()
    entrada = entrada1.get()

    if criterio == "IDContracte":
        if SWICH.get() == 0:
            query = f"SELECT *  FROM tblDatosContratoAbonado where IDContrato = '{entrada}'"
            df = pd.read_sql(query, conn)
            MostrarTabla(df)
    elif criterio == "NOM":
        query = f"SELECT *  FROM tblDatosContratoAbonado where FechaBaja IS NULL and NombreAbonado LIKE '{entrada}' "
        df = pd.read_sql(query, conn)
        MostrarTabla(df)

    elif criterio == "DNI":
        if SWICH.get() == 0:
            query = f"SELECT *  FROM tblDatosContratoAbonado where DNIAbonado = '{entrada}' "
            df = pd.read_sql(query, conn)
            MostrarTabla(df)

    if criterio == "---":
        if SWICH.get() == 0:
            query = "SELECT *  FROM tblDatosContratoAbonado where FechaBaja IS NULL"
            df = pd.read_sql(query, conn)
            MostrarTabla(df)

        elif SWICH.get() == 1:
            query = "SELECT *  FROM tblDatosContratoAbonado"
            df = pd.read_sql(query, conn)
            MostrarTabla(df)
def exportar():

    info.to_csv("datos.csv", index=False)
    info.to_excel("datos.xlsx", index=False)


def sql():
    consulta = CTkInputDialog(text="FES LA CONSULTA", title="CONSULTA SQL")
    sql = consulta.get_input()
    df = pd.read_sql(sql, conn)
    MostrarTabla(df)

def sqlpredefinido():
    app2 = CTk()
    app2.mainloop()

def peticion(consulta):
    df = pd.read_sql(consulta, conn)
    MostrarTabla(df)

def consultasimple():

    LISTA = ["Mostra tots els abonats","Mostra els contractes d’alta","Mostra els contractes d’alta que no tinguin ni email ni telefon","Mostra els contractes MUNICIPALS – El llistat ha de ser número contracte, nom abonat i la direcció de la casa","Mostra els contractes que tinguin COMPTADOR PARE","Mostra el rebut amb el cost més elevat de cada contracte","Mostra el numero de contractes per cada ruta","Mostra el número de comptadors per any d’instal·lació","Mostra els contractes d’alta que no tinguin consum durant els 3 ultims trimestres"]
    valor = simple.get()
    if valor == "Mostra tots els abonats":
        peticion("SELECT NombreAbonado,DNIAbonado ,tblCalles.Calle,Numero,Escalera,Piso,Puerta  FROM tblDatosContratoAbonado INNER JOIN tblCalles ON tblCalles.IDCalle = tblDatosContratoAbonado.IDCalle ")
    elif valor == "Mostra els contractes d’alta":
        peticion("SELECT NombreAbonado,DNIAbonado , tblCalles.Calle,Numero, Escalera,Piso,Puerta FROM tblDatosContratoAbonado WHERE FechaBaja is  null")
    elif valor == "Mostra els contractes d’alta que no tinguin ni email ni telefon":
        peticion("SELECT IDContrato,NombreAbonado,DNIAbonado FROM tblDatosContratoAbonado WHERE FechaBaja is not null AND( EMailAbonado is null OR EMailAbonado= '') AND( TelefonoAbonado1 is null OR TelefonoAbonado1= '') AND( TelefonoAbonado2 is null OR TelefonoAbonado2= '') AND MovilAbonado IS NULL")
    elif valor == "Mostra els contractes que tinguin COMPTADOR PARE":
        peticion("SELECT NombreAbonado,CalleCarteo,NumeroCarteo,EscaleraCarteo,PisoCarteo,PuertaCarteo, IDContadorPadre  FROM tblDatosContratoAbonado WHERE IDContadorPadre != '' " )
    elif valor == "Mostra els contractes MUNICIPALS":
        peticion("SELECT IDContrato,NombreAbonado,Calle FROM tblDatosContratoAbonado INNER JOIN tblCalles ON tblCalles.IDCalle = tblDatosContratoAbonado.IDCalle WHERE IDContrato LIKE 'MUNIC%'")
    elif valor == "Mostra el rebut amb el cost més elevat de cada contracte":
        peticion("SELECT IDContrato ,MAX(ImporteRecibo) FROM tblRecibos GROUP BY IDContrato" )
    elif valor == "Mostra el numero de contractes per cada ruta":
        peticion("SELECT IDRutaLectura , COUNT(IDContrato) FROM tblDatosContratoAbonado WHERE IDRutaLectura not in ('8900','9999') GROUP BY IDRutaLectura")
    elif valor == "Mostra el número de comptadors per any d’instal·lació":
        peticion("SELECT YEAR(FechaInstalacion),COUNT(IDContador)   FROM tblDatosContratoAbonado GROUP BY YEAR(FechaInstalacion) ORDER BY YEAR(FechaInstalacion);")
    elif valor == "Contractes d’alta que tinguin activades les alertes de consum":
        peticion(" select * from tblDatosContratoAbonado where FechaBaja is null and IDTipoControl > 0")
    elif valor == "Mostra els contractes amb rebuts domicialitzats al compte bancari":
        peticion("select * from tblDatosContratoAbonado  where FechaBaja is null and FormaPago = 2;")
    elif valor == "Mostra els contractes que tinguin el canon d’aigua industrial":
        peticion("select * from tblDatosContratoAbonado where FechaBaja is null and IDTipoAbonado2 = 'INDU'")
    elif valor == "Mostra els contractes que siguin comunitaris":
        peticion("select * from tblDatosContratoAbonado where FechaBaja is null and IDFamilia in ('10007','10008','10009')")
    elif valor == "Mostra els contractes que siguin bars i restaurants":
        peticion("select * from tblDatosContratoAbonado WHERE IDUso = 'RES' and FechaBaja is null")
    elif valor == "Mostra els contractes que siguin provisionals":
        peticion("SELECT *  FROM tblDatosContratoAbonado where FechaBaja IS NULL AND IDFamilia in ('10001','10002')")
    elif valor == "Número de OTs creades per cada treballador de Nostraigua":
        peticion("select IDUsuario,COUNT(IDOrdenTrabajo) as 'NUMERO OTs' from tblOrdenesTrabajo group by IDUsuario")
app = CTk()
app.after(0, lambda: app.state('zoomed'))





entrada1 = StringVar()

frame = CTkFrame(master=app, width=800, height=900)
frame.pack(side=LEFT, pady=10,padx=10)

SWICH = CTkSwitch(master=frame,text=" USUARIS DE BAIXA")
SWICH.pack(pady=10,padx=10)

button = CTkButton(master=frame, text="Consultar", command= lambda  :consultar())
button.pack(side=TOP, padx=10, pady=10)

borrar = CTkButton(master=frame, text="borrar", command= lambda : frametabla.destroy())
borrar.pack(side=TOP, padx=10, pady=10)

CTkButton(master=frame,text="CONSULTA SQL",command= lambda : sql() ).pack(side=TOP, padx=10, pady=10)


cabecera = CTkFrame(master=app, width=900)
cabecera.pack(side=TOP, padx=20)

opciones = CTkOptionMenu(cabecera,values= ["IDContracte","NOM","DNI","---"])
opciones.pack(side=LEFT, padx=20, pady=20)

CTkEntry(cabecera,textvariable=entrada1).pack(side=LEFT, padx=20, pady=20)

CTkButton(cabecera , text="EXPORTAR",command= lambda : exportar()).pack(side=RIGHT, padx=20, pady=20)

CTkButton(cabecera,text="CONSULTA SIMPLE",command= lambda: consultasimple(),corner_radius=100 ).pack(side=RIGHT, padx=20, pady=20)
simple = CTkComboBox(frame, values=["Mostra tots els abonats","Mostra els contractes d’alta","Mostra els contractes d’alta que no tinguin ni email ni telefon","Mostra els contractes MUNICIPALS","Mostra els contractes que tinguin COMPTADOR PARE","Mostra el rebut amb el cost més elevat de cada contracte","Mostra el numero de contractes per cada ruta","Mostra el número de comptadors per any d’instal·lació","Contractes d’alta que tinguin activades les alertes de consum","Mostra els contractes amb rebuts domicialitzats al compte bancari","Mostra els contractes que tinguin el canon d’aigua industrial"
,"Mostra els contractes que siguin comunitaris","Mostra els contractes que siguin bars i restaurants","Mostra els contractes que siguin provisionals","Número de OTs creades per cada treballador de Nostraigua"])
simple.pack(side=TOP)
app.mainloop()
