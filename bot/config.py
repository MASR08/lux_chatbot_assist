"""Configuración del chatbot: lee las claves secretas desde el archivo .env."""
import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "")


def claves_faltantes():
    """Devuelve la lista de claves que todavía no tienen valor."""
    claves = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_SECRET_KEY": SUPABASE_SECRET_KEY,
    }
    return [nombre for nombre, valor in claves.items() if not valor]


if __name__ == "__main__":
    faltan = claves_faltantes()
    if faltan:
        print("Faltan estas claves en el .env:", ", ".join(faltan))
    else:
        print("Todas las claves están configuradas.")
