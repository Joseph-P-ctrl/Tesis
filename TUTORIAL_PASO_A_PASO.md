# 🎬 TUTORIAL PASO A PASO - DESPLEGAR EN 5 MINUTOS

## OPCIÓN 1: STREAMLIT CLOUD (Recomendado - Más fácil)

### PASO 1: Preparar GitHub
```
1. Abre https://github.com
2. Click en "+" (arriba a la derecha)
3. "New repository"
4. Nombre: microexpr
5. Descripción: "Detección de microexpresiones"
6. Público (public)
7. Click "Create repository"
```

### PASO 2: Subir código
```
Opción A: Interfaz web (sin terminal)
1. Click en "Add file" → "Upload files"
2. Selecciona TODOS los archivos del proyecto
3. Click "Commit"

Opción B: Desde terminal (si sabes Git)
1. Abre PowerShell en la carpeta del proyecto
2. git init
3. git add .
4. git commit -m "Initial commit"
5. git remote add origin https://github.com/TU_USUARIO/microexpr.git
6. git push -u origin main
```

### PASO 3: Desplegar en Streamlit Cloud
```
1. Ve a https://share.streamlit.io/
2. Click en "Deploy an app"
3. "Continue with GitHub"
4. Autoriza a Streamlit
5. Selecciona tu repositorio "microexpr"
6. Deja "main" y "src/app.py"
7. Click "Deploy"
8. ¡Espera 2-3 minutos!
```

### PASO 4: ¡Listo!
```
Tu app estará en:
https://microexpr-XXXXX.streamlit.app/

Comparte este link con clientes
```

---

## OPCIÓN 2: VERCEL (Alternativa con más control)

### PASO 1: Instalar Node.js
```
1. Descarga desde https://nodejs.org/
2. Instala (versión LTS)
3. Abre PowerShell y verifica:
   node --version
   npm --version
```

### PASO 2: Instalar Vercel
```
PowerShell:
npm install -g vercel
```

### PASO 3: Subir a GitHub (igual que Opción 1)
```
(Seguir PASO 2 de arriba)
```

### PASO 4: Desplegar en Vercel
```
PowerShell (en carpeta del proyecto):
vercel

Selecciona:
- Vercel account
- Project name: microexpr
- Framework: Other
- Output directory: . (punto)

Espera deployment...
```

### PASO 5: ¡Listo!
```
URL: https://microexpr.vercel.app/ (o similar)

Puedes agregar dominio personalizado después
```

---

## 📱 CÓMO USAR LA APP (Para clientes)

### Opción A: Análisis por Cámara
```
1. Click "Encender cámara"
2. Permite acceso a cámara en navegador
3. Click "Capturar"
4. Ver resultado (emoción + % confianza)
5. Listo!
```

### Opción B: Análisis por Video
```
1. Click "Subir video"
2. Selecciona video (MP4, AVI, MOV)
3. Click "Analizar video"
4. Espera que procese (muestra % avance)
5. Ver tabla de resultados
6. Click "Descargar CSV"
```

---

## 🆘 PROBLEMAS COMUNES

### "Module not found" en Streamlit Cloud
**Solución:** requirements.txt tiene errores
- Ir a logs: Settings → View logs
- Agregar paquete faltante en requirements.txt
- Hacer git push para re-deployar

### Cámara no funciona
**Causa:** El navegador no permite acceso
- Chrome/Firefox: Bloquear → Permitir → Recargar
- Safari: Preferencias → Privacidad → Cámara → Permitir
- Streamlit Cloud requiere HTTPS (automático)

### "No se detectó rostro"
**Soluciones:**
- Acercarse más a la cámara
- Mejor iluminación frontal
- Quitar accesorios (lentes grandes)
- Rostro completo visible

### Video muy lento
**Causa:** Video muy grande o hardware lento
- Usar videos < 2 minutos
- Reducir resolución
- Esperar (es normal)

### Deploy no actualiza
**Solución:** Forzar refresco
- Streamlit: Settings → Reboot script
- Vercel: Dashboard → Redeploy
- Browser: Ctrl+Shift+R (hard refresh)

---

## ✅ CHECKLIST FINAL

Antes de compartir con clientes:

- [ ] App funciona localmente
- [ ] Cámara funciona
- [ ] Video analiza correctamente
- [ ] CSV se descarga
- [ ] Sin errores en consola (F12)
- [ ] Deploy completó sin errores
- [ ] URL funcionando desde otro dispositivo

---

## 💡 TIPS PRO

### Streamlit Cloud
- Auto-deploy en cada git push
- Logs automáticos
- Gratis hasta 3 apps
- HTTPS automático
- Sin mantenimiento

### Vercel
- Más rápido (CDN)
- Dominio personalizado fácil
- Analytics incluido
- Más flexible pero más complejo
- Versión gratuita limitada

### Para máxima performance
- Reducir tamaño de modelos
- Usar caché (@st.cache_resource)
- Comprimir videos
- CDN para imágenes

---

## 🎓 RECURSOS

- Streamlit docs: https://docs.streamlit.io/
- Vercel docs: https://vercel.com/docs
- GitHub Help: https://docs.github.com/
- Troubleshooting: Ver archivos DEPLOY.md

---

## 📞 SOPORTE

Si algo no funciona:
1. Revisar logs (botón Settings/Debug)
2. Ver DOCUMENTACIÓN.md
3. Buscar error en Google
4. Contactar al equipo

---

**¡Felicidades! Tu app MicroExpr está en producción! 🚀**

Versión: 1.0
Última actualización: Abril 2026
