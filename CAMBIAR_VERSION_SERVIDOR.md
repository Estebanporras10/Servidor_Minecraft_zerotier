# Cambio de versión del servidor

Este proyecto ya tiene dos carpetas separadas:

- `servidor_create/`: copia de respaldo del servidor anterior.
- `servidor_rpg/`: servidor activo preparado para Fabric 1.20.1.

## Para cambiar la versión otra vez

1. Haz respaldo de `servidor_rpg/` si el mundo o los mods actuales importan.
2. Vacía `servidor_rpg/` y vuelve a instalar el servidor con Fabric.
3. Usa el instalador de Fabric con una combinación válida de Minecraft y loader.
4. Actualiza `run.bat`, `run.sh` y `user_jvm_args.txt` si cambian los archivos generados.
5. Verifica que `eula.txt` tenga `eula=true`.
6. Copia solo los mods compatibles con la nueva versión a `servidor_rpg/mods/`.

## Comando usado para Fabric 1.20.1

```powershell
java -jar fabric-installer-1.1.1.jar server -mcversion 1.20.1 -loader 0.19.2 -downloadMinecraft -dir servidor_rpg
```

## Notas importantes

- Para Minecraft 1.20.1 se recomienda Java 17.
- Si el instalador deja una carpeta `.fabric` antigua durante una actualización, elimínala antes de reiniciar.
- Si solo cambias de mods y no de versión, no necesitas reinstalar el servidor.