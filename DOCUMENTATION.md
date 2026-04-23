# 📋 DOCUMENTACIÓN FINAL - MicroExpr

## ¿Qué es MicroExpr?

Aplicación web basada en IA que detecta microexpresiones faciales en fotos o videos. Utiliza:
- **Detección Facial**: Cascade de Haar
- **Análisis de Emociones**: Redes neuronales + Optical Flow
- **Modelos**: Básico (rápido) y Avanzado (preciso)

---

## 📱 Cómo Usar (Cliente)

### Opción 1: Análisis por Cámara
1. Click en "Encender cámara"
2. Captura una foto de tu rostro
3. Resultado inmediato (emoción + confianza)

### Opción 2: Análisis por Video
1. Sube un video MP4/AVI/MOV
2. Click en "Analizar video"
3. Descarga CSV con detalle frame-by-frame

---

## 🎯 Resultados

Para cada análisis obtienes:
- **Emoción detectada** (Felicidad, Tristeza, Sorpresa, etc.)
- **Nivel de confianza** (0-100%)
- **Bounding box** visual del rostro
- **Tabla exportable** en formato CSV

---

## ⚙️ Características Técnicas

| Característica | Descripción |
|---|---|
| **Backend** | Python + Streamlit |
| **ML Framework** | Scikit-learn |
| **Visión** | OpenCV (cv2) |
| **Detección facial** | Haar Cascade |
| **Video** | XVID codec (.avi) |
| **Exportación** | CSV, PNG |

---

## 🔐 Privacidad

- ✅ **Sin almacenamiento de datos** - Fotos/videos se procesan y se descartan
- ✅ **Sin conectar a internet** - (Streamlit Cloud = servidor privado)
- ✅ **Sin tracking** - No se registran interacciones

---

## 🆘 Solucionar Problemas

### La cámara no funciona
→ Asegúrate que: Streamlit Cloud usa HTTPS (seguro), navegador permite cámara

### "No se detectó rostro"
→ Acercarse más, mejorar iluminación, frontal

### Descarga lenta
→ Videos muy grandes toman tiempo. Usar clips < 2 min

### Modelo no entrena
→ Dataset debe tener: `dataset/EMOCION/foto1.jpg, foto2.jpg...`

---

## 📈 Próximas Mejoras (Opcionales)

- [ ] Análisis en tiempo real (streaming)
- [ ] Exportar video con anotaciones
- [ ] Dashboard de estadísticas
- [ ] Integración con Google Drive
- [ ] Soporte para múltiples rostros simultáneos

---

## 📞 Contacto Técnico

Para reportar bugs o solicitudes:
- GitHub Issues: [Tu repo]
- Email: [Tu email]

---

**Versión**: 1.0
**Última actualización**: Abril 2026
**Estado**: Producción ✅
