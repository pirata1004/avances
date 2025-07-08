¡Claro! Te ampliaré el bot con:

---

## Nuevas funcionalidades

### 1. Tienda con administración

* Comando para que **admins añadan objetos a la tienda** con nombre y precio.
* Comando para que los usuarios **compren** objetos si tienen dinero.

### 2. Añadir dinero a usuarios (solo admins)

* Comando para que admins den dinero a cualquier usuario.

### 3. Sistema de multas

* Comando para que admins **multen a usuarios**, restándoles dinero.

---

## Cómo funciona el guardado de datos

* Toda la información (usuarios, balances, inventarios, DNI) está en `usuarios.json`.
* La tienda se guarda en `tienda.json`.
* Los cooldowns (como el daily) están en `cooldowns.json`.
* Estos archivos se **leen y escriben en disco** automáticamente cada vez que haces cambios.
* Para que no se pierda nada, **no cierres el programa sin detenerlo correctamente** (Ctrl+C en consola) o que el hosting mantenga archivos.

Si usas hosting gratuito tipo Replit o Railway, estos archivos se guardan en el entorno de tu proyecto, pero **pueden borrarse si el contenedor se reinicia**.
Por eso, para producción, una base de datos (SQLite, Mongo, etc.) es mejor, pero para pruebas funciona muy bien.

---

## Código actualizado con lo pedido

