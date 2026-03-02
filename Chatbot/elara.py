import customtkinter as ctk
import json
import os
from difflib import get_close_matches

# Configuración de la paleta de colores
COLORES = {
    "fondo_ventana": "#242424",      # Gris muy oscuro
    "fondo_panel": "#2B2B2B",        # Un poco más claro para contraste
    "burbuja_bot": "#3A3A3A",        # Gris medio para burbuja
    "burbuja_usuario": "#FF80AB",    # Rosa vibrante para el usuario
    "texto_principal": "#FFFFFF",    # Blanco
    "texto_secundario": "#FCE4EC",   # Rosa muy pálido para subtítulos
    "acento": "#8338EC",             # Morado vibrante para botones
    "borde": "#FFB3C1"               # Rosa pastel para bordes suaves
}

# Configurar el tema visual de CustomTkinter
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("dark-blue") # Base azul para los sliders/controles

class ElaraAesthetic(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración básica de la ventana principal
        self.title("✨ Elara: My Bestie ✨")
        self.geometry("450x650")
        self.configure(fg_color=COLORES["fondo_ventana"])

        # Gestión de memoria (igual que antes)
        self.archivo_db = "elara_memory.json"
        self.memoria = self.cargar_conocimiento()

        # Construcción de la interfaz gráfica 

        # 1. Panel de Encabezado
        self.header_frame = ctk.CTkFrame(self, fg_color=COLORES["fondo_panel"], corner_radius=15, border_width=2, border_color=COLORES["borde"])
        self.header_frame.pack(pady=20, padx=20, fill="x")

        # Título principal
        self.label_titulo = ctk.CTkLabel(self.header_frame, text="🌻 ChatBot Aprendiz 🌻", 
                                        font=("Coquette", 24, "bold"), text_color=COLORES["texto_principal"])
        self.label_titulo.pack(pady=(15, 5))

        # Subtítulo
        self.label_estado = ctk.CTkLabel(self.header_frame, text=f"🧠 {len(self.memoria)} respuestas en memoria • ✨ Modo chat", 
                                          font=("Roboto", 12), text_color=COLORES["texto_secundario"])
        self.label_estado.pack(pady=(0, 15))

        # 2. Área de Chat
        self.chat_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=15, border_width=1, border_color="#404040")
        self.chat_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # 3. Panel de Entrada de Texto
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=20, padx=20, fill="x")

        # Campo de entrada redondeado
        self.entry_msg = ctk.CTkEntry(self.input_frame, placeholder_text="Escribe un mensaje súper cute...", 
                                      font=("Roboto", 13), fg_color=COLORES["fondo_panel"], 
                                      border_color="#505050", corner_radius=20, height=45)
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_msg.bind("<Return>", lambda e: self.enviar_mensaje())

        # Botón de enviar con icono/emoji y esquinas redondeadas
        self.btn_enviar = ctk.CTkButton(self.input_frame, text="▶️", command=self.enviar_mensaje, 
                                        font=("Roboto", 16, "bold"), fg_color=COLORES["acento"], 
                                        hover_color="#9D4EDD", corner_radius=20, width=50, height=45)
        self.btn_enviar.pack(side="right")

        # Mensaje de bienvenida inicial
        self.agregar_burbuja("bot", "¡Hola Gabbisita! Soy Elara ✨, tu asistente con memoria. ¡Escríbeme algo y enséñame si no sé la respuesta! 🌻")

    # Lógica de memoria

    def cargar_conocimiento(self):
        if os.path.exists(self.archivo_db):
            with open(self.archivo_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"hola": "¡Hola, preciosa! ✨"} # Conocimiento base

    def agregar_burbuja(self, autor, mensaje):
        """Crea burbujas de chat con estilos diferentes."""
        es_bot = (autor == "bot")
        
        # Marco de la burbuja (para redondear esquinas)
        bubble_frame = ctk.CTkFrame(self.chat_frame, 
                                    fg_color=COLORES["burbuja_bot"] if es_bot else COLORES["burbuja_usuario"],
                                    corner_radius=15)
        
        # Configurar alineación (Bot izquierda, Usuario derecha)
        padx_value = (10, 50) if es_bot else (50, 10)
        bubble_frame.pack(pady=8, padx=padx_value, anchor="w" if es_bot else "e")

        # Texto dentro de la burbuja
        label_msg = ctk.CTkLabel(bubble_frame, text=mensaje, font=("Roboto", 13), 
                                  text_color=COLORES["texto_principal"], wraplength=300, justify="left")
        label_msg.pack(pady=10, padx=15)

    def enviar_mensaje(self):
        user_input = self.entry_msg.get().strip()
        if not user_input: return

        # Agregar burbuja del usuario
        self.agregar_burbuja("user", user_input)
        self.entry_msg.delete(0, 'end')

        # Lógica de respuesta
        matches = get_close_matches(user_input.lower(), self.memoria.keys(), n=1, cutoff=0.6)
        if matches:
            self.agregar_burbuja("bot", self.memoria[matches[0]])
        else:
            self.pedir_nuevo_conocimiento(user_input)

    def pedir_nuevo_conocimiento(self, pregunta_nueva):
        """Módulo de Adquisición usando un cuadro de diálogo."""
        # CustomTkinter tiene su propio diálogo de entrada
        dialog = ctk.CTkInputDialog(text=f"Mmm... eso no lo sé aún. ¿Qué debería responder a '{pregunta_nueva}'? ✨🌻", title="Enseñándole a Elara")
        respuesta_nueva = dialog.get_input()
        
        if respuesta_nueva:
            self.memoria[pregunta_nueva.lower()] = respuesta_nueva
            with open(self.archivo_db, 'w', encoding='utf-8') as f:
                json.dump(self.memoria, f, indent=4, ensure_ascii=False)
            self.agregar_burbuja("bot", "¡Anotado en mi corazoncito! Ya soy más inteligente. ✨")
            # Actualizar contador en el encabezado
            self.label_estado.configure(text=f"🧠 {len(self.memoria)} respuestas en memoria • 🌸 Modo chat")
        else:
            self.agregar_burbuja("bot", "No te preocupes, tal vez me lo enseñes después. 🌸")

if __name__ == "__main__":
    app = ElaraAesthetic()
    app.mainloop()