# Servidor NeoForge

Esta carpeta contiene la estructura base de un servidor NeoForge (mod loader alternativo a Fabric).

## Diferencias con Fabric

| Aspecto | Fabric | NeoForge |
|--------|--------|----------|
| **Loader** | Fabric Loader | NeoForge |
| **Soporte** | Comunidad independiente | MangoHud/Neoforged |
| **Java recomendado** | Java 17 | Java 21 |
| **Mods** | Fabric mods | NeoForge mods (algunas diferencias) |

## Estructura

```
servidor_neoforge/
├── run.bat / run.sh          # Scripts para iniciar servidor
├── run_java21.bat            # Launcher con Java 21 explícito
├── server.properties         # Configuración del servidor
├── eula.txt                  # EULA (debe ser true para funcionar)
├── user_jvm_args.txt         # Argumentos Java (RAM, optimizaciones)
│
├── config/                   # Configuración de mods (auto-generada)
├── configureddefaults/       # Configuración por defecto
├── defaultconfigs/           # Más configuraciones de NeoForge
├── mods/                     # Mods NeoForge (descargar aparte)
│
├── world/                    # Mundo (generado al iniciar)
└── libraries/                # Dependencias de NeoForge
```

## Requisitos

- **Java 21** (NeoForge requiere Java 21 como mínimo)
- **RAM:** 6GB mínimo (configurado en `user_jvm_args.txt`)
- **Mods compatibles:** Solo mods NeoForge (no son 100% compatibles con Fabric)

## Primeros pasos

1. **Acepta EULA:**
   ```powershell
   notepad eula.txt
   # Cambia a: eula=true
   ```

2. **Verifica Java 21:**
   ```powershell
   java -version
   ```

3. **Descarga mods NeoForge** y colócalos en `mods/`

4. **Ejecuta:**
   ```powershell
   .\run_java21.bat
   # O simplemente:
   .\run.bat
   ```

## Notas importantes

- Los mods de Fabric NO funcionan en NeoForge (y viceversa)
- NeoForge requiere Java 21 obligatoriamente
- La configuración es casi idéntica a Fabric pero con diferentes mods
- El mundo es 100% compatible (puedes pasar datos entre loaders)
