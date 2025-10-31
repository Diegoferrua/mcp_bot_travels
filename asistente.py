"""
🌴 AGENTE DE PLANIFICACIÓN DE VACACIONES
Sistema inteligente para planificar vacaciones perfectas
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import random

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Cargar variables de entorno
load_dotenv()

# ============================================================================
# BASE DE DATOS DE VIAJEROS
# ============================================================================

class ViajerosDB:
    """Base de datos en memoria para gestionar viajeros"""
    def __init__(self):
        self.viajeros: List[Dict[str, Any]] = []
        self.contador = 1
    
    def agregar(self, nombre: str, edad: int, tipo: str = "adulto") -> Dict:
        viajero = {
            "id": self.contador,
            "nombre": nombre,
            "edad": edad,
            "tipo": tipo,  # adulto, niño, bebé
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.viajeros.append(viajero)
        self.contador += 1
        return viajero
    
    def listar(self) -> List[Dict]:
        return self.viajeros
    
    def limpiar(self):
        self.viajeros = []
        self.contador = 1
    
    def contar_por_tipo(self) -> Dict[str, int]:
        conteo = {"adulto": 0, "niño": 0, "bebé": 0}
        for v in self.viajeros:
            conteo[v["tipo"]] = conteo.get(v["tipo"], 0) + 1
        return conteo

# Instancia global
viajeros_db = ViajerosDB()

# ============================================================================
# HERRAMIENTA 1: GESTIÓN DE VIAJEROS
# ============================================================================

class ViajeroInput(BaseModel):
    """Input para gestión de viajeros"""
    accion: str = Field(description="Acción: 'agregar', 'listar', 'limpiar'")
    nombre: Optional[str] = Field(default=None, description="Nombre del viajero")
    edad: Optional[int] = Field(default=None, description="Edad del viajero")

@tool("gestionar_viajeros", args_schema=ViajeroInput)
def gestionar_viajeros(
    accion: str,
    nombre: Optional[str] = None,
    edad: Optional[int] = None
) -> str:
    """
    Gestiona la lista de viajeros para el viaje.
    Clasifica automáticamente: adulto (18+), niño (2-17), bebé (0-1)
    """
    
    if accion == "agregar":
        if not nombre or edad is None:
            return "❌ Necesito nombre y edad del viajero"
        
        # Clasificar por edad
        if edad >= 18:
            tipo = "adulto"
        elif edad >= 2:
            tipo = "niño"
        else:
            tipo = "bebé"
        
        viajero = viajeros_db.agregar(nombre, edad, tipo)
        return f"✅ Viajero agregado: {nombre} ({edad} años) - Categoría: {tipo}"
    
    elif accion == "listar":
        viajeros = viajeros_db.listar()
        if not viajeros:
            return "👥 No hay viajeros registrados aún"
        
        conteo = viajeros_db.contar_por_tipo()
        resultado = f"👥 Viajeros registrados ({len(viajeros)} total):\n"
        resultado += f"   👨‍👩‍👧‍👦 Adultos: {conteo['adulto']} | Niños: {conteo['niño']} | Bebés: {conteo['bebé']}\n\n"
        
        for v in viajeros:
            emoji = "👨" if v["tipo"] == "adulto" else "👶" if v["tipo"] == "bebé" else "🧒"
            resultado += f"{emoji} {v['nombre']} - {v['edad']} años ({v['tipo']})\n"
        return resultado
    
    elif accion == "limpiar":
        viajeros_db.limpiar()
        return "🗑️ Lista de viajeros limpiada"
    
    else:
        return f"❌ Acción no válida: {accion}"

# ============================================================================
# HERRAMIENTA 2: BÚSQUEDA DE VUELOS
# ============================================================================

def obtener_codigo_iata(ciudad: str) -> Optional[str]:
    """Obtiene el código IATA de una ciudad"""
    codigos_comunes = {
        # Sudamérica
        "lima": "LIM", "cusco": "CUZ", "cuzco": "CUZ", "arequipa": "AQP",
        "buenos aires": "BUE", "santiago": "SCL", 
        "bogota": "BOG", "bogotá": "BOG",  # Con y sin acento
        "medellin": "MDE", "medellín": "MDE",
        "cartagena": "CTG", 
        "quito": "UIO", 
        "guayaquil": "GYE", 
        "rio de janeiro": "GIG", "río de janeiro": "GIG",
        "sao paulo": "GRU", "são paulo": "GRU",
        "brasilia": "BSB", "brasília": "BSB",
        "montevideo": "MVD", 
        "asuncion": "ASU", "asunción": "ASU",
        "la paz": "LPB", "caracas": "CCS",
        
        # Norteamérica
        "new york": "NYC", "nueva york": "NYC", "miami": "MIA",
        "los angeles": "LAX", "chicago": "CHI", "houston": "HOU",
        "san francisco": "SFO", "washington": "WAS", "boston": "BOS",
        "las vegas": "LAS", "orlando": "MCO", "seattle": "SEA",
        "mexico": "MEX", "cancun": "CUN", "guadalajara": "GDL",
        "toronto": "YYZ", "vancouver": "YVR", "montreal": "YUL",
        
        # Europa
        "madrid": "MAD", "barcelona": "BCN", "sevilla": "SVQ",
        "paris": "PAR", "parís": "PAR",
        "londres": "LON", "london": "LON",
        "roma": "ROM", 
        "milan": "MIL", "milán": "MIL",
        "berlin": "BER", "berlín": "BER",
        "amsterdam": "AMS", "ámsterdam": "AMS",
        "bruselas": "BRU", 
        "viena": "VIE", 
        "praga": "PRG", 
        "lisboa": "LIS", 
        "dublin": "DUB", "dublín": "DUB",
        "atenas": "ATH", 
        "estambul": "IST", "istanbul": "IST",
        "moscu": "MOW", "moscú": "MOW",
        "zurich": "ZRH", "zúrich": "ZRH",
        
        # Asia
        "tokyo": "TYO", "tokio": "TYO", "toquio": "TYO",
        "bangkok": "BKK", 
        "singapur": "SIN", "singapore": "SIN",
        "hong kong": "HKG", 
        "dubai": "DXB", "dubái": "DXB",
        "delhi": "DEL", 
        "mumbai": "BOM", "bombay": "BOM",
        "shanghai": "SHA", "shanghái": "SHA",
        "beijing": "BJS", "pekín": "BJS", "pekin": "BJS",
        "seul": "SEL", "seoul": "SEL",
        "taipei": "TPE", 
        "manila": "MNL",
        
        # Oceanía
        "sydney": "SYD", "melbourne": "MEL", "auckland": "AKL",
    }
    return codigos_comunes.get(ciudad.lower())

def buscar_vuelos_amadeus(origen_iata: str, destino_iata: str, fecha_ida: str, 
                          fecha_vuelta: Optional[str], num_adultos: int) -> Optional[Dict]:
    """Busca vuelos usando Amadeus API"""
    try:
        # Obtener credenciales
        amadeus_key = os.getenv("AMADEUS_API_KEY")
        amadeus_secret = os.getenv("AMADEUS_API_SECRET")
        
        if not amadeus_key or not amadeus_secret:
            # print("Amadeus API no configurada")
            return None
        
        # 1. Obtener token de acceso
        auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": amadeus_key,
            "client_secret": amadeus_secret
        }
        
        auth_response = requests.post(auth_url, data=auth_data, timeout=10)
        if auth_response.status_code != 200:
            # print(f"Error auth Amadeus: {auth_response.status_code}")
            # print(f"Respuesta: {auth_response.text}")
            return None
        
        token = auth_response.json()["access_token"]
        
        # 2. Buscar vuelos
        search_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {token}"}
        
        params = {
            "originLocationCode": origen_iata,
            "destinationLocationCode": destino_iata,
            "departureDate": fecha_ida,
            "adults": num_adultos,
            "max": 5
        }
        
        if fecha_vuelta:
            params["returnDate"] = fecha_vuelta
        
        # print(f"Buscando vuelos: {origen_iata}->{destino_iata}, {fecha_ida}, {num_adultos} adultos")
        search_response = requests.get(search_url, headers=headers, params=params, timeout=15)
        
        if search_response.status_code == 200:
            data = search_response.json()
            # print(f"Encontrados {len(data.get('data', []))} vuelos")
            return data
        else:
            # print(f"Error busqueda Amadeus: {search_response.status_code}")
            # print(f"Respuesta: {search_response.text}")
            pass
        
        return None
        
    except Exception as e:
        # print(f"Error en Amadeus API: {e}")
        # import traceback
        # traceback.print_exc()
        return None

class VueloInput(BaseModel):
    """Input para búsqueda de vuelos"""
    origen: str = Field(description="Ciudad de origen (ej: 'Lima', 'Madrid')")
    destino: str = Field(description="Ciudad de destino")
    fecha_ida: str = Field(description="Fecha de ida (YYYY-MM-DD)")
    fecha_vuelta: Optional[str] = Field(default=None, description="Fecha de vuelta (YYYY-MM-DD)")

@tool("buscar_vuelos", args_schema=VueloInput)
def buscar_vuelos(
    origen: str,
    destino: str,
    fecha_ida: str,
    fecha_vuelta: Optional[str] = None
) -> str:
    """
    Busca vuelos disponibles entre dos ciudades usando Amadeus API.
    Si la API no está disponible, usa datos simulados realistas.
    Retorna opciones con precios reales o aproximados por persona.
    """
    try:
        # Validar que las fechas sean futuras
        from datetime import datetime, timedelta
        try:
            fecha_ida_obj = datetime.strptime(fecha_ida, "%Y-%m-%d")
            hoy = datetime.now()
            
            if fecha_ida_obj < hoy:
                dias_diff = (hoy - fecha_ida_obj).days
                fecha_sugerida = (hoy + timedelta(days=30)).strftime("%Y-%m-%d")
                return f"❌ ERROR: La fecha {fecha_ida} ya pasó (hace {dias_diff} días).\n\n💡 Sugerencia: Usa fechas futuras, por ejemplo: {fecha_sugerida}\n\nFormato correcto: YYYY-MM-DD"
        except ValueError:
            return f"❌ ERROR: Formato de fecha incorrecto: {fecha_ida}\n\n💡 Usa formato: YYYY-MM-DD (ejemplo: 2025-12-15)"
        
        # Obtener códigos IATA
        origen_iata = obtener_codigo_iata(origen)
        destino_iata = obtener_codigo_iata(destino)
        
        if not origen_iata or not destino_iata:
            return f"❌ No se encontró código IATA para {origen if not origen_iata else destino}. Ciudades disponibles: Lima, Madrid, Barcelona, París, Londres, New York, Miami, Cancún, etc."
        
        # Obtener información de viajeros
        conteo = viajeros_db.contar_por_tipo()
        num_adultos = max(conteo.get("adulto", 0), 1)
        num_ninos = conteo.get("niño", 0)
        num_bebes = conteo.get("bebé", 0)
        num_viajeros = len(viajeros_db.viajeros) or 1
        
        # Intentar usar Amadeus API
        datos_amadeus = buscar_vuelos_amadeus(origen_iata, destino_iata, fecha_ida, 
                                               fecha_vuelta, num_adultos)
        
        tipo_viaje = "ida y vuelta" if fecha_vuelta else "solo ida"
        
        if datos_amadeus and "data" in datos_amadeus and len(datos_amadeus["data"]) > 0:
            # USAR DATOS REALES DE AMADEUS
            resultado = f"✈️ VUELOS REALES - {tipo_viaje.upper()}\n"
            resultado += f"📍 {origen} ({origen_iata}) → {destino} ({destino_iata})\n"
            resultado += f"📅 Ida: {fecha_ida}"
            if fecha_vuelta:
                resultado += f" | Vuelta: {fecha_vuelta}"
            resultado += f"\n👥 Viajeros: {num_viajeros} persona(s)\n"
            resultado += f"   ({num_adultos} adulto(s), {num_ninos} niño(s), {num_bebes} bebé(s))\n\n"
            
            vuelos = datos_amadeus["data"][:3]  # Top 3 opciones
            
            for i, vuelo in enumerate(vuelos):
                precio_base = float(vuelo["price"]["total"])
                moneda = vuelo["price"]["currency"]
                
                # Calcular para todo el grupo
                precio_ninos = precio_base * 0.75 * num_ninos
                precio_bebes = precio_base * 0.15 * num_bebes
                total_grupo = (precio_base * num_adultos) + precio_ninos + precio_bebes
                
                # Información del vuelo
                segmentos = vuelo["itineraries"][0]["segments"]
                primer_segmento = segmentos[0]
                ultimo_segmento = segmentos[-1]
                
                aerolinea_code = primer_segmento["carrierCode"]
                duracion = vuelo["itineraries"][0]["duration"]
                escalas = len(segmentos) - 1
                
                hora_salida = primer_segmento["departure"]["at"].split("T")[1][:5]
                hora_llegada = ultimo_segmento["arrival"]["at"].split("T")[1][:5]
                
                resultado += f"🛫 Opción {i+1}: {aerolinea_code}\n"
                resultado += f"   ⏰ Salida: {hora_salida} | Llegada: {hora_llegada}\n"
                resultado += f"   🔄 Escalas: {escalas} | Duración: {duracion[2:]}\n"
                resultado += f"   💰 Precio por adulto: {precio_base:.2f} {moneda}\n"
                if num_ninos > 0:
                    resultado += f"   👶 Niños ({num_ninos}): {precio_ninos:.2f} {moneda}\n"
                if num_bebes > 0:
                    resultado += f"   🍼 Bebés ({num_bebes}): {precio_bebes:.2f} {moneda}\n"
                resultado += f"   💵 TOTAL GRUPO: {total_grupo:.2f} {moneda}\n\n"
            
            resultado += "✅ Precios reales obtenidos de Amadeus API\n\n"
            
            # Agregar links de compra
            resultado += "🔗 ENLACES PARA COMPRAR:\n"
            resultado += f"🌐 Google Flights: https://www.google.com/flights?hl=es#flt={origen_iata}.{destino_iata}.{fecha_ida}"
            if fecha_vuelta:
                resultado += f"*{destino_iata}.{origen_iata}.{fecha_vuelta}"
            resultado += f";c:EUR;e:1;sd:1;t:f\n"
            
            resultado += f"🌐 Skyscanner: https://www.skyscanner.com/transport/flights/{origen_iata}/{destino_iata}/{fecha_ida.replace('-', '')}"
            if fecha_vuelta:
                resultado += f"/{fecha_vuelta.replace('-', '')}"
            resultado += f"/?adultsv1={num_adultos}"
            if num_ninos > 0:
                resultado += f"&childrenv1={num_ninos}"
            resultado += "\n"
            
            resultado += f"🌐 Kayak: https://www.kayak.com/flights/{origen_iata}-{destino_iata}/{fecha_ida}"
            if fecha_vuelta:
                resultado += f"/{fecha_vuelta}"
            resultado += f"/{num_adultos}adults"
            if num_ninos > 0:
                resultado += f"/{num_ninos}children"
            resultado += "\n"
            
            return resultado
        
        else:
            # FALLBACK: DATOS SIMULADOS
            resultado = f"✈️ VUELOS SIMULADOS - {tipo_viaje.upper()}\n"
            resultado += f"📍 {origen} ({origen_iata}) → {destino} ({destino_iata})\n"
            resultado += f"📅 Ida: {fecha_ida}"
            if fecha_vuelta:
                resultado += f" | Vuelta: {fecha_vuelta}"
            resultado += f"\n👥 Viajeros: {num_viajeros} persona(s)\n\n"
            resultado += "⚠️ Usando datos simulados (configura AMADEUS_API_KEY para precios reales)\n\n"
            
            # Aerolíneas simuladas
            aerolineas = [
                {"nombre": "LATAM Airlines", "codigo": "LA"},
                {"nombre": "Avianca", "codigo": "AV"},
                {"nombre": "Copa Airlines", "codigo": "CM"},
                {"nombre": "Iberia", "codigo": "IB"},
                {"nombre": "American Airlines", "codigo": "AA"},
                {"nombre": "Air Europa", "codigo": "UX"}
            ]
            
            # Calcular precio base según distancia estimada (simulado)
            rutas_populares = {
                ("LIM", "CUZ"): 150, ("LIM", "MAD"): 800,
                ("MAD", "BCN"): 120, ("BUE", "GIG"): 350,
                ("MIA", "LIM"): 600, ("BOG", "CTG"): 180,
            }
            
            # Buscar precio base
            ruta = (origen_iata, destino_iata)
            ruta_inversa = (destino_iata, origen_iata)
            precio_base = rutas_populares.get(ruta) or rutas_populares.get(ruta_inversa) or 500
            
            # Generar opciones de vuelos
            multiplicador = 2 if fecha_vuelta else 1
            
            # Generar 3 opciones
            for i, aerolinea in enumerate(random.sample(aerolineas, min(3, len(aerolineas)))):
                variacion = random.uniform(0.85, 1.25)
                precio_adulto = int(precio_base * variacion * multiplicador)
                precio_nino = int(precio_adulto * 0.75)
                precio_bebe = int(precio_adulto * 0.15)
                
                # Calcular total
                total = (precio_adulto * num_adultos +
                        precio_nino * num_ninos +
                        precio_bebe * num_bebes)
                
                if total == 0:  # Si no hay viajeros registrados
                    total = precio_adulto
                
                hora_salida = random.choice(["06:30", "10:15", "14:45", "18:30", "22:00"])
                duracion = random.choice(["2h 30m", "3h 15m", "5h 45m", "8h 20m"])
                
                resultado += f"🛫 Opción {i+1}: {aerolinea['nombre']} ({aerolinea['codigo']})\n"
                resultado += f"   ⏰ Salida: {hora_salida} | Duración: {duracion}\n"
                resultado += f"   💰 Precio por adulto: ${precio_adulto} USD\n"
                if num_ninos > 0:
                    resultado += f"   👶 Niños: ${precio_nino} USD/niño\n"
                if num_bebes > 0:
                    resultado += f"   🍼 Bebés: ${precio_bebe} USD/bebé\n"
                resultado += f"   💵 TOTAL: ${total} USD\n\n"
            
            # Agregar links de compra
            resultado += "🔗 ENLACES PARA COMPRAR:\n"
            resultado += f"🌐 Google Flights: https://www.google.com/flights?hl=es#flt={origen_iata}.{destino_iata}.{fecha_ida}"
            if fecha_vuelta:
                resultado += f"*{destino_iata}.{origen_iata}.{fecha_vuelta}"
            resultado += f";c:EUR;e:1;sd:1;t:f\n"
            
            resultado += f"🌐 Skyscanner: https://www.skyscanner.com/transport/flights/{origen_iata}/{destino_iata}/{fecha_ida.replace('-', '')}"
            if fecha_vuelta:
                resultado += f"/{fecha_vuelta.replace('-', '')}"
            resultado += f"/?adultsv1={num_adultos}"
            if num_ninos > 0:
                resultado += f"&childrenv1={num_ninos}"
            resultado += "\n"
            
            resultado += f"🌐 Kayak: https://www.kayak.com/flights/{origen_iata}-{destino_iata}/{fecha_ida}"
            if fecha_vuelta:
                resultado += f"/{fecha_vuelta}"
            resultado += f"/{num_adultos}adults"
            if num_ninos > 0:
                resultado += f"/{num_ninos}children"
            resultado += "\n"
            
            return resultado
    
    except Exception as e:
        return f"❌ Error al buscar vuelos: {str(e)}"

# ============================================================================
# HERRAMIENTA 3: INFORMACIÓN DEL DESTINO
# ============================================================================

class DestinoInput(BaseModel):
    """Input para información del destino"""
    ciudad: str = Field(description="Ciudad o lugar turístico")
    idioma: str = Field(default="es", description="Idioma del resumen (es, en)")

@tool("info_destino", args_schema=DestinoInput)
def info_destino(ciudad: str, idioma: str = "es") -> str:
    """
    Obtiene información completa de un destino usando Wikipedia y datos geográficos.
    Incluye descripción, atracciones principales y datos relevantes.
    """
    try:
        from urllib.parse import quote
        resultado = ""
        
        # 1. Obtener descripción de Wikipedia (PRIORITARIO)
        # Codificar la ciudad para URL (maneja acentos y espacios)
        ciudad_encoded = quote(ciudad)
        wiki_url = f"https://{idioma}.wikipedia.org/api/rest_v1/page/summary/{ciudad_encoded}"
        
        headers = {
            "User-Agent": "TravelProAI/3.0 (Educational project)",
            "Accept": "application/json"
        }
        
        wiki_response = requests.get(wiki_url, headers=headers, timeout=10)
        
        if wiki_response.status_code == 200:
            wiki_data = wiki_response.json()
            titulo = wiki_data.get('title', ciudad)
            descripcion = wiki_data.get('extract', '')
            
            # Verificar que sea un destino turístico (no un personaje o concepto)
            # Si la descripción es muy corta o menciona mitología, buscar con "ciudad de X"
            if len(descripcion) < 100 or 'mitolog' in descripcion.lower():
                # Intentar con "ciudad de X" o usando búsqueda
                search_url = f"https://{idioma}.wikipedia.org/w/api.php"
                search_params = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": f"{ciudad} ciudad",
                    "srlimit": 1
                }
                search_resp = requests.get(search_url, headers=headers, params=search_params, timeout=10)
                if search_resp.status_code == 200:
                    search_data = search_resp.json()
                    if search_data.get('query', {}).get('search'):
                        titulo_real = search_data['query']['search'][0]['title']
                        # Volver a buscar con el título correcto
                        wiki_url_real = f"https://{idioma}.wikipedia.org/api/rest_v1/page/summary/{quote(titulo_real)}"
                        wiki_resp_real = requests.get(wiki_url_real, headers=headers, timeout=10)
                        if wiki_resp_real.status_code == 200:
                            wiki_data = wiki_resp_real.json()
                            titulo = wiki_data.get('title', ciudad)
                            descripcion = wiki_data.get('extract', '')
            
            # Limitar descripción para ahorrar tokens pero mantener info útil (500 caracteres)
            if len(descripcion) > 500:
                descripcion = descripcion[:500] + "..."
            
            if descripcion:
                resultado += f"📍 {titulo}\n\n"
                resultado += f"ℹ️ {descripcion}\n\n"
        
        # 2. Obtener datos geográficos adicionales
        clima_url = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad}&count=1&language=es"
        geo_response = requests.get(clima_url, timeout=10)
        
        if geo_response.status_code == 200:
            geo_data = geo_response.json()
            if geo_data.get('results'):
                resultado_geo = geo_data['results'][0]
                pais = resultado_geo.get('country', '')
                poblacion = resultado_geo.get('population', 0)
                lat = resultado_geo.get('latitude', 0)
                
                # Determinar clima general por latitud
                clima = "tropical" if abs(lat) < 23.5 else "templado" if abs(lat) < 66.5 else "frío"
                
                resultado += f"📊 DATOS CLAVE:\n"
                resultado += f"🌍 País: {pais}\n"
                if poblacion > 0:
                    resultado += f"👥 Población: {poblacion:,}\n"
                resultado += f"🌡️ Clima general: {clima}\n"
        
        if not resultado:
            return f"❌ No se encontró información de {ciudad}. Intenta con el nombre en español o inglés."
        
        return resultado
    
    except Exception as e:
        return f"❌ Error al consultar {ciudad}: {str(e)}"

# ============================================================================
# HERRAMIENTA 4: RECOMENDACIONES POR TEMPORADA
# ============================================================================

class TemporadaInput(BaseModel):
    """Input para recomendaciones de temporada"""
    destino: str = Field(description="Destino turístico")
    mes: str = Field(description="Mes del viaje (ej: 'Enero', 'Julio')")

@tool("recomendaciones_temporada", args_schema=TemporadaInput)
def recomendaciones_temporada(destino: str, mes: str) -> str:
    """
    Genera recomendaciones de actividades según la temporada del año.
    Considera el clima y eventos típicos del destino.
    """
    try:
        meses_verano_norte = ["junio", "julio", "agosto"]
        meses_invierno_norte = ["diciembre", "enero", "febrero"]
        
        mes_lower = mes.lower()
        
        # Consultar clima actual
        clima_url = f"https://geocoding-api.open-meteo.com/v1/search?name={destino}&count=1&language=es"
        geo_response = requests.get(clima_url, timeout=10)
        
        hemisferio = "norte"  # Por defecto
        if geo_response.status_code == 200:
            geo_data = geo_response.json()
            if geo_data.get('results'):
                lat = geo_data['results'][0].get('latitude', 0)
                hemisferio = "sur" if lat < 0 else "norte"
        
        # Determinar temporada
        if hemisferio == "norte":
            es_verano = mes_lower in meses_verano_norte
            es_invierno = mes_lower in meses_invierno_norte
        else:
            es_verano = mes_lower in meses_invierno_norte
            es_invierno = mes_lower in meses_verano_norte
        
        resultado = f"🗓️ Recomendaciones para {destino} en {mes.capitalize()}\n"
        resultado += f"🌐 Hemisferio: {hemisferio.capitalize()}\n\n"
        
        if es_verano:
            resultado += "☀️ TEMPORADA: VERANO\n"
            resultado += "Actividades recomendadas:\n"
            resultado += "🏖️ Playas y deportes acuáticos\n"
            resultado += "🚶 Tours a pie y senderismo\n"
            resultado += "🍹 Terrazas y actividades al aire libre\n"
            resultado += "📸 Fotografía paisajística\n"
            resultado += "🎪 Festivales y eventos culturales\n"
            resultado += "\n💡 Consejos: Protector solar, ropa ligera, hidratación"
        
        elif es_invierno:
            resultado += "❄️ TEMPORADA: INVIERNO\n"
            resultado += "Actividades recomendadas:\n"
            resultado += "🏛️ Museos y sitios históricos\n"
            resultado += "🍽️ Gastronomía local\n"
            resultado += "🎭 Teatro y eventos culturales\n"
            resultado += "🛍️ Compras y mercados locales\n"
            resultado += "☕ Cafés y experiencias gastronómicas\n"
            resultado += "\n💡 Consejos: Ropa abrigada, planificar horarios, reservas previas"
        
        else:
            resultado += "🌸 TEMPORADA: PRIMAVERA/OTOÑO\n"
            resultado += "Actividades recomendadas:\n"
            resultado += "🌳 Parques y jardines\n"
            resultado += "🚴 Ciclismo y actividades moderadas\n"
            resultado += "🎨 Eventos culturales\n"
            resultado += "📚 Tours históricos y culturales\n"
            resultado += "🍷 Experiencias gastronómicas\n"
            resultado += "\n💡 Consejos: Ropa en capas, clima variable"
        
        return resultado
    
    except Exception as e:
        return f"❌ Error al generar recomendaciones: {str(e)}"

# ============================================================================
# HERRAMIENTA 5: GENERADOR DE ITINERARIO
# ============================================================================

class ItinerarioInput(BaseModel):
    """Input para generar itinerario"""
    destino: str = Field(description="Destino del viaje")
    dias: int = Field(description="Número de días del viaje")
    presupuesto: str = Field(description="Nivel de presupuesto: 'bajo', 'medio', 'alto'")

@tool("generar_itinerario", args_schema=ItinerarioInput)
def generar_itinerario(destino: str, dias: int, presupuesto: str = "medio") -> str:
    """
    Genera un itinerario día a día con actividades y estimación de gastos.
    Adaptado al presupuesto especificado.
    """
    try:
        actividades_por_presupuesto = {
            "bajo": {
                "actividades": ["Tours gratuitos", "Mercados locales", "Parques públicos", "Museos gratis", "Caminatas"],
                "comida_dia": 25,
                "actividad_dia": 15,
                "transporte_dia": 10
            },
            "medio": {
                "actividades": ["Tours guiados", "Museos", "Restaurantes locales", "Actividades culturales", "Compras"],
                "comida_dia": 50,
                "actividad_dia": 40,
                "transporte_dia": 20
            },
            "alto": {
                "actividades": ["Tours premium", "Experiencias exclusivas", "Fine dining", "Spa", "Tours privados"],
                "comida_dia": 120,
                "actividad_dia": 100,
                "transporte_dia": 40
            }
        }
        
        config = actividades_por_presupuesto.get(presupuesto.lower(), actividades_por_presupuesto["medio"])
        
        resultado = f"📅 ITINERARIO DE {dias} DÍAS EN {destino.upper()}\n"
        resultado += f"💰 Presupuesto: {presupuesto.capitalize()}\n"
        resultado += f"👥 Viajeros: {len(viajeros_db.viajeros) or 1}\n\n"
        
        total_gasto = 0
        
        for dia in range(1, dias + 1):
            resultado += f"📆 DÍA {dia}:\n"
            
            if dia == 1:
                resultado += "   🛬 Llegada y check-in\n"
                actividad1 = random.choice(["Paseo por el centro histórico", "Tour de orientación", "Cena de bienvenida"])
                resultado += f"   🏃 {actividad1}\n"
            elif dia == dias:
                resultado += "   🧳 Check-out\n"
                actividad1 = random.choice(["Últimas compras", "Paseo de despedida", "Visita rápida"])
                resultado += f"   🏃 {actividad1}\n"
                resultado += "   🛫 Regreso\n"
            else:
                actividad1 = random.choice(config["actividades"])
                actividad2 = random.choice(config["actividades"])
                resultado += f"   ☀️ Mañana: {actividad1}\n"
                resultado += f"   🌆 Tarde: {actividad2}\n"
            
            gasto_dia = config["comida_dia"] + config["actividad_dia"] + config["transporte_dia"]
            total_gasto += gasto_dia
            resultado += f"   💵 Gasto estimado: ${gasto_dia} USD/persona\n\n"
        
        num_personas = len(viajeros_db.viajeros) or 1
        total_viaje = total_gasto * num_personas
        
        resultado += f"💰 RESUMEN FINANCIERO:\n"
        resultado += f"   Por persona: ${total_gasto} USD\n"
        resultado += f"   Total grupo ({num_personas} persona(s)): ${total_viaje} USD\n"
        resultado += f"\n📝 Nota: Precios aproximados, no incluyen vuelos ni alojamiento\n"
        
        return resultado
    
    except Exception as e:
        return f"❌ Error al generar itinerario: {str(e)}"

# ============================================================================
# HERRAMIENTA 6: CALCULADORA DE PRESUPUESTO
# ============================================================================

class PresupuestoInput(BaseModel):
    """Input para calcular presupuesto"""
    dias: int = Field(description="Número de días")
    destino: str = Field(description="Destino del viaje")
    nivel: str = Field(default="medio", description="Nivel: 'economico', 'medio', 'lujo'")

@tool("calcular_presupuesto", args_schema=PresupuestoInput)
def calcular_presupuesto(dias: int, destino: str, nivel: str = "medio") -> str:
    """
    Calcula el presupuesto total estimado para el viaje.
    Incluye: vuelos, alojamiento, comida, actividades, transporte.
    """
    try:
        # Costos por nivel y por día
        costos = {
            "economico": {
                "vuelo": 400,
                "hotel_noche": 40,
                "comida_dia": 25,
                "actividades_dia": 15,
                "transporte_dia": 10,
                "otros_dia": 10
            },
            "medio": {
                "vuelo": 700,
                "hotel_noche": 80,
                "comida_dia": 50,
                "actividades_dia": 40,
                "transporte_dia": 20,
                "otros_dia": 20
            },
            "lujo": {
                "vuelo": 1500,
                "hotel_noche": 200,
                "comida_dia": 120,
                "actividades_dia": 100,
                "transporte_dia": 40,
                "otros_dia": 50
            }
        }
        
        config = costos.get(nivel.lower(), costos["medio"])
        num_personas = len(viajeros_db.viajeros) or 1
        conteo = viajeros_db.contar_por_tipo()
        
        # Calcular costos
        vuelos = config["vuelo"] * num_personas
        # Descuentos para niños
        if conteo.get("niño", 0) > 0:
            vuelos -= config["vuelo"] * 0.25 * conteo["niño"]
        if conteo.get("bebé", 0) > 0:
            vuelos -= config["vuelo"] * 0.85 * conteo["bebé"]
        
        alojamiento = config["hotel_noche"] * dias
        comida = config["comida_dia"] * dias * num_personas
        actividades = config["actividades_dia"] * dias * num_personas
        transporte = config["transporte_dia"] * dias * num_personas
        otros = config["otros_dia"] * dias * num_personas
        
        total = vuelos + alojamiento + comida + actividades + transporte + otros
        
        resultado = f"💰 PRESUPUESTO ESTIMADO - {destino.upper()}\n"
        resultado += f"📊 Nivel: {nivel.capitalize()}\n"
        resultado += f"📅 Duración: {dias} días\n"
        resultado += f"👥 Viajeros: {num_personas} persona(s)\n\n"
        
        resultado += "📋 DESGLOSE:\n"
        resultado += f"✈️  Vuelos (ida y vuelta): ${int(vuelos)} USD\n"
        resultado += f"🏨 Alojamiento ({dias} noches): ${int(alojamiento)} USD\n"
        resultado += f"🍽️  Comidas: ${int(comida)} USD\n"
        resultado += f"🎭 Actividades: ${int(actividades)} USD\n"
        resultado += f"🚕 Transporte local: ${int(transporte)} USD\n"
        resultado += f"🛍️  Otros gastos: ${int(otros)} USD\n"
        resultado += f"\n{'='*40}\n"
        resultado += f"💵 TOTAL: ${int(total)} USD\n"
        resultado += f"💳 Por persona: ${int(total/num_personas)} USD\n"
        
        return resultado
    
    except Exception as e:
        return f"❌ Error al calcular presupuesto: {str(e)}"

# ============================================================================
# CONFIGURACIÓN DEL AGENTE
# ============================================================================

def crear_agente_vacaciones():
    """Crea y configura el agente de planificación de vacaciones"""
    
    # Configuración de API
    openai_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    if not openai_key:
        raise ValueError("❌ No se encontró OPENAI_API_KEY. Verifica tu archivo .env")
    
    llm = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=openai_key
    )
    
    # Sistema de memoria
    memory = MemorySaver()
    
    # Prompt del sistema
    system_prompt = """Eres Travel Pro AI, un agente experto en planificación de vacaciones con un proceso conversacional estructurado.

