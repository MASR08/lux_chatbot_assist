# Guía de configuración: Chatbot Lux

Resumen de lo que se ha configurado en el proyecto y de las buenas prácticas aplicadas en cada paso.
Se irá completando hasta terminar toda la configuración.

> Última actualización: 2026-10-13

## Estado

| Fase | Paso | Estado |
|---|---|---|
| 1 | Arquitectura y servicios decididos | ✅ |
| 1 | `.gitignore` y primer commit | ✅ |
| 1 | Manual Word preparado para el bot | ✅ |
| 2 | 1. Entorno virtual `.venv` | ✅ |
| 2 | 2. Estructura de carpetas | ✅ |
| 2 | 3. `requirements.txt` e instalar librerías | ✅ |
| 2 | 4. `.env`, `.env.example` y `bot/config.py` | ⏳ creado, falta terminar la verificación y hacer el commit |
| 3 | Cuentas de OpenAI y Supabase, elegir modelos, rellenar el `.env` | ⏳ pendiente |
| 5 | Cuenta de Vercel y variables de entorno en producción | ⏳ pendiente |

---

## Fase 1: Preparación

### 1.1 Arquitectura
```
web/ (página) → api/ (FastAPI) → bot/ (motor) → knowledge/ (lectores + almacén)
                    [Vercel]                         ↕ API de OpenAI · Supabase
```
- **Vercel** (gratis): aloja la página y la API.
- **Supabase** (gratis): base de datos con vectores (pgvector), login e imágenes.
- **API de OpenAI** (pago por uso): convierte texto en vectores y redacta las respuestas. Es el único costo.
- **GitHub** (gratis): guarda el código.

**Buena práctica:** el modelo de embeddings debe ser **el mismo** al indexar el manual y al buscar las preguntas. Si se cambia, hay que volver a indexar todo.

### 1.2 `.gitignore`: lo que nunca sube a GitHub
| Se ignora | Por qué |
|---|---|
| `.venv/` | Pesa mucho y se vuelve a crear con `requirements.txt` |
| `.env` | Contiene las claves secretas |
| `data/raw/` | El manual es un documento interno; el bot lo lee en local y lo sube a Supabase |
| `.archify/` | Diagramas que se pueden regenerar |
| `__pycache__/`, `*.pyc` | Archivos temporales de Python |

**Buenas prácticas:**
- Crear el `.gitignore` **antes** de tener archivos secretos. Lo que se sube a GitHub queda en el historial aunque se borre después.
- Antes de cada commit, revisar en **Source Control** (`Ctrl + Shift + G`) que no aparezcan `.venv`, `.env` ni el manual.
- Como lo ignorado no está en GitHub, hay que **guardar un respaldo aparte del manual**. En esta sesión se perdieron `.venv/` y `data/raw/` y hubo que recuperarlos.

### 1.3 Preparar el manual Word para el bot
El bot lee el Word con `python-docx`, que solo entiende bien un documento ordenado. Lo que se hizo:

1. **Copia de seguridad** del original antes de tocarlo.
2. **Estilos de título:** Título 1 para las secciones (1–6) y Título 2 para las subsecciones (2.1, 3.1 Deep Freeze, 3.2 Shadow Defender…). Para comprobarlo: *Vista → Panel de navegación*.
3. **Capturas unidas a sus flechas y recuadros:** seleccionar todo con `Ctrl + clic` → copiar → *Pegado especial → Imagen (PNG)* → borrar los originales.
4. **Todas las imágenes "En línea con el texto"**, justo debajo de su paso.
5. **Texto alternativo** en cada imagen: una frase que describe qué muestra.
6. **Sin cuadros de texto:** su contenido se pasó a párrafos normales.
7. **Datos sensibles fuera del texto:** la contraseña se cambió por "brindada por el administrador". La clave de licencia de las capturas se dejó porque es obsoleta.
8. **Erratas corregidas.**

**Resultado:** 18 imágenes en línea, 0 flotantes, 0 formas, 0 cuadros de texto, todas con texto alternativo.
Archivo final: `data/raw/MANUAL DE SOPORTE PARA COLABORADORES LUXv1.docx`.

**Por qué importa:**
- Los títulos con estilo permiten saber a qué sección pertenece cada fragmento.
- Las imágenes en línea quedan unidas a su paso.
- Los números dibujados en cuadros de texto se leían como texto suelto (el "2211").

---

## Fase 2: Entorno de Python

### Paso 1: Entorno virtual (`.venv`)
Es una "caja de herramientas" propia del proyecto: su Python y sus librerías, separados del resto del PC.

```powershell
py -3.12 -m venv .venv                     # crear (con Python 3.12)
.venv\Scripts\Activate.ps1                 # activar: aparece (.venv) en la terminal
python -m pip install --upgrade pip        # actualizar pip
```
- Si PowerShell bloquea la activación, ejecutar una sola vez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- En VS Code: `Ctrl + Shift + P` → **Python: Select Interpreter** → elegir `.venv`.

**Verificación:**
```powershell
python --version                 # Python 3.12.x
(Get-Command python).Source      # debe terminar en ...\chatbot_lux\.venv\Scripts\python.exe
```

**Buenas prácticas:**
- **Usar `py -3.12`** en lugar de `python`: el lanzador `py` elige la versión exacta aunque haya varias instaladas.
- **Un `.venv` se queda con la versión de Python con la que se creó.** Para cambiar de versión, se borra y se crea de nuevo.
- **Activar el `.venv` antes de instalar o ejecutar.** Si no, las librerías se instalan en el Python general del PC.
- **Seleccionar el intérprete en VS Code.** Así el editor no marca errores falsos y el botón ▶ usa el Python correcto.

