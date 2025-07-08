import re , os
from pdfminer.high_level import extract_text
from PyPDF2 import PdfReader, PdfWriter ,PdfMerger
import tkinter as tk

ruta = os.getcwd()+ "/"

def unionpdf():
    # Open the first PDF file
    pdf_file1 = open('example1.pdf', 'rb')
    # Open the second PDF file
    pdf_file2 = open('example2.pdf', 'rb')
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


def dividir_pdf_en_paginas(pdf_entrada, carpeta_salida):
    # crea carpeta
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




window = tk.Tk()
window.title("editor de pdf")

info = tk.StringVar(window)

window.geometry("400x400")

palabra = tk.StringVar(window)
carpeta_salida = tk.StringVar(window)

tk.Label(window, text="PDF EDITOR").pack()

tk.Label(window, text="NOM PDF").pack()

tk.Entry(window,width = 30 , textvariable=palabra).pack()

tk.Label(window, text="NOM CARPETA SORTIDA").pack()
separarpdf =tk.Entry(window,width=30,textvariable=carpeta_salida)
separarpdf.pack()




boton = tk.Button(window, text="CANVIAR NOMBRE PDF", command=lambda : canviarNombre(ruta + carpeta_salida.get()))
boton.pack()

prueba = tk.Button(window,text="SEPARARPDF" , command=lambda :dividir_pdf_en_paginas(palabra.get(),ruta + carpeta_salida.get()))
prueba.pack()

tk.Label(window, textvariable=info ,width=100,).pack()

tk.Button(window,text="Unir PDF").pack()



window.mainloop()

