import discord
from discord.ext import commands
import yt_dlp
import os
import json
import datetime
import requests
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
        data[uid] = {"balance": 0, "inventario": [], "dni": None}


def asegurar_objeto_tienda(tienda, nombre):
    if nombre not in tienda:
        tienda[nombre] = {"precio": 0}


# --- Música ---
def get_audio_source(url):
    ydl_opts = {
        'format':
        'bestaudio',
        'quiet':
        True,
        'outtmpl':
        'song.%(ext)s',
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
    ctx.voice_client.play(discord.FFmpegPCMAudio(file),
                          after=lambda e: print("Reproducción terminada"))
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
        await ctx.send(
            f"🪪 DNI de {ctx.author.name}:\nNombre: **{dni['nombre']}**\nEdad: **{dni['edad']}**"
        )
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
    await ctx.send(
        f"🛒 Producto **{nombre}** añadido a la tienda por {precio} monedas.")


@bot.command()
async def tienda(ctx):
    tienda = cargar_json(TIENDA_FILE)
    if not tienda:
        await ctx.send("La tienda está vacía.")
        return
    lista = "\n".join(f"- {nombre}: {info['precio']} monedas"
                      for nombre, info in tienda.items())
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

    data[str(ctx.author.id)]["balance"] -= precio
    data[str(ctx.author.id)]["inventario"].append(nombre)
    guardar_json(DATA_FILE, data)

    await ctx.send(f"✅ Compraste **{nombre}** por {precio} monedas.")


# --- Deportes ---
@bot.command()
async def futbol(ctx, liga: str = "140"):
    """
    Muestra resultados de fútbol. Ligas disponibles:
    140 = La Liga, 39 = Premier League, 78 = Bundesliga, 135 = Serie A, 61 = Ligue 1
    """
    try:
        api_key = os.getenv("FOOTBALL_API_KEY")
        if not api_key:
            await ctx.send("❌ API Key no configurada. Contacta al administrador.")
            return
            
        url = f"https://v3.football.api-sports.io/fixtures"
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "v3.football.api-sports.io"
        }
        
        params = {
            "league": liga,
            "last": 5  # Últimos 5 partidos
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            await ctx.send("❌ Error al conectar con la API de fútbol.")
            return
            
        data = response.json()
        
        if not data["response"]:
            await ctx.send("❌ No se encontraron resultados para esta liga.")
            return
        
        # Nombres de ligas
        league_names = {
            "140": "La Liga 🇪🇸",
            "39": "Premier League 🇬🇧", 
            "78": "Bundesliga 🇩🇪",
            "135": "Serie A 🇮🇹",
            "61": "Ligue 1 🇫🇷"
        }
        
        league_name = league_names.get(liga, f"Liga {liga}")
        embed = discord.Embed(title=f"⚽ {league_name} - Últimos resultados", color=0x00ff00)
        
        for match in data["response"]:
            home_team = match["teams"]["home"]["name"]
            away_team = match["teams"]["away"]["name"]
            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]
            status = match["fixture"]["status"]["short"]
            date = match["fixture"]["date"]
            
            if status == "FT":  # Partido finalizado
                score = f"{home_goals}-{away_goals}"
                embed.add_field(
                    name=f"{home_team} vs {away_team}",
                    value=f"Resultado: **{score}** ✅\n📅 {date[:10]}",
                    inline=False
                )
            elif status in ["1H", "2H", "HT"]:  # Partido en curso
                score = f"{home_goals}-{away_goals}" if home_goals is not None else "0-0"
                embed.add_field(
                    name=f"{home_team} vs {away_team}",
                    value=f"En vivo: **{score}** 🔴\nEstado: {status}",
                    inline=False
                )
            else:  # Partido programado
                embed.add_field(
                    name=f"{home_team} vs {away_team}",
                    value=f"Programado ⏰\n📅 {date[:10]} {date[11:16]}",
                    inline=False
                )
        
        await ctx.send(embed=embed)
        
    except requests.exceptions.RequestException:
        await ctx.send("❌ Error de conexión con la API.")
    except Exception as e:
        await ctx.send("❌ Error al obtener los resultados de fútbol.")


