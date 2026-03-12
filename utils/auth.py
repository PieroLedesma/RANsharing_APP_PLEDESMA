# =============================================================================
# utils/auth.py — Autenticación y registro de sesiones
# =============================================================================
import streamlit as st
import pandas as pd
from datetime import datetime
import os

LOG_FILE = "login_logs.csv"

def init_log_file():
    """Crea el archivo CSV si no existe."""
    if not os.path.exists(LOG_FILE):
        df = pd.DataFrame(columns=["Timestamp", "Area"])
        df.to_csv(LOG_FILE, index=False)

def log_login(area: str):
    """Registra en CSV el usuario y hora de ingreso."""
    init_log_file()
    df = pd.DataFrame({"Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")], "Area": [area]})
    df.to_csv(LOG_FILE, mode='a', header=False, index=False)

def check_password() -> bool:
    """Verifica si el usuario está autenticado. Retorna True si lo está."""
    
    # Callback que se ejecuta cuando se toca el botón de Ingreso o se pulsa Enter
    def password_entered():
        user = st.session_state.get("login_username", "")
        pwd = st.session_state.get("login_password", "")
        
        try:
            # Revisa la validez contra los secretos guardados
            valid_pwd = st.secrets["passwords"][user]
            if pwd == valid_pwd:
                st.session_state["password_correct"] = True
                st.session_state["logged_user"] = user
                
                # Borrar la password desde el dict en memoria (seguridad)
                if "login_password" in st.session_state:
                    del st.session_state["login_password"]
                    
                log_login(user)
            else:
                st.session_state["password_correct"] = False
        except Exception:
            # Si el área no existe en secrets o no se configuró algo
            st.session_state["password_correct"] = False

    # Si ya ingresó previamente en esta misma sesión
    if st.session_state.get("password_correct", False):
        return True

    # Renderiza la vista del Login en caso de no estar autenticado
    st.markdown("""
        <div style='text-align: center; margin-top: 10vh;'>
            <div style="font-size:50px; font-weight:900; color:#2D0A5E; letter-spacing:-1.5px;">
                📡 <span style="color:#E91E8C;">RAN</span>Sharing
            </div>
            <h3 style='color: #7B2D8B; font-weight: 500;'>Portal de Monitoreo Seguro</h3>
        </div>
        <hr style="opacity: 0.1;">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        try:
            # Genera la lista basándose en las llaves del secrets
            areas = list(st.secrets["passwords"].keys())
        except Exception:
            areas = ["NOC", "SOPORTE"]
            st.error("⚠️ Archivo secrets.toml no configurado. Falta bloque [passwords]")
            
        st.selectbox("Área de Acceso", areas, key="login_username")
        st.text_input("Contraseña", type="password", key="login_password", on_change=password_entered)
        
        if st.button("Ingresar al Portal", on_click=password_entered, use_container_width=True):
            pass
            
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("Contraseña incorrecta o usuario no disponible.")
            
    return False

def download_logs_button():
    """Genera un botón de descarga para que algunos perfiles bajen el CSV de logins"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "rb") as file:
            st.download_button(
                label="📥 Exportar Log de Accesos (CSV)",
                data=file,
                file_name=f"log_accesos_ransharing_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Solo visible para ciertas áreas administrativas",
                key="btn_csv_export"
            )
