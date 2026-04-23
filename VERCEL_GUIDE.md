# 🔥 GUÍA VERCEL ESPECÍFICA (Alternativa Premium)

Si el cliente quiere máximo control y velocidad, Vercel es ideal.

## ¿Por qué Vercel?
✅ Más rápido (CDN global)
✅ Dominio personalizado
✅ Más control técnico
✅ Escalable
❌ Requiere más setup
❌ Streamlit en Vercel tiene limitaciones

## Opción A: Vercel + Streamlit (Recomendado para Vercel)

### 1. Instalar Vercel CLI
```bash
npm install -g vercel
```

### 2. Crear `vercel.json` (ya está incluido)
```json
{
  "buildCommand": "pip install -r requirements.txt",
  "outputDirectory": ".",
  "env": {
    "STREAMLIT_SERVER_HEADLESS": "true"
  }
}
```

### 3. Deployar
```bash
vercel
```

### 4. Seguir el asistente:
- Crear proyecto en Vercel
- Conectar GitHub (recomendado)
- Auto-deploy en cada push

## Opción B: Vercel + FastAPI (Más Control)

Si necesitas verdadera escalabilidad, convertir a FastAPI:

```python
# api/index.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import streamlit.web.cli as cli

app = FastAPI()

@app.get("/")
async def root():
    # Ejecutar Streamlit aquí
    return {"message": "MicroExpr API"}
```

Luego deploy: `vercel`

## Opción C: Vercel + Heroku (Alternativa Más Simple)

Si Vercel con Streamlit da problemas:
1. Pushear a Heroku: `heroku create microexpr`
2. Deploy: `git push heroku main`
3. Ver en: `https://microexpr.herokuapp.com`

## Dominio Personalizado en Vercel

1. En dashboard Vercel → Proyecto
2. Settings → Domains
3. Agregar: `microexpr.tudominio.com`
4. Actualizar DNS en tu registrador

## Variables de Entorno en Vercel

Si necesitas APIs o keys:
1. Vercel Dashboard → Settings → Environment Variables
2. Agregar: `CLAVE=valor`
3. Redeploy automático

## Troubleshooting Vercel

| Error | Solución |
|-------|----------|
| Build fails | Revisar logs: `vercel logs` |
| Timeout | Reducir tamaño modelos `.pkl` |
| CORS error | Agregar headers en `vercel.json` |
| Cámara no funciona | Streamlit requiere HTTPS (Vercel lo proporciona) |

## Monitoreo en Vercel

- Uptime: Dashboard automático
- Logs: `vercel logs tu-proyecto`
- Analytics: Ver en dashboard

## Costo

| Plan | Precio |
|------|--------|
| Hobby | Gratis (limitado) |
| Pro | $20/mes |
| Enterprise | Contactar |

Para este proyecto: **Hobby** (gratis) es suficiente.

## Actualizar App en Vercel

1. Hacer cambios locales
2. Commit a GitHub: `git push`
3. Vercel auto-deploya
4. App actualizada en 30-60 segundos

**¡Listo para producción premium! 🚀**
