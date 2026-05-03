🎮 GUÍA RÁPIDA - CONECTARSE AL SERVIDOR MINECRAFT
================================================

## 1️⃣ REQUISITOS

✓ Minecraft 1.20.1 instalado en tu PC
✓ Tener instalado Fabric Loader 0.19.2 (para usar mods después)
✓ La red del servidor debe estar disponible

---

## 2️⃣ INICIAR EL SERVIDOR

### Paso 1: Abrir Terminal en d:\warp_server\minecraft_server

### Paso 2: Ejecutar el panel de admin
```
   run_admin_panel.bat

Para abrir la ventana Java del servidor con logs (la GUI de Minecraft server):

   run_server_window.bat
```

### Paso 3: En el menú que aparece, seleccionar opción 1
```
[1] Start Server
```

### Paso 4: Esperar el mensaje "Done!"
Ejemplo esperado en los logs del panel:
```
✓ Server started successfully
Server is running (PID: XXXX)
```

---

## 3️⃣ CONECTARSE DESDE MINECRAFT

### PARA CONECTAR LOCALMENTE (desde la misma red)
1. Abre Minecraft 1.20.1
2. Click en "Multiplayer"
3. Click en "Add Server" o "Agregar servidor"
4. Ingresa estos datos:

   **Nombre del servidor:** Warp Server
   **IP:** 192.168.100.8
   **Puerto:** 25565
   (o simplemente: 192.168.100.8:25565)

5. Click "Done" / "Hecho"
6. Aparecerá en la lista, haz click para entrar

### PARA CONECTAR VÍA ZEROTIER (desde fuera de la red)
1. Asegúrate de estar en la red Zerotier ZEE-MC
2. Abre Minecraft 1.20.1
3. Click en "Multiplayer"
4. Click en "Add Server"
5. Ingresa estos datos:

   **Nombre del servidor:** Warp Server (VPN)
   **IP:** 10.147.103.80
   **Puerto:** 25565
   (o simplemente: 10.147.103.80:25565)

6. Click "Done"
7. Aparecerá en la lista, haz click para entrar

---

## ⚠️ SI NO PUEDES CONECTARTE

### Verificar que el servidor está corriendo
En el admin_panel.py debería mostrar:
```
Status: ✅ RUNNING
```

### Si ves "❌ STOPPED"
1. Presiona opción 1 para iniciar
2. Espera 10-15 segundos
3. Reintenta conectar

### Si ves conexión rechazada
1. Verifica que usas la IP correcta (192.168.100.8 o 10.147.103.80)
2. Verifica el puerto 25565
3. Asegúrate de estar en Minecraft 1.20.1
4. Reinicia el servidor desde el panel

### Si está lento al conectar
- El servidor necesita 5-10 segundos para estar completamente listo
- Espera a que aparezca el mensaje "Done!" en los logs
- Intenta conectar nuevamente

---

## 📋 IPs DISPONIBLES

### Para conexión LOCAL (misma red):
- IP: 192.168.100.8
- Puerto: 25565
- Úsalo si estás en la misma red que el servidor

### Para conexión VPN (fuera de la red):
- IP: 10.147.103.80
- Puerto: 25565
- Red: Zerotier ZEE-MC (debes estar autorizado)
- Úsalo si accedes desde afuera con Zerotier

---

## 🎮 CONTROLES EN EL JUEGO

**T** = Chat (para hablar con otros jugadores)
**ESC** = Menú de pausa
**/help** = Ver comandos disponibles
**/stop** = Detener servidor (si tienes permisos)

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Cuántos jugadores pueden conectarse?**
R: Hasta 10 jugadores simultáneamente (configurado en server.properties)

**P: ¿Se guardan progreso e inventario?**
R: Sí, automáticamente. El mundo se guarda en d:\warp_server\minecraft_server\servidor_rpg\world\

**P: ¿Se puede agregar mods?**
R: Sí, los jugadores deben tener los MISMOS mods instalados que el servidor

**P: ¿Cómo detener el servidor?**
R: Ejecuta admin_panel.py → opción 2 "Stop Server"

**P: ¿Dónde veo los logs?**
R: En d:\warp_server\minecraft_server\servidor_rpg\server.log

---

Status: ✅ SERVIDOR LISTO
Versión: Minecraft 1.20.1 + Fabric Loader 0.19.2
Actualizado: 01 Mayo 2026
