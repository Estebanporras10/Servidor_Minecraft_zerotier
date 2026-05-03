# Configuración de Mods

Los archivos `.toml`, `.json`, `.json5` y otros que van aquí son generados por los mods.

## Cómo funciona

1. Coloca los mods en `mods/`
2. Inicia el servidor
3. Los mods generan sus archivos de configuración aquí automáticamente

## Importante

- **NO editees los archivos mientras el servidor corre** — se sobrescribirán
- Detén el servidor antes de cambiar configuración
- Los cambios en `config/` entran en efecto cuando reinicies el servidor

## Notas

- Algunos mods dejan archivos en `configureddefaults/` también
- Algunos mods pueden crear subcarpetas adicionales aquí
- Cada versión de Minecraft/Fabric puede tener diferentes configuraciones