🎯 FLUJO DE CONVERSACIÓN (SIGUE ESTE ORDEN):

PASO 1: CONOCER A LOS VIAJEROS
- Pregunta por nombres y edades de TODOS los viajeros
- Usa gestionar_viajeros para registrarlos
- Confirma el registro

PASO 2: DESTINO Y DURACIÓN
- Pregunta: ¿A dónde quieren ir?
- Pregunta: ¿Por cuántos días?
- Pregunta: ¿Desde qué ciudad viajan?
- Usa info_destino para dar información breve del destino

PASO 3: OCASIÓN ESPECIAL
- Pregunta si el viaje es para algo especial (luna de miel, aniversario, vacaciones familiares, etc.)
- Esto ayuda a personalizar las recomendaciones

PASO 4: ITINERARIO PERSONALIZADO
- Pregunta el nivel de presupuesto (económico, medio, lujo)
- Usa recomendaciones_temporada para actividades según época
- Usa generar_itinerario con la info recopilada
- Muestra el itinerario día a día

PASO 5: FECHAS DE VIAJE
- AHORA pregunta las fechas específicas (formato: YYYY-MM-DD)
- Explica que necesitas fechas concretas para buscar vuelos

PASO 6: BÚSQUEDA DE VUELOS
- Usa buscar_vuelos con toda la información
- Los links se generan automáticamente
- Muestra opciones y presupuesto total