@bot.command()
async def nba(ctx):
    """Muestra resultados recientes de la NBA"""
    try:
        api_key = os.getenv("FOOTBALL_API_KEY")  # Usa la misma API key
        if not api_key:
            await ctx.send("❌ API Key no configurada. Contacta al administrador.")
            return
            
        # Para NBA usaremos una API diferente o datos simulados mejorados
        # Aquí tienes datos más realistas hasta que configures una API de NBA específica
        
        embed = discord.Embed(title="🏀 NBA - Últimos resultados", color=0xff6600)
        embed.add_field(
            name="🔔 Información",
            value="Para resultados en tiempo real de NBA, se necesita configurar una API específica de baloncesto.\n\nPuedes usar `!futbol` para fútbol con datos reales.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send("❌ Error al obtener los resultados de NBA.")


@bot.command()
async def ligas(ctx):
    """Muestra las ligas disponibles para el comando !futbol"""
    embed = discord.Embed(title="⚽ Ligas disponibles", color=0x3498db)
    
    embed.add_field(
        name="🇪🇸 España",
        value="`!futbol 140` - La Liga",
        inline=True
    )
    
    embed.add_field(
        name="🇬🇧 Inglaterra", 
        value="`!futbol 39` - Premier League",
        inline=True
    )
    
    embed.add_field(
        name="🇩🇪 Alemania",
        value="`!futbol 78` - Bundesliga", 
        inline=True
    )
    
    embed.add_field(
        name="🇮🇹 Italia",
        value="`!futbol 135` - Serie A",
        inline=True
    )
    
    embed.add_field(
        name="🇫🇷 Francia",
        value="`!futbol 61` - Ligue 1",
        inline=True
    )
    
    embed.add_field(
        name="🌍 Champions League",
        value="`!futbol 2` - UEFA Champions League",
        inline=True
    )
    
    await ctx.send(embed=embed)


@bot.command()
async def equipo(ctx, *, nombre_equipo: str):
    """Busca información de un equipo específico"""
    try:
        api_key = os.getenv("FOOTBALL_API_KEY")
        if not api_key:
            await ctx.send("❌ API Key no configurada.")
            return
            
        url = "https://v3.football.api-sports.io/teams"
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "v3.football.api-sports.io"
        }
        
        params = {"search": nombre_equipo}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200 or not response.json()["response"]:
            await ctx.send("❌ Equipo no encontrado.")
            return
            
        team = response.json()["response"][0]["team"]
        
        embed = discord.Embed(title=f"⚽ {team['name']}", color=0x3498db)
        embed.set_thumbnail(url=team["logo"])
        
        embed.add_field(name="🏙️ Ciudad", value=team.get("country", "N/A"), inline=True)
        embed.add_field(name="🏟️ Fundado", value=team.get("founded", "N/A"), inline=True)
        embed.add_field(name="🌍 País", value=team.get("country", "N/A"), inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send("❌ Error al buscar el equipo.")



@bot.command()
async def division_mma(ctx, division: str = None):
    """Muestra información sobre divisiones de peso en MMA"""
    try:
        divisiones = {
            "pesado": {
                "nombre": "Peso Pesado",
                "limite": "120.2 kg (265 lbs)",
                "campeon": "Jon Jones",
                "descripcion": "Sin límite superior de peso"
            },
            "semipesado": {
                "nombre": "Peso Semipesado", 
                "limite": "93.0 kg (205 lbs)",
                "campeon": "Alex Pereira",
                "descripcion": "División de elite con grandes atletas"
            },
            "medio": {
                "nombre": "Peso Medio",
                "limite": "83.9 kg (185 lbs)", 
                "campeon": "Dricus Du Plessis",
                "descripcion": "División muy competitiva"
            },
            "welter": {
                "nombre": "Peso Wélter",
                "limite": "77.1 kg (170 lbs)",
                "campeon": "Belal Muhammad",
                "descripción": "Una de las divisiones más profundas"
            },
            "ligero": {
                "nombre": "Peso Ligero",
                "limite": "70.3 kg (155 lbs)",
                "campeon": "Islam Makhachev", 
                "descripcion": "División con más talento"
            }
        }
        
        if division:
            div_busqueda = division.lower()
            if div_busqueda in divisiones:
                div = divisiones[div_busqueda]
                embed = discord.Embed(title=f"⚖️ {div['nombre']}", color=0xff0000)
                embed.add_field(name="📏 Límite de Peso", value=div["limite"], inline=True)
                embed.add_field(name="🏆 Campeón Actual", value=div["campeon"], inline=True)
                embed.add_field(name="📝 Descripción", value=div["descripcion"], inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ División no encontrada. Usa: pesado, semipesado, medio, welter, ligero")
        else:
            embed = discord.Embed(title="⚖️ Divisiones de Peso UFC", color=0xff0000)
            for nombre, info in divisiones.items():
                embed.add_field(
                    name=f"{info['nombre']}",
                    value=f"Límite: {info['limite']}\nCampeón: {info['campeon']}",
                    inline=True
                )
            await ctx.send(embed=embed)
            
    except Exception as e:
        await ctx.send("❌ Error al mostrar las divisiones.")


# --- MMA/UFC ---
@bot.command()
async def ufc(ctx):
    """Muestra los próximos eventos de UFC"""
    try:
        # Simulación de datos hasta configurar API específica de MMA
        embed = discord.Embed(title="🥊 UFC - Próximos Eventos", color=0xdc143c)
        
        embed.add_field(
            name="UFC 307",
            value="📅 **Fecha:** 5 de Octubre 2024\n🏟️ **Lugar:** Delta Center, Salt Lake City\n🥊 **Pelea Principal:** Alex Pereira vs. Khalil Rountree Jr.",
            inline=False
        )
        
        embed.add_field(
            name="UFC 308", 
            value="📅 **Fecha:** 26 de Octubre 2024\n🏟️ **Lugar:** Etihad Arena, Abu Dhabi\n🥊 **Pelea Principal:** Ilia Topuria vs. Max Holloway",
            inline=False
        )
        
        embed.add_field(
            name="UFC 309",
            value="📅 **Fecha:** 16 de Noviembre 2024\n🏟️ **Lugar:** Madison Square Garden, Nueva York\n🥊 **Pelea Principal:** Jon Jones vs. Stipe Miocic",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Nota",
            value="Para eventos en tiempo real, configura una API específica de MMA/UFC en Secrets.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send("❌ Error al obtener eventos de UFC.")


@bot.command()
async def peleador(ctx, *, nombre: str):
    """Busca información de un peleador de MMA"""
    try:
        # Base de datos simulada de peleadores famosos
        peleadores = {
            "jon jones": {
                "nombre": "Jon Jones",
                "division": "Peso Pesado",
                "record": "27-1-0",
                "titulo": "Campeón de Peso Pesado UFC",
                "apodo": "Bones",
                "pais": "Estados Unidos",
                "edad": 37
            },
            "israel adesanya": {
                "nombre": "Israel Adesanya", 
                "division": "Peso Medio",
                "record": "24-3-0",
                "titulo": "Ex-Campeón de Peso Medio UFC",
                "apodo": "The Last Stylebender",
                "pais": "Nigeria/Nueva Zelanda",
                "edad": 35
            },
            "conor mcgregor": {
                "nombre": "Conor McGregor",
                "division": "Peso Ligero",
                "record": "22-6-0",
                "titulo": "Ex-Campeón de Peso Pluma y Ligero UFC",
                "apodo": "The Notorious",
                "pais": "Irlanda",
                "edad": 36
            },
            "khabib nurmagomedov": {
                "nombre": "Khabib Nurmagomedov",
                "division": "Peso Ligero",
                "record": "29-0-0",
                "titulo": "Ex-Campeón de Peso Ligero UFC (Retirado)",
                "apodo": "The Eagle",
                "pais": "Rusia",
                "edad": 36
            },
            "alex pereira": {
                "nombre": "Alex Pereira",
                "division": "Peso Semipesado",
                "record": "11-2-0",
                "titulo": "Campeón de Peso Semipesado UFC",
                "apodo": "Poatan",
                "pais": "Brasil",
                "edad": 37
            }
        }
        
        peleador_info = peleadores.get(nombre.lower())
        
        if not peleador_info:
            await ctx.send("❌ Peleador no encontrado en la base de datos.")
            return
        
        embed = discord.Embed(
            title=f"🥊 {peleador_info['nombre']} '{peleador_info['apodo']}'",
            color=0xdc143c
        )
        
        embed.add_field(name="🏆 Título", value=peleador_info['titulo'], inline=False)
        embed.add_field(name="⚖️ División", value=peleador_info['division'], inline=True)
        embed.add_field(name="📊 Record", value=peleador_info['record'], inline=True)
        embed.add_field(name="🌍 País", value=peleador_info['pais'], inline=True)
        embed.add_field(name="🎂 Edad", value=f"{peleador_info['edad']} años", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send("❌ Error al buscar información del peleador.")


@bot.command()
async def divisiones_ufc(ctx):
    """Muestra las divisiones de peso de UFC"""
    embed = discord.Embed(title="🥊 Divisiones de Peso UFC", color=0xdc143c)
    
    divisiones = [
        ("🪶 Peso Mosca Femenino", "115 lbs (52.2 kg)"),
        ("🐝 Peso Gallo Femenino", "135 lbs (61.2 kg)"),
        ("🪶 Peso Pluma Femenino", "145 lbs (65.8 kg)"),
        ("🥊 Peso Paja Femenino", "125 lbs (56.7 kg)"),
        ("🪶 Peso Mosca", "125 lbs (56.7 kg)"),
        ("🐝 Peso Gallo", "135 lbs (61.2 kg)"),
        ("🪶 Peso Pluma", "145 lbs (65.8 kg)"),
        ("⚡ Peso Ligero", "155 lbs (70.3 kg)"),
        ("🌟 Peso Wélter", "170 lbs (77.1 kg)"),
        ("🥊 Peso Medio", "185 lbs (83.9 kg)"),
        ("💪 Peso Semipesado", "205 lbs (93.0 kg)"),
        ("🏔️ Peso Pesado", "265 lbs (120.2 kg)")
    ]
    
    for division, peso in divisiones:
        embed.add_field(name=division, value=peso, inline=True)
    
    await ctx.send(embed=embed)


@bot.command()
async def ranking_ufc(ctx, division: str = "p4p"):
    """
    Muestra el ranking de una división específica
    Divisiones: p4p, pesado, semipesado, medio, welter, ligero, pluma, gallo, mosca
    """
    try:
        rankings = {
            "p4p": {
                "titulo": "🏆 Ranking Libra por Libra",
                "peleadores": [
                    "1. Islam Makhachev",
                    "2. Alexander Volkanovski", 
                    "3. Jon Jones",
                    "4. Leon Edwards",
                    "5. Alex Pereira"
                ]
            },
            "pesado": {
                "titulo": "🏔️ Peso Pesado",
                "peleadores": [
                    "C. Jon Jones",
                    "1. Stipe Miocic",
                    "2. Tom Aspinall",
                    "3. Curtis Blaydes",
                    "4. Sergei Pavlovich"
                ]
            },
            "semipesado": {
                "titulo": "💪 Peso Semipesado", 
                "peleadores": [
                    "C. Alex Pereira",
                    "1. Jamahal Hill",
                    "2. Jiří Procházka",
                    "3. Magomed Ankalaev",
                    "4. Jan Błachowicz"
                ]
            },
            "ligero": {
                "titulo": "⚡ Peso Ligero",
                "peleadores": [
                    "C. Islam Makhachev",
                    "1. Arman Tsarukyan",
                    "2. Charles Oliveira",
                    "3. Justin Gaethje",
                    "4. Dustin Poirier"
                ]
            }
        }
        
        ranking_info = rankings.get(division.lower())
        
        if not ranking_info:
            divisiones_disponibles = ", ".join(rankings.keys())
            await ctx.send(f"❌ División no encontrada.\nDisponibles: {divisiones_disponibles}")
            return
        
        embed = discord.Embed(
            title=ranking_info["titulo"],
            color=0xdc143c
        )
        
        ranking_text = "\n".join(ranking_info["peleadores"])
        embed.add_field(name="Top 5", value=ranking_text, inline=False)
        
        embed.add_field(
            name="ℹ️ Leyenda",
            value="C. = Campeón\n1-15 = Ranking oficial",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send("❌ Error al mostrar el ranking.")


@bot.command()
async def records_ufc(ctx):
    """Muestra récords históricos de UFC"""
    embed = discord.Embed(title="📊 Récords Históricos UFC", color=0xdc143c)
    
    embed.add_field(
        name="🏆 Más Defensas de Título",
        value="1. Anderson Silva - 10 defensas\n2. Demetrious Johnson - 11 defensas\n3. Jon Jones - 8 defensas",
        inline=False
    )
    
    embed.add_field(
        name="⚡ KO Más Rápido",
        value="Jorge Masvidal vs. Ben Askren\n5 segundos (UFC 239)",
        inline=True
    )
    
    embed.add_field(
        name="🏃 Sumisión Más Rápida",
        value="Oleg Taktarov vs. Anthony Macias\n9 segundos (UFC 6)",
        inline=True
    )
    
    embed.add_field(
        name="🔥 Más Peleas en UFC",
        value="Jim Miller - 41 peleas",
        inline=True
    )
    
    embed.add_field(
        name="🎯 Más Finalizaciones",
        value="Donald Cerrone - 23 finalizaciones",
        inline=True
    )
    
    embed.add_field(
        name="🥊 Más KOs",
        value="Derrick Lewis - 13 KOs",
        inline=True
    )
    
    embed.add_field(
        name="🤼 Más Sumisiones",
        value="Charles Oliveira - 16 sumisiones",
        inline=True
    )
    
    await ctx.send(embed=embed)


# --- Pokémon ---
@bot.command()
async def pokemon(ctx, nombre: str):
    """Busca información de un Pokémon"""
    try:
        url = f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}"
        response = requests.get(url)
        
        if response.status_code == 404:
            await ctx.send("❌ Pokémon no encontrado.")
            return
            
        data = response.json()
        
        # Obtener información de la especie para la descripción
        species_url = data["species"]["url"]
        species_response = requests.get(species_url)
        species_data = species_response.json()
        
        # Buscar descripción en español
        description = "Sin descripción disponible"
        for entry in species_data["flavor_text_entries"]:
            if entry["language"]["name"] == "es":
                description = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                break
        
        embed = discord.Embed(
            title=f"🔍 {data['name'].capitalize()}",
            description=description,
            color=0xff0000
        )
        
        embed.set_thumbnail(url=data["sprites"]["front_default"])
        
        # Información básica
        embed.add_field(name="ID", value=data["id"], inline=True)
        embed.add_field(name="Altura", value=f"{data['height']/10} m", inline=True)
        embed.add_field(name="Peso", value=f"{data['weight']/10} kg", inline=True)
        
        # Tipos
        tipos = [tipo["type"]["name"].capitalize() for tipo in data["types"]]
        embed.add_field(name="Tipos", value=" / ".join(tipos), inline=False)
        
        # Estadísticas base
        stats = ""
        for stat in data["stats"]:
            stat_name = stat["stat"]["name"].replace("-", " ").title()
            stats += f"{stat_name}: {stat['base_stat']}\n"
        
        embed.add_field(name="Estadísticas Base", value=stats, inline=False)
        
        await ctx.send(embed=embed)
        
    except requests.exceptions.RequestException:
        await ctx.send("❌ Error de conexión con la API de Pokémon.")
    except Exception as e:
        await ctx.send("❌ Error al buscar el Pokémon.")


@bot.command()
async def pokemon_random(ctx):
    """Muestra un Pokémon aleatorio"""
    try:
        import random
        pokemon_id = random.randint(1, 1010)  # Hasta la Gen 9
        
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
        response = requests.get(url)
        data = response.json()
        
        embed = discord.Embed(
            title=f"🎲 Pokémon Aleatorio: {data['name'].capitalize()}",
            color=0x3498db
        )
        
        embed.set_image(url=data["sprites"]["front_default"])
        
        embed.add_field(name="ID", value=data["id"], inline=True)
        embed.add_field(name="Altura", value=f"{data['height']/10} m", inline=True)
        embed.add_field(name="Peso", value=f"{data['weight']/10} kg", inline=True)
        
        tipos = [tipo["type"]["name"].capitalize() for tipo in data["types"]]
        embed.add_field(name="Tipos", value=" / ".join(tipos), inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send("❌ Error al obtener Pokémon aleatorio.")


@bot.command()
async def tipo_pokemon(ctx, tipo: str):
    """Muestra información sobre un tipo de Pokémon"""
    try:
        url = f"https://pokeapi.co/api/v2/type/{tipo.lower()}"
        response = requests.get(url)
        
        if response.status_code == 404:
            await ctx.send("❌ Tipo de Pokémon no encontrado.")
            return
            
        data = response.json()
        
        embed = discord.Embed(
            title=f"⚡ Tipo: {data['name'].capitalize()}",
            color=0x9b59b6
        )
        
        # Efectividad
        super_effective = [rel["name"].capitalize() for rel in data["damage_relations"]["double_damage_to"]]
        not_very_effective = [rel["name"].capitalize() for rel in data["damage_relations"]["half_damage_to"]]
        no_effect = [rel["name"].capitalize() for rel in data["damage_relations"]["no_damage_to"]]
        
        if super_effective:
            embed.add_field(name="Súper efectivo contra", value=", ".join(super_effective), inline=False)
        if not_very_effective:
            embed.add_field(name="Poco efectivo contra", value=", ".join(not_very_effective), inline=False)
        if no_effect:
            embed.add_field(name="No afecta a", value=", ".join(no_effect), inline=False)
            
        # Algunos Pokémon de este tipo
        pokemon_list = [p["pokemon"]["name"].capitalize() for p in data["pokemon"][:5]]
        embed.add_field(name="Algunos Pokémon de este tipo", value=", ".join(pokemon_list), inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send("❌ Error al buscar información del tipo.")


# --- Moderación ---
@bot.command()
@commands.has_permissions(administrator=True)
async def limpiar(ctx, cantidad: int = None):
    """Borra mensajes del canal. Si no se especifica cantidad, borra todos."""
    try:
        if cantidad is None:
            # Borrar todos los mensajes
            deleted = await ctx.channel.purge()
            await ctx.send(f"🧹 Se borraron {len(deleted)} mensajes del canal.", delete_after=5)
        else:
            if cantidad <= 0:
                await ctx.send("❌ La cantidad debe ser mayor a 0.")
                return
            if cantidad > 100:
                await ctx.send("❌ No puedes borrar más de 100 mensajes a la vez.")
                return
            
            # Borrar cantidad específica de mensajes
            deleted = await ctx.channel.purge(limit=cantidad + 1)  # +1 para incluir el comando
            await ctx.send(f"🧹 Se borraron {len(deleted) - 1} mensajes.", delete_after=5)
            
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para borrar mensajes.")
    except discord.HTTPException:
        await ctx.send("❌ Error al borrar mensajes. Los mensajes muy antiguos no se pueden borrar.")


@bot.command()
@commands.has_permissions(administrator=True)
async def limpiar_usuario(ctx, miembro: discord.Member, cantidad: int = 50):
    """Borra mensajes de un usuario específico en el canal"""
    try:
        def check_user(message):
            return message.author == miembro
        
        deleted = await ctx.channel.purge(limit=cantidad, check=check_user)
        await ctx.send(f"🧹 Se borraron {len(deleted)} mensajes de {miembro.mention}.", delete_after=5)
        
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para borrar mensajes.")
    except discord.HTTPException:
        await ctx.send("❌ Error al borrar mensajes.")


# --- Calculadora ---
@bot.command()
async def calc(ctx, *, expresion: str):
    """Calculadora básica - Ejemplo: !calc 2 + 2 * 3"""
    try:
        # Limpiar la expresión de caracteres peligrosos
        expresion = expresion.replace(" ", "")
        allowed_chars = "0123456789+-*/.()^"
        
        if not all(c in allowed_chars for c in expresion):
            await ctx.send("❌ Solo se permiten números y operadores básicos (+, -, *, /, ^, paréntesis)")
            return
        
        # Reemplazar ^ por ** para potencias
        expresion = expresion.replace("^", "**")
        
        # Evaluar la expresión de forma segura
        resultado = eval(expresion)
        
        embed = discord.Embed(title="🧮 Calculadora", color=0x3498db)
        embed.add_field(name="Operación", value=f"`{expresion.replace('**', '^')}`", inline=False)
        embed.add_field(name="Resultado", value=f"**{resultado}**", inline=False)
        
        await ctx.send(embed=embed)
        
    except ZeroDivisionError:
        await ctx.send("❌ Error: División por cero.")
    except Exception:
        await ctx.send("❌ Expresión matemática inválida.")


@bot.command()
async def raiz(ctx, numero: float):
    """Calcula la raíz cuadrada de un número"""
    try:
        if numero < 0:
            await ctx.send("❌ No se puede calcular la raíz cuadrada de un número negativo.")
            return
        
        import math
        resultado = math.sqrt(numero)
        
        embed = discord.Embed(title="🧮 Raíz Cuadrada", color=0x3498db)
        embed.add_field(name="Número", value=f"`{numero}`", inline=True)
        embed.add_field(name="Resultado", value=f"**{resultado:.6f}**", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception:
        await ctx.send("❌ Error al calcular la raíz cuadrada.")


@bot.command()
async def potencia(ctx, base: float, exponente: float):
    """Calcula una potencia - Ejemplo: !potencia 2 3"""
    try:
        resultado = base ** exponente
        
        embed = discord.Embed(title="🧮 Potencia", color=0x3498db)
        embed.add_field(name="Base", value=f"`{base}`", inline=True)
        embed.add_field(name="Exponente", value=f"`{exponente}`", inline=True)
        embed.add_field(name="Resultado", value=f"**{resultado}**", inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception:
        await ctx.send("❌ Error al calcular la potencia.")


@bot.command()
async def porcentaje(ctx, numero: float, porcentaje: float):
    """Calcula el porcentaje de un número - Ejemplo: !porcentaje 200 15"""
    try:
        resultado = (numero * porcentaje) / 100
        
        embed = discord.Embed(title="🧮 Porcentaje", color=0x3498db)
        embed.add_field(name="Número", value=f"`{numero}`", inline=True)
        embed.add_field(name="Porcentaje", value=f"`{porcentaje}%`", inline=True)
        embed.add_field(name="Resultado", value=f"**{resultado}**", inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception:
        await ctx.send("❌ Error al calcular el porcentaje.")


@bot.command()
async def factorial(ctx, numero: int):
    """Calcula el factorial de un número"""
    try:
        if numero < 0:
            await ctx.send("❌ El factorial no está definido para números negativos.")
            return
        
        if numero > 20:
            await ctx.send("❌ Número demasiado grande (máximo 20).")
            return
        
        import math
        resultado = math.factorial(numero)
        
        embed = discord.Embed(title="🧮 Factorial", color=0x3498db)
        embed.add_field(name="Número", value=f"`{numero}!`", inline=True)
        embed.add_field(name="Resultado", value=f"**{resultado:,}**", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception:
        await ctx.send("❌ Error al calcular el factorial.")


@bot.command()
async def convertir(ctx, tipo: str, valor: float):
    """
    Conversiones de unidades
    Tipos: celsius_fahrenheit, fahrenheit_celsius, km_millas, millas_km, kg_libras, libras_kg
    """
    try:
        conversiones = {
            "celsius_fahrenheit": lambda c: (c * 9/5) + 32,
            "fahrenheit_celsius": lambda f: (f - 32) * 5/9,
            "km_millas": lambda km: km * 0.621371,
            "millas_km": lambda mi: mi / 0.621371,
            "kg_libras": lambda kg: kg * 2.20462,
            "libras_kg": lambda lb: lb / 2.20462
        }
        
        if tipo not in conversiones:
            tipos_disponibles = ", ".join(conversiones.keys())
            await ctx.send(f"❌ Tipo de conversión no válido.\nDisponibles: {tipos_disponibles}")
            return
        
        resultado = conversiones[tipo](valor)
        
        # Nombres más legibles
        nombres = {
            "celsius_fahrenheit": ("°C", "°F"),
            "fahrenheit_celsius": ("°F", "°C"),
            "km_millas": ("km", "millas"),
            "millas_km": ("millas", "km"),
            "kg_libras": ("kg", "libras"),
            "libras_kg": ("libras", "kg")
        }
        
        unidad_origen, unidad_destino = nombres[tipo]
        
        embed = discord.Embed(title="🔄 Conversión", color=0x3498db)
        embed.add_field(name="Valor original", value=f"`{valor} {unidad_origen}`", inline=True)
        embed.add_field(name="Resultado", value=f"**{resultado:.4f} {unidad_destino}**", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception:
        await ctx.send("❌ Error en la conversión.")


# --- Comando de ayuda personalizado ---
@bot.command()
async def comandos(ctx):
    """Muestra todos los comandos disponibles"""
    embed = discord.Embed(title="📋 Lista de Comandos", color=0x00ff00)
    
    embed.add_field(
        name="🎵 Música",
        value="`!join` - Unirse al canal\n`!play <url>` - Reproducir música\n`!pause` - Pausar\n`!resume` - Reanudar\n`!stop` - Parar y desconectar",
        inline=False
    )
    
    embed.add_field(
        name="💰 Economía",
        value="`!balance` - Ver monedas\n`!daily` - Reclamar recompensa diaria\n`!addmoney <usuario> <cantidad>` - Añadir dinero (admin)\n`!multa <usuario> <cantidad>` - Multar usuario (admin)",
        inline=False
    )
    
    embed.add_field(
        name="🛒 Tienda",
        value="`!tienda` - Ver productos\n`!comprar <producto>` - Comprar producto\n`!addproducto <nombre> <precio>` - Añadir producto (admin)",
        inline=False
    )
    
    embed.add_field(
        name="🎒 Inventario",
        value="`!inventario` - Ver inventario\n`!additem <nombre>` - Añadir item",
        inline=False
    )
    
    embed.add_field(
        name="🪪 DNI",
        value="`!crear_dni <nombre> <edad>` - Crear DNI\n`!ver_dni` - Ver tu DNI",
        inline=False
    )
    
    embed.add_field(
        name="⚽ Deportes",
        value="`!futbol [liga]` - Resultados de fútbol\n`!ligas` - Ver ligas disponibles\n`!equipo <nombre>` - Info de equipo\n`!nba` - Resultados de NBA\n`!ufc` - Eventos de UFC\n`!peleador <nombre>` - Info de peleador\n`!division_mma [división]` - Divisiones de peso",
        inline=False
    )
    
    embed.add_field(
        name="🥊 MMA/UFC",
        value="`!ufc` - Próximos eventos UFC\n`!peleador <nombre>` - Info de peleador\n`!divisiones_ufc` - Divisiones de peso\n`!ranking_ufc [división]` - Rankings\n`!records_ufc` - Récords históricos",
        inline=False
    )
    
    embed.add_field(
        name="🔍 Pokémon",
        value="`!pokemon <nombre>` - Info de Pokémon\n`!pokemon_random` - Pokémon aleatorio\n`!tipo_pokemon <tipo>` - Info de tipo",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Moderación (Admin)",
        value="`!limpiar [cantidad]` - Borrar mensajes del canal\n`!limpiar_usuario <usuario> [cantidad]` - Borrar mensajes de un usuario",
        inline=False
    )
    
    embed.add_field(
        name="🧮 Calculadora",
        value="`!calc <expresión>` - Calculadora básica\n`!raiz <número>` - Raíz cuadrada\n`!potencia <base> <exp>` - Potencias\n`!porcentaje <num> <%>` - Porcentajes\n`!factorial <número>` - Factorial\n`!convertir <tipo> <valor>` - Conversiones",
        inline=False
    )
    
    await ctx.send(embed=embed)


# --- MAIN ---
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("TOKEN")
    bot.run(TOKEN)
