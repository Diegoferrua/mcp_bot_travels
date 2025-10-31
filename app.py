"""
🌴 TRAVEL PRO AI - Agente de Planificación de Vacaciones
Interfaz web con Streamlit
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from asistente import crear_agente_vacaciones, viajeros_db
from langchain_core.messages import HumanMessage, AIMessage

# Cargar variables de entorno
load_dotenv()

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Travel Pro AI",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================================

st.markdown("""
<style>
    /* Header principal */
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        animation: gradient 3s ease infinite;
    }
    
    .sub-header {
        font-size: 1.3rem;
        text-align: center;
        color: #95a5a6;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    /* Mensajes de chat mejorados */
    .chat-message {
        padding: 1.3rem;
        border-radius: 1rem;
        margin-bottom: 1.2rem;
        line-height: 1.7;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: 5px solid #4A5FD9;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-left: 5px solid #e14852;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
    }
    
    /* Cards de características */
    .feature-card {
        padding: 1.8rem;
        border-radius: 1rem;
        background: linear-gradient(135deg, rgba(78, 205, 196, 0.1) 0%, rgba(69, 183, 209, 0.1) 100%);
        border: 2px solid rgba(78, 205, 196, 0.3);
        margin-bottom: 1.2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(78, 205, 196, 0.3);
    }
    
    .feature-card h4 {
        color: #4ECDC4;
        margin-bottom: 0.8rem;
        font-size: 1.2rem;
    }
    
    .feature-card p {
        color: #bdc3c7;
        margin: 0;
        line-height: 1.6;
    }
    
    /* Inputs mejorados */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.08);
        border: 2px solid rgba(78, 205, 196, 0.4);
        border-radius: 0.8rem;
        padding: 1rem;
        color: white;
        font-size: 1.05rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4ECDC4;
        box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.2);
        background-color: rgba(255, 255, 255, 0.12);
    }
    
    /* Botones mejorados */
    .stButton > button {
        background: linear-gradient(135deg, #4ECDC4 0%, #45B7D1 100%);
        color: white;
        border: none;
        border-radius: 0.8rem;
        padding: 0.8rem 1.5rem;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(78, 205, 196, 0.5);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Métricas */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(78, 205, 196, 0.2));
        padding: 1rem;
        border-radius: 0.8rem;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INICIALIZACIÓN DE ESTADO
# ============================================================================

def inicializar_estado():
    """Inicializa el estado de la sesión"""
    if 'agente' not in st.session_state:
        st.session_state.agente = crear_agente_vacaciones()
    
    if 'config' not in st.session_state:
        st.session_state.config = {
            "configurable": {"thread_id": f"travel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}
        }
    
    if 'historial' not in st.session_state:
        st.session_state.historial = []
    
    if 'contador_mensajes' not in st.session_state:
        st.session_state.contador_mensajes = 0

# ============================================================================
# FUNCIONES DE INTERFAZ
# ============================================================================

def mostrar_header():
    """Muestra el encabezado de la aplicación"""
    st.markdown('<div class="main-header">✈️ Travel Pro AI 🌴</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tu Agente Personal de Planificación de Vacaciones</div>', unsafe_allow_html=True)

def mostrar_sidebar():
    """Muestra la barra lateral con información y controles"""
    with st.sidebar:
        # Logo/Imagen
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 5rem;'>🏝️</div>
            <h2 style='color: #4ECDC4; margin: 0;'>Travel Pro AI</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Capacidades
        st.markdown("### 🎯 Mis Capacidades")
        st.markdown("""
        <div style='background: rgba(78, 205, 196, 0.1); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            👥 <b>Gestión de Viajeros</b><br>
            <small>Administra tu grupo de viaje</small>
        </div>
        <div style='background: rgba(69, 183, 209, 0.1); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            ✈️ <b>Búsqueda de Vuelos</b><br>
            <small>Encuentra las mejores opciones</small>
        </div>
        <div style='background: rgba(255, 107, 107, 0.1); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            🌍 <b>Info de Destinos</b><br>
            <small>Conoce tu próximo destino</small>
        </div>
        <div style='background: rgba(245, 87, 108, 0.1); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            📅 <b>Itinerarios Personalizados</b><br>
            <small>Planificación día a día</small>
        </div>
        <div style='background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            💰 <b>Cálculo de Presupuesto</b><br>
            <small>Control total de gastos</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Ejemplos de uso
        st.markdown("### 💡 Ejemplos Rápidos")
        ejemplos = [
            "Quiero planear un viaje",
            "Somos 2 personas: Juan (30) y María (28)",
            "Queremos ir a París por 5 días",
            "Es para nuestra luna de miel",
            "Del 15 al 20 de marzo 2026",
            "Presupuesto medio"
        ]
        
        for i, ejemplo in enumerate(ejemplos):
            if st.button(f"📝 {ejemplo}", key=f"ejemplo_{i}", use_container_width=True):
                st.session_state.ejemplo_seleccionado = ejemplo
        
        st.markdown("---")
        
        # Estadísticas
        st.markdown("### 📊 Estadísticas del Viaje")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style='font-size: 2rem; font-weight: bold; color: #4ECDC4;'>{st.session_state.contador_mensajes}</div>
                <div style='font-size: 0.9rem; color: #95a5a6;'>Mensajes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            num_viajeros = len(viajeros_db.viajeros)
            st.markdown(f"""
            <div class="metric-card">
                <div style='font-size: 2rem; font-weight: bold; color: #FF6B6B;'>{num_viajeros}</div>
                <div style='font-size: 0.9rem; color: #95a5a6;'>Viajeros</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Desglose de viajeros
        if num_viajeros > 0:
            conteo = viajeros_db.contar_por_tipo()
            st.markdown(f"""
            <div style='background: rgba(78, 205, 196, 0.1); padding: 0.8rem; border-radius: 0.5rem; margin-top: 0.5rem;'>
                <small>
                👨 Adultos: {conteo.get('adulto', 0)} |
                🧒 Niños: {conteo.get('niño', 0)} |
                👶 Bebés: {conteo.get('bebé', 0)}
                </small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Botones de acción
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpiar Chat", use_container_width=True):
                st.session_state.historial = []
                st.session_state.contador_mensajes = 0
                st.rerun()
            
        with col2:
            if st.button("👥 Limpiar Viajeros", use_container_width=True):
                viajeros_db.limpiar()
                st.rerun()
        
        st.markdown("---")
        
        # Footer
        st.markdown("""
        <div style='text-align: center; color: #7f8c8d; font-size: 0.85rem; padding: 1rem;'>
            <div style='margin-bottom: 0.5rem;'>✨ Powered by</div>
            <div><b>LangChain • OpenAI • LangGraph</b></div>
            <div style='margin-top: 0.5rem; color: #95a5a6;'>Versión 3.0 Travel Edition</div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_historial():
    """Muestra el historial de conversación"""
    for mensaje in st.session_state.historial:
        if mensaje['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 Tú:</strong><br>
                {mensaje['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Convertir saltos de línea a <br> para mejor visualización
            contenido = mensaje['content'].replace('\n', '<br>')
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Travel Pro:</strong><br>
                {contenido}
            </div>
            """, unsafe_allow_html=True)

def procesar_mensaje(user_input: str):
    """Procesa el mensaje del usuario con el agente"""
    # Agregar mensaje del usuario al historial
    st.session_state.historial.append({
        'role': 'user',
        'content': user_input
    })
    st.session_state.contador_mensajes += 1
    
    # Procesar con el agente
    with st.spinner('🤔 Planificando tu viaje perfecto...'):
        try:
            response_content = ""
            
            # Obtener el estado completo del grafo
            result = st.session_state.agente.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                st.session_state.config
            )
            
            # Obtener la última respuesta del asistente
            if result and "messages" in result:
                for message in reversed(result["messages"]):
                    if isinstance(message, AIMessage) and message.content:
                        response_content = message.content
                        break
            
            # Agregar respuesta del asistente al historial
            if response_content:
                st.session_state.historial.append({
                    'role': 'assistant',
                    'content': response_content
                })
            else:
                st.session_state.historial.append({
                    'role': 'assistant',
                    'content': "❌ No pude generar una respuesta. Por favor, intenta de nuevo."
                })
        
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            st.session_state.historial.append({
                'role': 'assistant',
                'content': f"❌ Error: {str(e)}\n\nSi el problema persiste, intenta limpiar el chat."
            })

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

def main():
    """Función principal de la aplicación web"""
    
    # Inicializar estado
    inicializar_estado()
    
    # Mostrar componentes
    mostrar_header()
    mostrar_sidebar()
    
    # Área de chat
    st.markdown("### 💬 Conversación")
    
    # Contenedor para el historial
    chat_container = st.container()
    with chat_container:
        mostrar_historial()
    
    # Input del usuario con formulario para mejor UX
    st.markdown("---")
    with st.form(key="mensaje_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
    
    with col1:
        # Verificar si hay ejemplo seleccionado
        default_value = st.session_state.get('ejemplo_seleccionado', '')
        user_input = st.text_input(
                "💬 Escribe tu mensaje:",
            value=default_value,
                placeholder="Ej: Quiero planear vacaciones a París para 2 personas...",
            key="user_input_field"
        )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Alineación vertical
            enviar = st.form_submit_button("📤 Enviar", use_container_width=True)
    
    # Limpiar ejemplo seleccionado después de usarlo
        if 'ejemplo_seleccionado' in st.session_state:
            del st.session_state.ejemplo_seleccionado
    
    # Procesar mensaje
    if enviar and user_input:
        procesar_mensaje(user_input)
        st.rerun()
    
    # Mensaje de bienvenida si no hay historial
    if not st.session_state.historial:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(78, 205, 196, 0.1), rgba(69, 183, 209, 0.1)); 
                    padding: 2rem; border-radius: 1rem; margin: 2rem 0; border: 2px solid rgba(78, 205, 196, 0.3);'>
            <h3 style='color: #4ECDC4; text-align: center; margin-bottom: 1rem;'>
                👋 ¡Bienvenido a Travel Pro AI!
            </h3>
            <p style='text-align: center; color: #bdc3c7; font-size: 1.1rem; line-height: 1.8;'>
                Soy tu asistente personal de viajes. Te guiaré paso a paso para planificar el viaje perfecto:
            </p>
            <div style='text-align: left; color: #bdc3c7; max-width: 600px; margin: 1.5rem auto; line-height: 2;'>
                <div style='padding: 0.5rem; border-left: 3px solid #4ECDC4; margin: 0.5rem 0; padding-left: 1rem;'>
                    <b>1️⃣ Viajeros:</b> Nombres y edades
                </div>
                <div style='padding: 0.5rem; border-left: 3px solid #45B7D1; margin: 0.5rem 0; padding-left: 1rem;'>
                    <b>2️⃣ Destino:</b> A dónde, por cuántos días, desde dónde
                </div>
                <div style='padding: 0.5rem; border-left: 3px solid #FF6B6B; margin: 0.5rem 0; padding-left: 1rem;'>
                    <b>3️⃣ Ocasión:</b> ¿Es un viaje especial?
                </div>
                <div style='padding: 0.5rem; border-left: 3px solid #F5576C; margin: 0.5rem 0; padding-left: 1rem;'>
                    <b>4️⃣ Itinerario:</b> Plan día a día personalizado
                </div>
                <div style='padding: 0.5rem; border-left: 3px solid #667eea; margin: 0.5rem 0; padding-left: 1rem;'>
                    <b>5️⃣ Fechas:</b> Cuándo quieres viajar
                </div>
                <div style='padding: 0.5rem; border-left: 3px solid #764ba2; margin: 0.5rem 0; padding-left: 1rem;'>
                    <b>6️⃣ Vuelos:</b> Opciones reales con links de compra
                </div>
            </div>
            <p style='text-align: center; color: #4ECDC4; margin-top: 1.5rem; font-size: 1.1rem;'>
                <b>💬 Empieza diciendo: "Quiero planear un viaje"</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar tarjetas de características
        st.markdown("### ✨ ¿Cómo puedo ayudarte?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>👥 Gestión de Viajeros</h4>
                <p>Registra todos los participantes del viaje: adultos, niños y bebés. Esto me permite calcular precios más precisos.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <h4>✈️ Búsqueda de Vuelos</h4>
                <p>Encuentro las mejores opciones de vuelos con precios aproximados para tu grupo.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>🌍 Info de Destinos</h4>
                <p>Te proporciono información detallada de cualquier ciudad usando Wikipedia y datos de clima.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <h4>🗓️ Recomendaciones</h4>
                <p>Sugiero actividades según la temporada y el clima de tu destino.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4>📅 Itinerarios</h4>
                <p>Creo planes día a día adaptados a tu presupuesto: económico, medio o de lujo.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <h4>💰 Presupuesto Total</h4>
                <p>Calculo el costo completo incluyendo vuelos, hotel, comidas, actividades y más.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

