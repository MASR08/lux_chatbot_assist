# Chatbot de Lux Gaming Center

## Rol de Claude
Arquitecto de Software Senior y Tutor Técnico Lead (IA, Python, Vercel, Supabase, OpenAI). Guía paso a paso al desarrollador
para diseñar e implementar este chatbot desde cero, sin abrumarlo con complejidad innecesaria.

## Contexto del proyecto
- **Qué es:** chatbot que responde consultas técnicas de Lux Gaming Center (negocio de alquiler de computadoras).
- **Usuarios:** los trabajadores entran a una web interna, hacen preguntas y el bot responde con texto y/o imágenes.
- **Fuentes de información:** la página web del negocio y un manual de usuario en Word (.docx).
- **Técnica:** RAG (leer y trocear fuentes → buscar pedazos relevantes → la IA redacta con esa info → mostrar imágenes asociadas).
- **Desarrollador:** está aprendiendo a programar desde cero; es su primer proyecto.
- **Entorno:** Visual Studio Code en Windows.
- **Despliegue futuro:** Vercel (hosting) + Supabase (base de datos) + API de OpenAI (embeddings y LLM).

## Reglas de trabajo
1. **Pedagogía mixta:** explicar siempre el *porqué* en español sencillo antes de dar código.
2. **Mapeo de archivos:** indicar siempre en qué archivo/carpeta va cada código (ej. `bot/config.py`).
3. **Diseño modular:** separar la lógica del bot, las fuentes de información y la API.
4. **Sin atajos incompletos:** nada de placeholders sin explicar. Los bloques largos se explican por partes.
5. **Validación continua:** al final de cada paso, dar una tarea concreta o verificación antes de avanzar.

## Fases
1. Alcance, arquitectura y preparación del entorno en VS Code.
2. Estructura de carpetas y entorno virtual de Python.
3. Motor del chatbot y lógica de respuestas.
4. Pruebas locales e integración de las fuentes de información.
5. Preparación para el despliegue en la nube.

## Etapas del proyecto (definidas por el desarrollador)
**Etapa 1: Preparación de datos (indexación e ingesta).** Se ejecuta una vez y se repite cuando cambian las fuentes.
Corre **en el PC del desarrollador** (script de Python dentro de `knowledge/`, con el `.venv` activado); no pasa por Vercel.

| Paso | Qué hace | Herramienta | Dónde (código) |
|---|---|---|---|
| A) Fuentes crudas | Manual Word, web (y en el futuro PDFs o artículos de soporte) | Archivo local en `data/raw/` (fuera de Git). Web: librería para descargar páginas (se elige al integrar la web) | `data/raw/` |
| B) Extracción | Sacar el texto plano y las imágenes (OCR solo si el documento está escaneado; el manual actual no lo está) | `python-docx` | `knowledge/loaders/word_loader.py` (web: `web_loader.py`) |
| C) Chunking | Cortar el texto en fragmentos pequeños e independientes, con sus metadatos | Python propio (sin servicios externos) | `knowledge/` |
| D) Embedding + carga | Convertir cada fragmento en un vector y guardarlo | **API de OpenAI** (modelo de embeddings, librería `openai`) → **Supabase** (pgvector para fragmentos y vectores; Supabase Storage para las imágenes; librería `supabase`) | `knowledge/store.py` |

**Etapa 2: Recuperación y generación (consulta del usuario).** Ocurre en cada pregunta.
En local corre en el PC; en producción, `web/` y `api/` corren en **Vercel**.

| Paso | Qué hace | Herramienta | Dónde (código) |
|---|---|---|---|
| 0) Entrada | El trabajador escribe la pregunta en la web, que la envía a la API | `web/` + **FastAPI** (alojadas en **Vercel**; login con **Supabase Auth** antes de publicar) | `web/`, `api/main.py` |
| 1) Vectorizar | Convertir la pregunta en un vector con el **mismo** modelo de embeddings de la Etapa 1 | **API de OpenAI** (embeddings) | `bot/engine.py` |
| 2) Búsqueda | Búsqueda vectorial por similitud | **Supabase** (pgvector) | `bot/engine.py` → `knowledge/store.py` |
| 3) Recuperar | Obtener los K fragmentos más relevantes con sus metadatos | **Supabase** (pgvector) | `knowledge/store.py` |
| 4) Armar prompt | Juntar la pregunta y los fragmentos en un solo prompt | Python propio | `bot/engine.py` |
| 5) Responder | El LLM responde basándose solo en esos fragmentos; si el fragmento tiene imagen, se adjunta (regla fija) | **API de OpenAI** (LLM) + **Supabase Storage** (imagen) | `bot/engine.py` → `api/` → `web/` |

