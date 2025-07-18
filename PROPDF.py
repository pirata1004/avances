import re , os

from customtkinter import CTkLabel, CTkButton, CTkEntry
from pdfminer.high_level import extract_text
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import customtkinter as ctk
from tkinter import filedialog

def seleccionar_pdf(var_destino):
    archivo = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
    if archivo:
        var_destino.set(archivo)


ruta = os.getcwd()+ "/"

def unionpdf(pdf1, pdf2):
    # Open the first PDF file
    pdf_file1 = open(pdf1,"rb")
    # Open the second PDF file
    pdf_file2 = open( pdf2,"rb")
    # Create a PDF merger
    pdf_merger = PdfMerger()
    # Add the first PDF file
    pdf_merger.append(pdf_file1)
    # Add the second PDF file
    pdf_merger.append(pdf_file2)
    # Merge the PDF files
    pdf_merger.write('merged.pdf')
    # Close the PDF files
    pdf_file1.close()
    pdf_file2.close()


def dividir_pdf_en_paginas(pdf_entrada, carpeta_salida = ruta):
    # crea carpetae
    os.makedirs(carpeta_salida, exist_ok=True)

    # Cargar el PDF
    with open(pdf_entrada, "rb") as archivo:
        lector = PdfReader(archivo)
        total_paginas = len(lector.pages)

        for i in range(total_paginas):
            escritor = PdfWriter()
            escritor.add_page(lector.pages[i])

            nombre_salida = os.path.join(carpeta_salida, f"pagina_{i + 1}.pdf")
            with open(nombre_salida, "wb") as salida:
                escritor.write(salida)

    info.set(f"PDF dividido en {total_paginas} archivos en: {carpeta_salida}")







def canviarNombre(directorio):
    # Directorio donde están los archivos PDF

    # Patrón para encontrar el número de factura
    factura_pattern = re.compile(r"OR\d{9}")
    # Recorremos todos los archivos en el directorio
    for archivo in os.listdir(directorio):
        if archivo.lower().endswith(".pdf"):
            ruta_pdf = os.path.join(directorio, archivo)
            try:
                texto = extract_text(ruta_pdf)
                coincidencias = factura_pattern.findall(texto)
                if coincidencias:
                    nuevo_nombre = coincidencias[0] + ".pdf"
                    nueva_ruta = os.path.join(directorio, nuevo_nombre)

                    os.rename(ruta_pdf, nueva_ruta)
                    info.set(f"Renombrado: {archivo} -> {nuevo_nombre}")
                else:
                    info.set(f"No se encontró número de factura en: {archivo}")
            except Exception as e:
                info.set(f"Error procesando {archivo}: {e}")



ctk.set_appearance_mode("dark")  # Opciones: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # También puedes probar: "green", "dark-blue", etc.


window = ctk.CTk()

def abrir_ventana_2():
    window.withdraw()  # Oculta la ventana 1

    ventana2 = ctk.CTk()

    entrada2 = ctk.StringVar()
    entrada3 = ctk.StringVar()

    ventana2.geometry("400x400")
    ventana2.title("unir pdf")
    CTkLabel(ventana2,text="INSERTE EL NOMBRE DE LOS PDF PARA UNIR").pack()

    ctk.CTkButton(ventana2, text="Seleccionar PDF 1", command=lambda: seleccionar_pdf(entrada2)).pack()



    boton1 = ctk.CTkButton(ventana2, text="Seleccionar PDF 2", command=lambda: seleccionar_pdf(entrada3))
    boton1.pack(pady=60)

    ventana2.protocol("WM_DELETE_WINDOW",lambda :exit())

    boton = CTkButton(ventana2, text="UNIR",  command=lambda: unionpdf(entrada2.get(),entrada3.get()) )
    boton.pack(pady=30)

    CTkButton(ventana2,text="VOLVER",command = lambda: volver()).pack()

    def volver():
        window.deiconify()  # Muestra la ventana 1
        ventana2.destroy()

    ventana2.mainloop()


def abrir_ventana_3():
    window.withdraw()  # Oculta la ventana 1

    ventana3 = ctk.CTk()
    ventana3.geometry("500x600")

    entrada2 = ctk.StringVar()
    user = ctk.StringVar()
    password = ctk.StringVar()



    CTkLabel(ventana3, text="COMPRIMIDOR DF").pack()

    ctk.CTkButton(ventana3, text="Seleccionar PDF ", command= lambda:  seleccionar_pdf(entrada2)).pack()
    CTkLabel(ventana3, text="USUARIO").pack()

    CTkLabel(ventana3, text="CONTASEÑA DF").pack()
    PASSWORD = CTkEntry(ventana3, show="*" ,textvariable=password,width=300)
    PASSWORD.pack(pady=60)

    boton = CTkButton(ventana3, text="cifrar", command=lambda: cifrado(entrada2.get(),password.get()))
    boton.pack(pady=30)

    boton = CTkButton(ventana3, text="desifrar", command=lambda: descifrar(entrada2.get(),password.get()))
    boton.pack(pady=30)

    CTkButton(ventana3, text="VOLVER", command=lambda: volver3()).pack()

    def volver3():
        window.deiconify()  # Muestra la ventana 1
        ventana3.destroy()

    print(entrada2.get())
    ventana3.protocol("WM_DELETE_WINDOW", lambda: exit())
    ventana3.mainloop()


window.title("editor de pdf")

info = ctk.StringVar(window)

window.geometry("400x400")

palabra = ctk.StringVar(window)
carpeta_salida = ctk.StringVar(window)

CTkLabel(window, text="PDF EDITOR").pack()

CTkLabel(window, text="NOM PDF").pack()

ctk.CTkEntry(window,width = 300 , textvariable=palabra).pack()

CTkLabel(window, text="NOM CARPETA SORTIDA").pack()
separarpdf = ctk.CTkEntry(window,width=300,textvariable=carpeta_salida)
separarpdf.pack()


ctk.CTkLabel(window, text="   " ,width=100,).pack()

boton = CTkButton(window, text="CANVIAR NOMBRE PDF", command=lambda : canviarNombre(ruta + carpeta_salida.get()))
boton.pack(pady=30)



prueba = CTkButton(window,text="SEPARARPDF" , command=lambda :dividir_pdf_en_paginas(palabra.get(),ruta + carpeta_salida.get()))
prueba.pack()

ctk.CTkLabel(window, textvariable=info ,width=100,).pack()

ctk.CTkButton(window,text="Unir PDF",command=lambda :abrir_ventana_2() ).pack()

cifraje = ctk.CTkButton(window,text="cifrado",command=lambda :abrir_ventana_3() )
cifraje.pack(pady=15)


window.mainloop()





