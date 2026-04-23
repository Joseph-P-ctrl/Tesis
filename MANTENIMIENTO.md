# 🛠️ GUÍA DE MANTENIMIENTO - POST-DESPLIEGUE

## DESPUÉS DEL DESPLIEGUE

La app está en vivo. Aquí está cómo mantenerla.

---

## 📊 MONITOREO DIARIO

### Streamlit Cloud
```
1. Ve a https://share.streamlit.io/
2. Click en tu app "microexpr"
3. Arriba a la derecha: "Settings"
4. Tab "Logs"
5. Busca errores
```

### Vercel
```
1. Ve a https://vercel.com/dashboard
2. Selecciona "microexpr"
3. Tab "Deployments"
4. Ver estado (verde = ok, rojo = error)
5. Click en deploy → "Logs"
```

### Health Check
```
Cada semana:
- Probar cámara (encender, capturar)
- Probar video (subir, analizar)
- Descargar CSV (verificar datos)
- Verificar no haya errores (F12 en browser)
```

---

## 🔄 ACTUALIZAR LA APP

### Cambio simple (tema, texto, UI)
```
1. Editar src/app.py en GitHub directamente
   - O en editor local → git push
2. Streamlit Cloud: Auto-actualiza en 30 seg
3. Vercel: Auto-actualiza en 1-2 min
4. Refresca el navegador (Ctrl+R)
```

### Cambio complejo (nuevos modelos, funcionalidad)
```
1. Editar localmente
2. Probar: streamlit run src/app.py
3. Si ok → git commit → git push
4. Deploy actualiza automáticamente
```

### Agregar dependencia nueva
```
1. pip install nuevo_paquete
2. pip freeze > requirements.txt
3. git push
4. Cloud re-instala automáticamente
```

---

## 🚨 SOLUCIONAR PROBLEMAS

### App no carga
```
Streamlit Cloud:
1. Settings → Reboot script
2. Si persiste → delete → redeploy

Vercel:
1. Dashboard → Redeploy
2. Revisar logs en "Deployments"
```

### Errores de "Module not found"
```
1. Revisar que todas las dependencias estén en requirements.txt
2. pip install paquete_faltante
3. pip freeze > requirements.txt
4. git push
```

### Resultado incorrecto
```
Si la predicción parece mal:
1. Verificar iluminación
2. Acercarse más
3. Probar con rostro diferente
4. (Sin modelos reales, demo mode simula)
```

### Cámara/Micrófono no funciona
```
1. Verificar permisos del navegador
2. Permitir cámara: Settings → Privacy
3. HTTPS requerido (Streamlit Cloud = automático)
4. Probar en otro navegador
```

### Video muy lento
```
1. Video grande → Reducir a < 2 min
2. Internet lenta → Usar WiFi estable
3. Server ocupado → Esperar o probar después
4. Si persiste → Contactar soporte
```

---

## 📈 ESCALAR (Si crece el uso)

### Si muchos usuarios simultáneos:
```
Streamlit Cloud:
- Upgrade a plan "Starter" o superior
- https://streamlit.io/cloud/pricing

Vercel:
- Upgrade a plan "Pro" ($20/mes)
- Auto-escalado con más users
```

### Si modelo es muy lento:
```
1. Optimizar modelo (reducir tamaño)
2. Usar GPU (Vercel Pro permite)
3. Caché agresivo
4. Procesamiento async
```

### Si almacenamiento es problema:
```
- Streamlit Cloud: 1GB gratis
- Vercel: 100MB per deployment
- Si falta: agregar base de datos (MongoDB, etc.)
```

---

## 🆙 ACTUALIZACIONES IMPORTANTES

### Actualizar Streamlit
```
1. Cambiar en requirements.txt:
   streamlit>=1.28.0 → streamlit>=1.30.0
2. git push
3. Cloud re-instala
```

### Actualizar OpenCV (si hay bugs)
```
1. pip install --upgrade opencv-python
2. pip freeze > requirements.txt
3. git push
```

### Cambiar Python version
```
1. Crear archivo runtime.txt:
   python-3.11
2. git push
3. Cloud usa nueva versión
```

---

## 📊 ESTADÍSTICAS DE USO

### Streamlit Cloud
```
1. Settings → App usage
2. Ver:
   - Users activos
   - Sessions
   - Memoria usada
   - CPU
```

### Vercel
```
1. Analytics en dashboard
2. Ver:
   - Requests/día
   - Response time
   - Error rate
   - Geo (dónde usan)
```

---

## 🔒 SEGURIDAD POST-DESPLIEGUE

- ✅ Streamlit Cloud = HTTPS automático
- ✅ Vercel = HTTPS automático
- ⚠️ No guardar fotos (se descartan automático)
- ⚠️ No poner credenciales en código (usar .env)
- ⚠️ Revisar logs regularmente (sin datos sensibles)

### Si hay breach
```
1. Cambiar contraseña GitHub
2. Revisar commits
3. Revertir si necesario (git revert)
4. Re-deploy
```

---

## 📝 LOGS Y DEBUGGING

### Ver logs Streamlit Cloud
```
Settings → Logs → Buscar "error"
```

### Ver logs Vercel
```
Dashboard → Deployments → Click deploy → Logs
```

### Activar debug local
```
STREAMLIT_LOGGER_LEVEL=debug streamlit run src/app.py
```

### Registrar eventos
```
# En app.py:
st.write("DEBUG: valor =", variable)
print("DEBUG:", variable)  # Aparece en logs
```

---

## 🎯 TAREAS MENSUALES

- [ ] Revisar logs (buscar errores)
- [ ] Probar todas las funciones
- [ ] Backup de código (GitHub = automático)
- [ ] Actualizar dependencias si hay updates
- [ ] Revisar estadísticas de uso
- [ ] Responder issues de usuarios

---

## 💾 BACKUP Y RECOVERY

### Código está en GitHub (automático backup)
```
git clone https://github.com/TU_USUARIO/microexpr.git
```

### Recuperar versión anterior
```
git log  # Ver histórico
git revert COMMIT_ID  # Volver a versión
git push  # Re-deploy
```

### Si cloud se cae
```
Streamlit Cloud:
- Cambiar repositorio a Vercel
- O a otro Streamlit

Vercel:
- Cambiar a Streamlit Cloud
- O a Heroku/Railway
```

---

## 🧪 TESTING PRE-UPDATE

Antes de actualizar:

1. **Local**
   ```bash
   streamlit run src/app.py
   python validate.py
   ```

2. **Manual**
   - Probar cámara
   - Probar video
   - Probar CSV

3. **GitHub**
   - git push a rama "testing"
   - Deploy desde rama
   - Verificar

4. **Production**
   - Si todo ok → merge main
   - Auto-deploy en production

---

## 📞 SOPORTE

| Problema | Dónde Reportar |
|----------|----------------|
| Bug Streamlit | https://discuss.streamlit.io/ |
| Bug Vercel | https://vercel.com/support |
| Código propio | GitHub Issues |
| ML Model | Contactar equipo |

---

## ✅ CHECKLIST MENSUAL

- [ ] Revisar logs
- [ ] Probar funciones
- [ ] Ver estadísticas
- [ ] Actualizar dependencias
- [ ] Responder usuarios
- [ ] Backup confirmado

---

**La app está en buenas manos. ¡Felicidades! 🚀**

Última actualización: Abril 2026
