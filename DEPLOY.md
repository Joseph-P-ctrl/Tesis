# MicroExpr - Analizador de Microexpresiones Faciales

Aplicación web para detección de microexpresiones faciales usando Inteligencia Artificial y Optical Flow.

---

## 🚀 Despliegue en la Nube (Para el Cliente)

### **OPCIÓN 1: Streamlit Community Cloud ⭐ (RECOMENDADO - Gratis, 1 click)**

1. **Subir el proyecto a GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/TU_USUARIO/microexpr.git
   git push -u origin main
   ```

2. **Ir a https://share.streamlit.io/**
3. **Click en "Deploy an app"**
4. **Conectar GitHub y seleccionar este repositorio**
5. **Seleccionar:** 
   - Repository: `tu-usuario/microexpr`
   - Branch: `main`
   - Main file path: `src/app.py`
6. **Click "Deploy"** ✅

La app estará en vivo en: `https://microexpr-XXXXX.streamlit.app/`

---

### **OPCIÓN 2: Vercel + Python FastAPI (Alternativa)**

Si prefieres máximo control y escalabilidad:

1. **Crear archivo `api/index.py`** (ya incluido)
2. **Instalar Vercel CLI:**
   ```bash
   npm install -g vercel
   ```
3. **Desplegar:**
   ```bash
   vercel
   ```
4. **Seguir el asistente de Vercel**

---

### **OPCIÓN 3: Railway, Hugging Face Spaces o Heroku**

- **Hugging Face Spaces** (Streamlit integrado): https://huggingface.co/spaces
- **Railway**: https://railway.app/ 
- **Heroku** (requiere tarjeta): https://www.heroku.com/

---

## 📦 Requisitos para Ejecutar Localmente

```bash
# Clonar el proyecto
git clone <tu-repo>
cd Tesis

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
streamlit run src/app.py
```

Abre: http://localhost:8501

---

## 🎯 Funcionalidades

✅ **Foto única**: Captura, detecta rostro, analiza emoción
✅ **Modo ráfaga**: Grabar secuencia de fotos → genera video .avi
✅ **Subir video**: Analiza video MP4/AVI/MOV
✅ **Dos modelos**:
   - Básico: Rápido y ligero
   - Avanzado (Ensemble): Más preciso
✅ **Resultados exportables**: CSV con todas las detecciones
✅ **Diseño premium**: Dark mode con gradientes

---

## 📁 Estructura del Proyecto

```
Tesis/
├── src/
│   ├── app.py                 # App principal Streamlit
│   ├── config.py              # Configuración
│   ├── model.py               # Modelos básicos
│   ├── model_advanced.py      # Modelos ensemble
│   └── preprocessing.py       # Detección facial
├── models/                    # Guardar modelos entrenados (.pkl)
├── data/
│   └── dataset/               # Dataset para entrenar
├── requirements.txt           # Dependencias Python
├── vercel.json               # Config Vercel
├── .streamlit/
│   └── config.toml           # Config Streamlit
└── README.md
```

---

## 🔧 Configuración después del Despliegue

**Para que el modelo funcione con datos reales:**

1. Entrenar el modelo con tu dataset:
   ```bash
   python src/train_model.py --dataset data/dataset
   ```
2. Guardar los `.pkl` en carpeta `models/`
3. Actualizar el deploy

Sin archivos `.pkl`, la app funciona en **modo demo** (simulaciones).

---

## 🎨 Personalización

Editar `src/app.py`:
- **Colores**: Sección `EMOTION_COLORS`
- **Emociones**: Diccionario `EMOTION_ES`
- **Modelos**: Rutas en `src/config.py`

---

## 📞 Soporte

Para problemas en Streamlit Cloud:
- Ir a: https://discuss.streamlit.io/
- Consultar logs: Ver en "Settings" → "View logs"

---

**Nota:** La app está lista para producción. El cliente solo necesita:
1. GitHub + Streamlit Cloud (recomendado)
2. O Vercel + FastAPI (más avanzado)

¡Listo para compartir! 🚀
