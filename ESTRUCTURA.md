# 📁 ESTRUCTURA DEL PROYECTO

```
d:/Tesis/
│
├── 📄 README.md
│   └─ Guía general del proyecto
│
├── 📋 DEPLOY.md ⭐ LEER PRIMERO
│   └─ Opciones de despliegue (Streamlit Cloud, Vercel, Railway)
│
├── 🚀 QUICK_DEPLOY.txt
│   └─ Resumen de 3 pasos para Streamlit Cloud
│
├── 🔥 VERCEL_GUIDE.md
│   └─ Instrucciones detalladas para Vercel (alternativa)
│
├── 📊 DOCUMENTATION.md
│   └─ Cómo usar la app (para usuarios finales)
│
├── ✅ ENTREGA_CLIENTE.md
│   └─ Checklist antes de entregar
│
├── 📄 RESUMEN.txt
│   └─ Resumen ejecutivo (5 min lectura)
│
├── 🐍 src/
│   ├── app.py ⭐ PROGRAMA PRINCIPAL
│   │   └─ ~470 líneas de código real
│   │   ├─ UI Streamlit (español)
│   │   ├─ Captura por cámara
│   │   ├─ Análisis de video
│   │   ├─ Modo ráfaga (burst)
│   │   └─ Exportación CSV
│   │
│   ├── config.py
│   │   └─ Configuración centralizada
│   │   ├─ Rutas a modelos
│   │   ├─ Parámetros ML
│   │   └─ Labels de emociones
│   │
│   ├── model.py
│   │   └─ Modelo básico Scikit-learn
│   │   ├─ load_model() → carga .pkl
│   │   └─ predict_emotion()
│   │
│   ├── model_advanced.py
│   │   └─ Modelo avanzado (ensemble)
│   │   ├─ load_advanced_model() → carga .pkl
│   │   └─ predict_emotion_advanced()
│   │
│   └── preprocessing.py
│       └─ Visión por computadora
│       ├─ FaceDetector (Haar cascade)
│       ├─ extract_face_roi()
│       ├─ sequence_to_motion_features()
│       └─ to_gray()
│
├── 🤖 models/
│   ├── microexpr_model.pkl (opcional)
│   │   └─ Modelo básico entrenado
│   │
│   ├── microexpr_cnn_lstm.pkl (opcional)
│   │   └─ Modelo avanzado entrenado
│   │
│   └── [Sin estos, la app funciona en DEMO MODE]
│
├── 📊 data/
│   ├── dataset/
│   │   ├── happiness/ (fotos sonriendo)
│   │   ├── sadness/ (fotos tristes)
│   │   ├── anger/ (fotos enojadas)
│   │   └── ... (más emociones)
│   │   
│   └─ [Opcional: para entrenar modelos propios]
│
├── ⚙️ .streamlit/
│   └── config.toml
│       └─ Configuración Streamlit (colores, puerto, etc.)
│
├── 🔧 .env (no incluido, crear si necesario)
│   └─ Variables de entorno (APIs, keys, etc.)
│
├── 📦 requirements.txt ⭐ IMPORTANTE
│   └─ Todas las dependencias Python:
│       ├─ streamlit
│       ├─ opencv-python
│       ├─ numpy, pandas
│       ├─ scikit-learn
│       └─ etc.
│
├── 📝 vercel.json
│   └─ Configuración Vercel (alternativa)
│
├── 🎯 validate.py
│   └─ Script para validar setup
│       └─ python validate.py
│
├── 🔄 prepare_github.ps1 (Windows)
│   └─ Script para preparar GitHub
│
├── 🔄 prepare_github.sh (Linux/Mac)
│   └─ Script para preparar GitHub
│
├── 🚀 start.sh
│   └─ Script para iniciar app (Linux/Mac)
│
├── .gitignore
│   └─ Archivos a NO subir a GitHub
│       ├─ .venv/ (entorno virtual)
│       ├─ __pycache__/
│       ├─ *.pyc
│       └─ .env
│
└── .venv/
    └─ [Entorno virtual Python - NO SUBIR]
        ├─ Scripts/ (ejecutables)
        └─ Lib/ (paquetes instalados)
```

---

## 🔑 ARCHIVOS MÁS IMPORTANTES

| Archivo | Para Qué | Quién |
|---------|----------|-------|
| `src/app.py` | Aplicación | Dev + Usuario |
| `requirements.txt` | Instalar dependencias | Deploy automatizado |
| `DEPLOY.md` | Cómo desplegar | Cliente |
| `.streamlit/config.toml` | Config Streamlit | Dev |
| `vercel.json` | Config Vercel | Dev (si elige Vercel) |
| `validate.py` | Verificar setup | Dev antes de deploy |

---

## 📥 FLUJO DE DESPLIEGUE

```
1. Cliente clona repositorio
   ↓
2. `pip install -r requirements.txt`
   ↓
3. Elige opción de deploy:
   ├─ A) Streamlit Cloud → 1 click (RECOMENDADO)
   ├─ B) Vercel → vercel CLI
   └─ C) Railway/Hugging Face → Seguir pasos
   ↓
4. App en vivo 🎉
```

---

## 🎯 PARA EL CLIENTE

**El cliente NO necesita saber de Python ni código.**
- Solo sigue los pasos en `QUICK_DEPLOY.txt`
- O ve directamente a `https://share.streamlit.io/`

**Archivos que VER:**
1. `RESUMEN.txt` - 5 min lectura
2. `QUICK_DEPLOY.txt` - Pasos
3. `DOCUMENTATION.md` - Cómo usar

**Archivos que IGNORAR:**
- `src/` (código fuente)
- `.venv/` (entorno virtual)
- `ENTREGA_CLIENTE.md` (para desarrollador)

---

## ✅ VERIFICACIÓN PRE-DESPLIEGUE

Antes de entregar, ejecutar:
```bash
python validate.py
```

Debe mostrar todos ✅

---

## 🎉 LISTA DE ENTREGA

- [x] Código funcional (src/)
- [x] Documentación completa
- [x] Guías de despliegue
- [x] Scripts de validación
- [x] Configuración Streamlit
- [x] Configuración Vercel (alternativa)
- [x] .gitignore preparado
- [x] requirements.txt optimizado

**ESTADO: LISTO PARA PRODUCCIÓN ✅**

---

Última actualización: Abril 2026