📋 REGLAS IMPORTANTES:
1. NO SALTES PASOS - Sigue el orden
2. UNA PREGUNTA A LA VEZ - No abrumes al usuario
3. SÉ CONVERSACIONAL - Amigable pero conciso
4. USA LAS HERRAMIENTAS - No inventes información
5. CONFIRMA ANTES DE CONTINUAR - Asegúrate de tener la info correcta

💬 ESTILO DE COMUNICACIÓN:
- Respuestas cortas (3-5 líneas máximo antes de usar herramientas)
- Emojis para hacer más amigable
- Preguntas claras y directas
- Si falta información, pídela específicamente

⚠️ IMPORTANTE:
- Si el usuario da toda la info de una vez, sigue igual el flujo pero más rápido
- Siempre usa info_destino ANTES de generar itinerario
- Busca vuelos AL FINAL, después del itinerario
- Los links de vuelos se generan AUTOMÁTICAMENTE

Ejemplo de inicio ideal:
Usuario: "Quiero planear vacaciones"
Tú: "¡Genial! 🌴 Primero, cuéntame: ¿Quiénes viajan? Dame nombres y edades de cada persona."

¡Crea experiencias de viaje inolvidables! ✈️"""

    # Herramientas disponibles
    tools = [
        gestionar_viajeros,
        buscar_vuelos,
        info_destino,
        recomendaciones_temporada,
        generar_itinerario,
        calcular_presupuesto
    ]
    
    # Crear agente
    agente = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=SystemMessage(content=system_prompt)
    )
    
    return agente