Mapeo a carpetas: la Etapa 1 vive en `knowledge/` (loaders = A+B, chunking + embeddings + store = C+D). La Etapa 2 vive en `bot/engine.py`, se expone con `api/` y se ve en `web/`.

Claves y secretos (`OPENAI_API_KEY`, URL y clave de Supabase): en local van en `.env` (ignorado por Git); en producción, en las variables de entorno de Vercel. Se leen desde `bot/config.py`.

## Arquitectura propuesta
```
web/ (frontend) → api/ (FastAPI) → bot/ (motor) → knowledge/ (loaders + store)
                     [Vercel]                         ↕ API de OpenAI · Supabase
```

Estructura de carpetas propuesta (todavía no está creada; se crea en la Fase 2):
```
lux_chatbot_assist/
├── api/            __init__.py, main.py
├── bot/            __init__.py, config.py, engine.py
├── knowledge/      __init__.py, store.py, loaders/ (word_loader.py, web_loader.py)
├── data/           raw/ (manual Word), images/ (imágenes extraídas)
├── web/            index.html, style.css, app.js
├── tests/          __init__.py
├── .env, .gitignore, requirements.txt, README.md
```

## Decisiones de la V1
- Servicios:
  - **Vercel (plan Hobby, 0 USD):** hosting de `web/` y `api/`. Se conecta a GitHub y publica cada cambio. Hobby es "no comercial" según sus términos; el desarrollador (dueño del negocio) asume que el uso interno es aceptable (zona gris, riesgo bajo).
  - **Supabase (plan Free, 0 USD):** base vectorial (pgvector), login (Supabase Auth) e imágenes (Supabase Storage). Se pausa tras 1 semana sin actividad (se reactiva a mano, sin perder datos).
  - **API de OpenAI (pago por uso):** embeddings y LLM, directamente con OpenAI (se descartó Azure OpenAI por ser más complejo de configurar, con precio parecido). Es el único costo; con un modelo económico se estima ~1 a 3 USD/mes para ~3 000 preguntas. Usar saldo prepagado o límite de gasto. Los modelos concretos se eligen en la Fase 3.
  - **GitHub (0 USD):** repositorio del código.
- El modelo de embeddings debe ser el mismo en la Etapa 1 y en la Etapa 2; si se cambia, hay que volver a indexar.
- Cuentas: el desarrollador aún no tiene cuentas de Vercel, Supabase ni OpenAI (plataforma de API); se crean más adelante. GitHub probablemente ya existe (el repo tiene remoto `origin`); por confirmar.
- El desarrollador todavía no domina cómo se calculan los costos por tokens; reforzarlo con ejemplos reales cuando se elija el modelo (Fase 3).
- Orden de trabajo: primero el manual Word de punta a punta; la web se integra después.
- Respuestas según la fuente:
  - Manual: texto + imagen (si el fragmento usado tiene una asociada) + "Fuente: Manual, sección X" (sin enlace).
  - Web: solo texto (sin imágenes) + icono ↗ con enlace a la página, sin mostrar la URL completa.
  - Sin información: "No encontré esa información…", sin inventar.
- La imagen se muestra solo si el fragmento usado tiene una imagen asociada (regla fija; no lo decide la IA).
- Cada fragmento guarda metadatos: origen (manual/web), sección, URL (si es web) e imagen (si tiene).
- Ayudas visuales: formato Markdown (pasos numerados, negritas, listas) + etiqueta de origen (📘 Manual / 🌐 Web). La caja de avisos queda para después.
- Login: sin login en local; antes del despliegue hay que protegerlo con Supabase Auth.
- Entorno: Python 3.12.4 (el del `.venv`), Git 2.56. Ojo: en el PC también hay Python 3.15 (`C:\Python315`), que es el que responde a `python` sin el venv activado; algunas librerías (p. ej. MarkItDown/onnxruntime) aún no funcionan en 3.15. Usar siempre el venv.
- Herramientas de apoyo (fuera del venv, no forman parte del chatbot): Node.js + skill Archify para diagramas (salida en `.archify/`, ignorada por Git).

## Progreso
- **Fase actual:** cerrando la Fase 1 (última sesión: 2026-10-12).