### Paso 2: Estructura de carpetas
```
chatbot_lux/
├── api/            __init__.py                   ← la "ventanilla" (FastAPI)
├── bot/            __init__.py, config.py        ← el motor (busca y responde)
├── knowledge/      __init__.py                   ← lee, trocea y guarda las fuentes
│   └── loaders/    __init__.py                   ← un lector por tipo de fuente
├── data/
│   ├── raw/        (manual Word, fuera de Git)
│   └── images/     (imágenes extraídas)
├── web/                                          ← la página de los trabajadores
├── tests/          __init__.py                   ← pruebas
├── docs/           guia_configuracion.md
├── .env, .env.example, .gitignore, requirements.txt, CLAUDE.md
```
```powershell
New-Item -ItemType Directory -Force api, bot, knowledge\loaders, data\images, web, tests
New-Item -ItemType File api\__init__.py, bot\__init__.py, knowledge\__init__.py, knowledge\loaders\__init__.py, tests\__init__.py
```

**Buenas prácticas:**
- **Diseño modular:** cada carpeta tiene un solo trabajo. Si algo falla, se sabe dónde buscar.
- **`__init__.py`** (vacío) convierte una carpeta en un **paquete** importable, por ejemplo `from bot.config import ...`. Solo va en carpetas con código Python.
- **No crear archivos vacíos "por si acaso".** Cada archivo se crea cuando se escribe su código.
- Git no guarda carpetas vacías. `web/` y `data/images/` aparecerán en GitHub cuando tengan archivos.

### Paso 3: `requirements.txt`
Es la lista de librerías del proyecto. Va a Git, y Vercel la usa al desplegar.

```text
python-docx==1.2.0      # leer el manual Word
openai==3.29.0          # embeddings y respuestas de la IA
supabase==2.32.0        # base de datos vectorial e imágenes
python-dotenv==1.2.4    # leer el archivo .env
fastapi==0.143.0        # la API
uvicorn==0.54.0         # servidor para probar la API en local
```
```powershell
pip install -r requirements.txt     # instalar todo (con el .venv activado)
pip list                            # ver lo instalado
```

**Buenas prácticas:**
- **Fijar versiones con `==`:** así Vercel instala exactamente lo que se probó en el PC. Para actualizar, se cambia el número a propósito y se vuelve a probar.
- **Solo las librerías principales.** Sus dependencias las instala pip automáticamente.
- **Si se pierde el `.venv`:** crearlo de nuevo y ejecutar `pip install -r requirements.txt`.

### Paso 4: Claves secretas (`.env`, `.env.example`, `bot/config.py`)

| Archivo | Qué contiene | ¿Va a Git? |
|---|---|---|
| `.env` | Los valores reales de las claves | ❌ Nunca |
| `.env.example` | Los mismos nombres, **sin valores** (plantilla) | ✅ Sí |
| `bot/config.py` | El código que lee las claves | ✅ Sí |

```text
OPENAI_API_KEY=
SUPABASE_URL=
SUPABASE_SECRET_KEY=
```
- Formato: `NOMBRE=valor`, sin espacios ni comillas.
- `SUPABASE_SECRET_KEY` solo la usa el código Python, **nunca** la página `web/`.

**Cómo funciona `bot/config.py`:**
- `load_dotenv()` carga el `.env` en las variables de entorno. En Vercel no hay `.env`; las variables vienen de su panel y el código no cambia.
- `os.getenv("NOMBRE", "")` lee una variable. Si no existe, devuelve un texto vacío para que el programa no se rompa al importarlo.
- `claves_faltantes()` devuelve las claves vacías, para avisar con un mensaje claro.
- `if __name__ == "__main__":` solo se ejecuta al lanzar el archivo a mano. Al importarlo desde otro archivo, ese bloque se salta; el resto funciona igual.

**Verificación:**
```powershell
python -m bot.config
# Sin claves: "Faltan estas claves en el .env: OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SECRET_KEY"
```

**Buenas prácticas:**
- **Nunca escribir claves dentro del código.** El código va a GitHub.
- **Un solo archivo lee las claves** (`bot/config.py`). El resto del programa se las pide a él.
- **Nunca poner valores reales en `.env.example`.**
- **Comprobar las claves al arrancar** en lugar de esperar a que falle una llamada a OpenAI.
- **`config.py` reúne todo lo ajustable:** claves, modelos, número de fragmentos (K), rutas. Así el código no tiene números ni textos "escondidos".

---

## Comandos frecuentes

| Para… | Comando |
|---|---|
| Activar el entorno | `.venv\Scripts\Activate.ps1` |
| Reinstalar las librerías | `pip install -r requirements.txt` |
| Comprobar las claves | `python -m bot.config` |
| Ver qué cambió antes del commit | `Ctrl + Shift + G` (Source Control) |

---

## Por completar
- **Fase 2, paso 4:** terminar la verificación y hacer el commit de `.env.example` y `bot/config.py`.
- **Fase 3:**
  - crear las cuentas de OpenAI (con límite de gasto) y Supabase, y rellenar el `.env`;
  - elegir los modelos (embeddings y LLM) y añadirlos a `config.py`;
  - activar pgvector y crear la tabla de fragmentos.
- **Fase 5:** cuenta de Vercel, variables de entorno en su panel y login con Supabase Auth antes de publicar.
