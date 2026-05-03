# Configuración del Servidor Minecraft

Esta guía te explica cómo clonar este proyecto y dejarlo listo para funcionar, sin exponer datos privados.

## Estructura del Proyecto

```
minecraft_server/
├── admin_panel.py              # Panel de administración del servidor
├── run_admin_panel.bat         # Launcher para Windows
├── run_server_window.bat       # Abre ventana Java del servidor
├── requirements.txt            # Dependencias Python
├── panel_config.example.json   # Ejemplo de configuración (seguro)
├── .env.example                # Ejemplo de variables de entorno
├── .gitignore                  # Archivos excluidos de Git
│
├── servidor_rpg/               # Servidor Fabric 1.20.1 (compartido parcialmente)
│   ├── run.bat / run.sh        # Scripts para iniciar servidor
│   ├── server.properties       # Configuración del servidor (sin datos privados)
│   ├── eula.txt                # EULA (¡debes configurar como true!)
│   ├── user_jvm_args.txt       # Argumentos Java
│   ├── config/                 # Configuración de mods
│   ├── mods/                   # ⚠️ NO incluido en repo (descarga separadamente)
│   └── world/                  # ⚠️ NO incluido en repo (generado al ejecutar)
│
└── Documentación/
    ├── README.md               # Descripción general
    ├── SETUP.md                # Esta archivo
    ├── QUICK_START.md          # Inicio rápido
    ├── CAMBIAR_VERSION_SERVIDOR.md
    ├── ZEROTIER_GUIA_AMIGOS.md
    └── FIREWALL_SETUP.md
```

## 1. Clonar el Repositorio

```bash
git clone <your-repo-url>
cd minecraft_server
```

## 2. Instalar Dependencias Python

```powershell
# Windows PowerShell
py -3 -m pip install -r requirements.txt

# Linux/Mac
python3 -m pip install -r requirements.txt
```

## 3. Configurar Secretos (Credenciales)

Elige **UNA** de estas opciones:

### Opción A: Archivo local (desarrollo local)

```powershell
# Copia el archivo de ejemplo
Copy-Item panel_config.example.json panel_config.local.json

# Edita con tus valores reales
# Abre panel_config.local.json y configura:
# - rcon_password: contraseña fuerte para comandos
# - network_id: tu red Zerotier (si usas ZeroTier)
# - max_memory, min_memory: según tu PC
```

**panel_config.local.json** (ejemplo después de editar):
```json
{
  "rcon_password": "tu_contraseña_fuerte_aqui",
  "network_id": "154a350c86a332b5",
  "max_memory": "8G"
}
```

**Nunca commitees este archivo** — está en `.gitignore`.

### Opción B: Variables de entorno (recomendado para producción)

```powershell
# PowerShell
$env:RCON_PASSWORD = "tu_contraseña_fuerte"
$env:NETWORK_ID = "tu_network_id"
$env:MAX_MEMORY = "8G"
```

```bash
# Bash/Linux
export RCON_PASSWORD="tu_contraseña_fuerte"
export NETWORK_ID="tu_network_id"
export MAX_MEMORY="8G"
```

Ver `.env.example` para todas las variables disponibles.

## 4. Preparar el Servidor

### Paso A: Verificar EULA

```powershell
# Edita servidor_rpg/eula.txt
notepad servidor_rpg/eula.txt

# Cambia a:
# eula=true
```

### Paso B: Descargar/Copiar Mods (Opcional)

Los **mods NO se incluyen en el repositorio** (demasiado peso). Copialos manualmente:

```powershell
# Coloca tus mods aquí:
# servidor_rpg/mods/

# Los mods deben coincidir con:
# - Versión: Minecraft 1.20.1
# - Loader: Fabric 0.19.2
```

Consulta `CAMBIAR_VERSION_SERVIDOR.md` si necesitas cambiar versión.

### Paso C: Crear World (Primera Ejecución)

El servidor generará automáticamente un mundo la primera vez que ejecutes. La carpeta `servidor_rpg/world/` se creará automáticamente.

## 5. Ejecutar el Servidor

### Opción 1: Con el Panel (recomendado)

```powershell
.\run_admin_panel.bat
```

Desde el menú:
1. Selecciona `[1] Start Server`
2. Espera a que aparezca "Done!" en los logs

### Opción 2: Ventana Java Directa

```powershell
.\run_server_window.bat
```

## 6. Conectar Jugadores

### Localmente (misma red):

1. Abre Minecraft 1.20.1 con Fabric Loader
2. Multiplayer → Add Server
3. Dirección: `192.168.100.8:25565` (o tu IP local)

### Via Zerotier (desde fuera):

Sigue `ZEROTIER_GUIA_AMIGOS.md`

## Solución de Problemas

### "eula=false" error
→ Abre `servidor_rpg/eula.txt` y cambia a `eula=true`

### "Mods incompatibles"
→ Verifica que los mods sean para Minecraft 1.20.1 y Fabric Loader 0.19.2

### Puerto 25565 en uso
→ Cambia el puerto en `servidor_rpg/server.properties` (línea `server-port=`)

### RCON authentication failed
→ Verifica `rcon_password` en `panel_config.local.json` o `RCON_PASSWORD` en env

## Desplegar en la Nube (Oracle, Linode, etc.)

Para subir el servidor a un hosting en la nube:

1. Instala el repo en la VM
2. **NO uses** `panel_config.local.json` — usa **variables de entorno** en el cloud
3. Ejemplo en OCI:
   ```bash
   export RCON_PASSWORD="xxxx"
   export NETWORK_ID="xxxx"
   export MAX_MEMORY="4G"
   ./run.sh  # o run.bat si es Windows
   ```

## Seguridad

- ✅ **Credenciales**: Nunca en el repo, siempre en archivos locales o env vars
- ✅ **Mods**: Descárgalos de fuentes confiables
- ✅ **Contraseñas**: Cámbialas si alguna vez se expone
- ✅ **Firewall**: Solo abre puerto 25565 si es necesario

## Notas

- Fabric 1.20.1 requiere Java 17 o superior
- Ram mínima recomendada: 4GB (servidor + sistema)
- La carpeta `world/` puede crecer mucho; haz backups regularmente

---

¿Preguntas? Lee la documentación en orden:
1. `README.md` — Descripción general
2. `QUICK_START.md` — Inicio rápido
3. `ZEROTIER_GUIA_AMIGOS.md` — Para conectar amigos por VPN
4. `FIREWALL_SETUP.md` — Configuración de firewall

