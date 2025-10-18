# Guía: Cómo Modificar Rutas de Configuración

## 📍 Ubicación Central de Rutas

Todas las rutas de archivos de configuración están definidas en:
```
src/ePy_docs/config/setup.epyson
```

## 🔧 Modificar Rutas

### Ejemplo 1: Mover archivo de colores

**Antes:**
```json
{
  "config_files": {
    "colors": "internals/styling/colors.epyson"
  }
}
```

**Después (nueva ubicación):**
```json
{
  "config_files": {
    "colors": "config/colors.epyson"
  }
}
```

**Pasos:**
1. Editar `config/setup.epyson`
2. Cambiar la ruta en `config_files`
3. Mover físicamente el archivo a la nueva ubicación
4. Reiniciar aplicación (ConfigManager recarga automáticamente)

### Ejemplo 2: Agregar nuevo archivo de configuración

**En `config/setup.epyson`:**
```json
{
  "config_files": {
    ...archivos existentes...,
    "validation": "internals/validation/rules.epyson",
    "templates": "resources/templates/default.epyson"
  }
}
```

**Uso en código:**
```python
from ePy_docs.config import ConfigManager

cm = ConfigManager()
validation_config = cm.get_config('validation')
templates_config = cm.get_config('templates')
```

### Ejemplo 3: Organizar por categorías

```json
{
  "config_files": {
    "colors": "config/styling/colors.epyson",
    "fonts": "config/styling/fonts.epyson",
    
    "tables": "config/formatting/tables.epyson",
    "images": "config/formatting/images.epyson",
    "text": "config/formatting/text.epyson",
    
    "pdf": "config/output/pdf.epyson",
    "html": "config/output/html.epyson"
  }
}
```

## ⚠️ Importantes

### ✅ Hacer:
- Usar rutas relativas al paquete (`internals/`, `config/`, etc.)
- Mantener extensión `.epyson`
- Verificar que el archivo existe en la nueva ubicación
- Actualizar `setup.epyson` antes de mover archivos

### ❌ No Hacer:
- Usar rutas absolutas (`C:/Users/...`, `/home/...`)
- Usar rutas con `src/` (solo funciona en desarrollo)
- Cambiar nombres de claves sin actualizar código que las usa
- Olvidar mover el archivo físico después de cambiar la ruta

## 🧪 Verificar Cambios

Después de modificar rutas, ejecutar:

```python
from ePy_docs.config import ConfigManager

cm = ConfigManager()

# Ver todas las configs cargadas
print("Configs:", list(cm._configs.keys()))

# Verificar una específica
config = cm.get_config('nombre_del_config')
if config:
    print("✅ Cargado correctamente")
else:
    print("❌ Error al cargar")
```

O usar el script de demo:
```bash
python demo_config_manager.py
```

## 📋 Checklist para Modificar Rutas

- [ ] Editar `config/setup.epyson`
- [ ] Actualizar ruta en sección `config_files`
- [ ] Crear directorio destino si no existe
- [ ] Mover archivo físico a nueva ubicación
- [ ] Ejecutar `demo_config_manager.py` para verificar
- [ ] Verificar que aparece `✅` en la lista de archivos
- [ ] Probar en código que usa esa configuración

## 🔄 Rollback en Caso de Error

Si algo sale mal:

1. **Restaurar ruta anterior en setup.epyson**
2. **Mover archivo de vuelta a ubicación original**
3. **Reiniciar aplicación**

El ConfigManager mostrará warnings si no encuentra archivos:
```
⚠️ Warning: Config file not found: /ruta/incorrecta/archivo.epyson
```

## 📚 Estructura Recomendada

```
src/ePy_docs/
├── config/
│   ├── setup.epyson          # 👈 RUTAS AQUÍ
│   └── config_manager.py
├── internals/
│   ├── formatting/
│   │   ├── tables.epyson
│   │   ├── images.epyson
│   │   └── text.epyson
│   ├── styling/
│   │   └── colors.epyson
│   └── generation/
│       ├── pdf.epyson
│       └── html.epyson
└── resources/
    └── configs/              # Opcional: configs de usuario
```

## 💡 Mejores Prácticas

1. **Agrupar por función:** Mantener archivos relacionados juntos
2. **Nombres descriptivos:** `tables.epyson` no `t.epyson`
3. **Estructura consistente:** Usar mismo patrón de directorios
4. **Documentar cambios:** Actualizar README cuando se reorganiza
5. **Versionar:** Usar git para rastrear cambios en rutas

---

**Última actualización:** 18 de octubre de 2025
