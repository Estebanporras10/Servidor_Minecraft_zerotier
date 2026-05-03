# Mundo del Servidor

Esta carpeta contiene el mundo (mapa, estructuras, datos de jugadores).

## No incluido en Git

La carpeta `world/` está excluida del repositorio porque:
- Es muy grande (puede ocupar GBs)
- Se genera automáticamente al iniciar el servidor
- Contiene datos únicos de tu servidor

## Respaldos

Haz respaldos regularmente:

```bash
# Copia la carpeta completa
robocopy world/ .\backups\world_$(date +%Y%m%d_%H%M%S)\ /E

# O usa compresión
Compress-Archive -Path world -DestinationPath backups\world_backup.zip
```

## Primeras ejecución

El servidor creará automáticamente:
- `world/region/` — datos del mapa
- `world/playerdata/` — datos de jugadores
- `world/stats/` — estadísticas

Todo se genera cuando el servidor inicia por primera vez.