```python
import discord
from discord.ext import commands
import yt_dlp
import os
import json
import asyncio
import datetime
from flask import Flask
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = "usuarios.json"
COOLDOWN_FILE = "cooldowns.json"
TIENDA_FILE = "tienda.json"

# --- Flask para keep alive ---
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot activo."

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run_flask).start()

# --- Funciones básicas ---

def cargar_json(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump({}, f)
    with open(file, "r") as f:
        return json.load(f)

def guardar_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def asegurar_usuario(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "balance": 0,
            "inventario": [],
            "dni": None
        }

def asegurar_objeto_tienda(tienda, nombre):
    if nombre not in tienda:
        tienda[nombre] = {"precio": 0}

# --- Música ---

def get_audio_source(url):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return "song.mp3", info.get("title", "Canción")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("🔊 Conectado al canal de voz.")
    else:
        await ctx.send("❌ Debes estar en un canal de voz.")

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.invoke(bot.get_command("join"))

    await ctx.send("🎵 Cargando...")
    file, title = get_audio_source(url)
    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(file), after=lambda e: print("Reproducción terminada"))
    await ctx.send(f"▶️ Reproduciendo: **{title}**")

@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Pausado.")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Reanudado.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 Desconectado.")

# --- Economía básica ---

@bot.command()
async def balance(ctx):
    data = cargar_json(DATA_FILE)
    asegurar_usuario(data, ctx.author.id)
    guardar_json(DATA_FILE, data)
    b = data[str(ctx.author.id)]["balance"]
    await ctx.send(f"💼 {ctx.author.name}, tienes **{b} monedas**.")

@bot.command()
async def daily(ctx):
    now = datetime.datetime.utcnow()
    uid = str(ctx.author.id)

    cooldowns = cargar_json(COOLDOWN_FILE)

    last = cooldowns.get(uid)
    if last:
        last_time = datetime.datetime.fromisoformat(last)
        if (now - last_time).total_seconds() < 86400:
            await ctx.send("⏳ Ya reclamaste tu daily hoy.")
            return

    data = cargar_json(DATA_FILE)
    asegurar_usuario(data, ctx.author.id)
    data[uid]["balance"] += 100
    guardar_json(DATA_FILE, data)

    cooldowns[uid] = now.isoformat()
    guardar_json(COOLDOWN_FILE, cooldowns)

    await ctx.send("🎁 Recibiste 100 monedas diarias.")

@bot.command()
@commands.has_permissions(administrator=True)
async def addmoney(ctx, miembro: discord.Member, cantidad: int):
    if cantidad <= 0:
        await ctx.send("❌ Cantidad inválida.")
        return
    data = cargar_json(DATA_FILE)
    asegurar_usuario(data, miembro.id)
    data[str(miembro.id)]["balance"] += cantidad
    guardar_json(DATA_FILE, data)
    await ctx.send(f"💰 Se agregaron {cantidad} monedas a {miembro.name}.")

@bot.command()
@commands.has_permissions(administrator=True)
async def multa(ctx, miembro: discord.Member, cantidad: int):
    if cantidad <= 0:
        await ctx.send("❌ Cantidad inválida.")
        return
    data = cargar_json(DATA_FILE)
    asegurar_usuario(data, miembro.id)
    if data[str(miembro.id)]["balance"] < cantidad:
        await ctx.send("❌ El usuario no tiene suficiente dinero para la multa.")
        return
    data[str(miembro.id)]["balance"] -= cantidad
    guardar_json(DATA_FILE, data)
    await ctx.send(f"🚨 {miembro.name} fue multado con {cantidad} monedas.")

# --- Inventario ---

@bot.command()
async def additem(ctx, *, nombre: str):
    data = cargar_json(DATA_FILE)
    asegurar_usuario(data, ctx.author.id)
    data[str(ctx.author.id)]["inventario"].append(nombre)
    guardar_json(DATA_FILE, data)
    await ctx.send(f"📦 Añadido **{nombre}** a tu inventario.")

@bot.command()
async def inventario(ctx):
    data = cargar_json(DATA_FILE)
    asegurar_usuario(data, ctx.author.id)
    inv = data[str(ctx.author.id)]["inventario"]
    if inv:
        lista = "\n".join(f"- {item}" for item in inv)
        await ctx.send(f"🎒 Tu inventario:\n{lista}")
    else:
        await ctx.send("🎒 Tu inventario está vacío.")

# --- DNI ---

@bot.command()
async def crear_dni(ctx, nombre: str, edad: int):
    data = cargar_json(DATA_FILE)
    asegurar_usuario(data, ctx.author.id)
    data[str(ctx.author.id)]["dni"] = {"nombre": nombre, "edad": edad}
    guardar_json(DATA_FILE, data)
    await ctx.send("🪪 DNI creado.")

@bot.command()
async def ver_dni(ctx):
    data = cargar_json(DATA_FILE)
    asegurar_usuario(data, ctx.author.id)
    dni = data[str(ctx.author.id)]["dni"]
    if dni:
        await ctx.send(f"🪪 DNI de {ctx.author.name}:\nNombre: **{dni['nombre']}**\nEdad: **{dni['edad']}**")
    else:
        await ctx.send("❌ No tienes DNI. Usa `!crear_dni <nombre> <edad>`.")

# --- Tienda ---

@bot.command()
@commands.has_permissions(administrator=True)
async def addproducto(ctx, nombre: str, precio: int):
    if precio <= 0:
        await ctx.send("❌ Precio inválido.")
        return
    tienda = cargar_json(TIENDA_FILE)
    tienda[nombre] = {"precio": precio}
    guardar_json(TIENDA_FILE, tienda)
    await ctx.send(f"🛒 Producto **{nombre}** añadido a la tienda por {precio} monedas.")

@bot.command()
async def tienda(ctx):
    tienda = cargar_json(TIENDA_FILE)
    if not tienda:
        await ctx.send("La tienda está vacía.")
        return
    lista = "\n".join(f"- {nombre}: {info['precio']} monedas" for nombre, info in tienda.items())
    await ctx.send(f"🛒 **Tienda:**\n{lista}")

@bot.command()
async def comprar(ctx, nombre: str):
    tienda = cargar_json(TIENDA_FILE)
    if nombre not in tienda:
        await ctx.send("❌ Producto no encontrado.")
        return
    precio = tienda[nombre]["precio"]

    data = cargar_json(DATA_FILE)
    asegurar_usuario(data, ctx.author.id)

    if data[str(ctx.author.id)]["balance"] < precio:
        await ctx.send("❌ No tienes suficiente dinero.")
        return

    data[str(ctx.author.id)]["balance
```