### Hecho
- **Arquitectura decidida:** Vercel + Supabase + API de OpenAI (se descartó Azure). Las etapas indican qué herramienta se usa en cada paso.
- **Entorno virtual:** creado en `.venv/` (Python 3.12.4). Sin librerías instaladas todavía (las del Python global no se ven desde el venv). Activación: PowerShell `.venv\Scripts\Activate.ps1` (ya se explicó `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`); cmd `.venv\Scripts\activate.bat`.
- **`.gitignore`:** creado (ignora `.venv/`, `.env`, `data/raw/`, `.archify/`, `__pycache__/`, `*.pyc`). El manual no se sube a Git (no hace falta: la ingesta corre en local y sube a Supabase); el desarrollador debe guardar un respaldo aparte. Esto NO resuelve que la contraseña llegue al bot.
- **Git:** el repositorio ya tiene remoto (`origin/main`), así que probablemente ya existe la cuenta de GitHub (confirmar). Pendiente el primer commit con `.gitignore` y `CLAUDE.md` (lo hace el desarrollador).
- **Diagrama de las dos etapas:** generado con Archify en `.archify/workflow-etapas-chatbot-20261012-205029/etapas-chatbot.html` (todavía muestra Azure OpenAI; regenerarlo con OpenAI si se quiere).
- **Manual analizado:** `data/raw/MANUAL DE SOPORTE PARA COLABORADORES LUX.docx`. Secciones 1 a 6 (2.1 Fortnite/Epic, 2.2 VALORANT/LOL, 3 descongelar Deep Freeze/Shadow Defender, 4 soporte en SENET, 5 volver a congelar, 6 prueba final). Los títulos NO usan estilos de Título de Word y **todo el texto está en negrita**, así que no hay forma de distinguir títulos sin aplicar estilos. La contraseña de administrador aparece **4 veces** en el texto (2 en la sección 3, 2 en la sección 5). El "2211" suelto no es una errata: son los números 1 y 2 de círculos dibujados sobre capturas de Shadow Defender; desaparece al unir esas capturas.
- **Revisión de imágenes (2026-10-12):** 22 PNG, solo 1 "en línea con el texto", 41 elementos flotantes, 22 formas dibujadas (recuadros/flechas rojas sobre capturas), varios cuadros de texto, 0 con texto alternativo, 3 imágenes de 0–1 KB. La captura de Deep Freeze muestra parte de la clave de licencia.
- **Prueba con la imagen del Paso 5 (sección 3):** en `data/raw/pruebas/` (ignorado por Git) están el `.docx` de solo la página 3 con la captura unida a sus 2 recuadros, en línea y con texto alternativo; la imagen original y la unida en PNG; y el resultado de MarkItDown en `.md`. Conclusiones: la imagen arreglada sale en su sitio con descripción; las flotantes salen mal ubicadas o sin flechas; MarkItDown no guarda las imágenes (deja `data:image...` recortado), así que **se mantiene `python-docx` para `word_loader.py`** y MarkItDown queda, como mucho, para revisar el manual.
- **Decisión sobre imágenes en el bot:** cada imagen se guarda como archivo (`data/images/` → Supabase Storage) y su dirección va en los **metadatos** del fragmento, no en el texto que recibe la IA (cero tokens). El texto alternativo puede ir en el fragmento (pocos tokens, mejora la búsqueda).
- **Herramientas evaluadas:** Archify (instalado como skill global en `~/.agents/skills/archify`, enlazado a Claude Code; requiere Node.js, ya instalado). Spec Kit de GitHub (no por ahora; quizá más adelante). MarkItDown (solo como revisor).

### Pendiente del desarrollador
1. **Decidir qué hacer con la contraseña** (4 veces en el texto) y con la **clave de licencia** visible en la captura de Deep Freeze: quitarla, filtrarla al indexar o mantenerla.
2. **Decidir quién arregla el manual:** el desarrollador en Word (siguiendo el ejemplo del Paso 5) o Claude generando una copia corregida del manual completo, imagen por imagen, para revisarla al final.
3. **Aplicar estilos Título 1/Título 2** (se explicó paso a paso; verificar con Vista → Panel de navegación).
4. **Preparar las imágenes:** unir cada captura con sus flechas (Pegado especial → Imagen PNG), ponerlas "En línea con el texto" bajo su paso, añadir texto alternativo, revisar las 3 diminutas, y escribir como texto la información que solo esté en imágenes. Objetivo de la verificación: flotantes = 0, formas = 0, todas en línea y con texto alternativo (Claude puede volver a contarlas).
5. **Corregir errores del manual:** en la sección 5, el bloque de Shadow Defender dice "Deep Freeze"; hay un "2." repetido en la sección 4.
6. **Hacer el primer commit y push** de `.gitignore` y `CLAUDE.md`.
7. Más adelante: la URL de la web y las cuentas de Supabase y OpenAI (Fase 3) y de Vercel (Fase 5).

### Siguiente con Claude
- Cerrar la Fase 1 con las decisiones anteriores y empezar la Fase 2: estructura de carpetas, `requirements.txt`, instalar librerías en el venv, `.env` y `bot/config.py`.
- Opcional, propuesto y aplazado: una prueba que guarde las imágenes como archivos y genere Markdown que apunte a ellas (vista previa de `word_loader.py`).

- Historial de la primera conversación: `claude_conversation.md`.

> Claude: actualiza la sección "Progreso" al terminar cada paso o fase.
