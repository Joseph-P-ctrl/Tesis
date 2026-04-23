# 🎯 ÍNDICE - ¿QUÉ ARCHIVO LEER?

## PARA EL CLIENTE (NO técnico)

### Primero (5 min):
1. **[RESUMEN.txt](RESUMEN.txt)** - Qué es y cómo funciona
2. **[QUICK_DEPLOY.txt](QUICK_DEPLOY.txt)** - 3 pasos para desplegar

### Luego (10 min):
3. **[TUTORIAL_PASO_A_PASO.md](TUTORIAL_PASO_A_PASO.md)** - Instrucciones detalladas
4. **[DOCUMENTATION.md](DOCUMENTATION.md)** - Cómo usar la app

### Si hay problemas (5-10 min):
5. **[MANTENIMIENTO.md](MANTENIMIENTO.md)** - Solucionar problemas

---

## PARA EL DESARROLLADOR/DEVOPS

### Setup (10 min):
1. **[ESTRUCTURA.md](ESTRUCTURA.md)** - Qué hay en cada carpeta
2. **[README.md](README.md)** - Descripción técnica general
3. `validate.py` - Verificar ambiente

### Despliegue (15 min):
4. **[DEPLOY.md](DEPLOY.md)** - Todas las opciones de deploy
5. **[QUICK_DEPLOY.txt](QUICK_DEPLOY.txt)** - Opción recomendada (Streamlit Cloud)
6. **[VERCEL_GUIDE.md](VERCEL_GUIDE.md)** - Si quiere Vercel

### Producción (5 min):
7. **[ENTREGA_CLIENTE.md](ENTREGA_CLIENTE.md)** - Checklist antes de entregar
8. **[MANTENIMIENTO.md](MANTENIMIENTO.md)** - Post-despliegue

---

## PARA INSTALAR Y EJECUTAR LOCALMENTE

```bash
# 1. Clonar
git clone <repo>
cd Tesis

# 2. Entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. Instalar
pip install -r requirements.txt

# 4. Validar
python validate.py

# 5. Ejecutar
streamlit run src/app.py
```

---

## ARCHIVOS POR USO

| Archivo | Para Qué | Leer Si |
|---------|----------|---------|
| **RESUMEN.txt** | Overview 5 min | Cliente quiere saber qué es |
| **QUICK_DEPLOY.txt** | Deploy fácil | Cliente quiere empezar YA |
| **DEPLOY.md** | Todas opciones | Técnico eligiendo plataforma |
| **TUTORIAL_PASO_A_PASO.md** | Pasos detallados | Cliente necesita guía visual |
| **VERCEL_GUIDE.md** | Vercel específico | Cliente elige Vercel |
| **DOCUMENTATION.md** | Uso de la app | Usuario final |
| **ESTRUCTURA.md** | Carpetas/archivos | Dev entendiendo proyecto |
| **README.md** | Info general | Dev leyendo primero |
| **MANTENIMIENTO.md** | Post-deploy | Admin manteniendo |
| **ENTREGA_CLIENTE.md** | Checklist | Dev antes de entregar |

---

## FLUJO RECOMENDADO

### Escenario 1: Cliente quiere desplegar rápido
```
RESUMEN.txt 
    ↓
QUICK_DEPLOY.txt 
    ↓
Desplegar en Streamlit Cloud 
    ↓
DOCUMENTATION.md (si usuario final)
```

### Escenario 2: Desarrollador revisa proyecto
```
README.md 
    ↓
ESTRUCTURA.md 
    ↓
python validate.py 
    ↓
streamlit run src/app.py
```

### Escenario 3: Empresa quiere Vercel + dominio
```
DEPLOY.md 
    ↓
VERCEL_GUIDE.md 
    ↓
TUTORIAL_PASO_A_PASO.md 
    ↓
Desplegar 
    ↓
MANTENIMIENTO.md
```

### Escenario 4: Hay problema post-deploy
```
MANTENIMIENTO.md (Troubleshooting) 
    ↓
Revisar logs 
    ↓
Solucionar 
    ↓
OK ✅
```

---

## ARCHIVOS NO PARA LEER (Código)

- `src/app.py` - Código fuente (para dev)
- `src/config.py` - Config (para dev)
- `.streamlit/config.toml` - Config (auto)
- `vercel.json` - Config (auto)
- `requirements.txt` - Dependencias (auto)
- `.venv/` - Entorno (local, no usar)

---

## ARCHIVOS IMPORTANTES PERO AUTO

- `README.md` - Ya está
- `.gitignore` - Ya está
- `requirements.txt` - Ya está
- `validate.py` - Para ejecutar, no leer

---

## LINKS RÁPIDOS

| Tarea | Link |
|-------|------|
| Crear GitHub | https://github.com/new |
| Desplegar Streamlit | https://share.streamlit.io/ |
| Desplegar Vercel | https://vercel.com/new |
| Documentación Streamlit | https://docs.streamlit.io/ |
| Documentación Vercel | https://vercel.com/docs |

---

## RESUMEN DE ARCHIVOS

Total archivos de documentación: **11**
- 3 archivos cortos (5 min cada)
- 5 archivos medianos (10-15 min cada)
- 3 archivos técnicos (para dev)

**Tiempo total para leer TODO:** ~90 minutos
**Tiempo mínimo para desplegar:** ~15 minutos

---

## ✅ ORDEN RECOMENDADO

1. **RESUMEN.txt** ← Empieza aquí
2. **QUICK_DEPLOY.txt** ← Setup en 5 min
3. **TUTORIAL_PASO_A_PASO.md** ← Si necesita más detalle
4. **DOCUMENTATION.md** ← Después deployed
5. **MANTENIMIENTO.md** ← Si hay problemas

---

**¿No sabes por dónde empezar?**
→ Abre RESUMEN.txt (5 minutos)
→ Luego QUICK_DEPLOY.txt
→ ¡A producción!

Última actualización: Abril 2026
