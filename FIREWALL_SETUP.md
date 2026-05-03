# 🔥 CONFIGURACIÓN DE FIREWALL PARA MINECRAFT SERVER

## ❌ PROBLEMA IDENTIFICADO

Tus amigos no pueden conectarse porque el **firewall de Windows está bloqueando el puerto 25565**. El servidor está corriendo correctamente pero el firewall no permite conexiones entrantes.

## ✅ SOLUCIÓN - EJECUTAR COMO ADMINISTRADOR

Abre PowerShell **como Administrador** y ejecuta estos comandos:

### 1. Abrir PowerShell como Administrador
- Click derecho en el menú Inicio
- Seleccionar "Windows PowerShell (Administrador)"
- Click "Sí" en el UAC

### 2. Ejecutar comandos para abrir firewall
```powershell
# Permitir tráfico TCP ( Minecraft usa TCP para conexiones )
netsh advfirewall firewall add rule name="Minecraft Server TCP" dir=in action=allow protocol=TCP localport=25565

# Permitir tráfico UDP ( para query/status )
netsh advfirewall firewall add rule name="Minecraft Server UDP" dir=in action=allow protocol=UDP localport=25565

# Verificar que las reglas se agregaron
netsh advfirewall firewall show rule name="Minecraft Server TCP"
netsh advfirewall firewall show rule name="Minecraft Server UDP"
```

### 3. Verificar que el servidor está escuchando
```powershell
netstat -an | findstr :25565
```

Deberías ver algo como:
```
TCP    0.0.0.0:25565          0.0.0.0:0              LISTENING
```

## 🌐 CONFIGURACIÓN ZEROTIER (ESTÁ CORRECTA)

Tu configuración de Zerotier está perfecta:
- **Estado**: ONLINE ✅
- **Red**: ZEE-MC (154a350c86a332b5) ✅
- **IP del servidor**: 10.147.103.80 ✅
- **Ping**: Funcionando ✅

## 🎮 INSTRUCCIONES PARA TUS AMIGOS

### Requisitos para tus amigos:
1. **Instalar Zerotier**: https://www.zerotier.com/download/
2. **Unirse a la red**: `zerotier-cli join 154a350c86a332b5`
3. **Minecraft 1.20.1 con Fabric Loader 0.19.2** instalado
4. **Agregar servidor** en Minecraft:
   - **Nombre**: Warp Server
   - **IP**: 10.147.103.80
   - **Puerto**: 25565

### Conexión Local (si están en tu red):
- **IP**: 192.168.100.8:25565

## 📋 VERIFICACIÓN POST-CONFIGURACIÓN

Después de configurar el firewall:

1. **Reinicia el servidor Minecraft**
2. **Pide a un amigo que intente conectarse**
3. **Si aún no funciona**, verifica:
   - Que tu amigo esté en la red Zerotier
   - Que tu amigo tenga la misma versión (1.20.1 + Fabric Loader 0.19.2)
   - Que el servidor esté mostrando "Done!" en los logs

## 🚨 SI SIGUE SIN FUNCIONAR

### Opciones adicionales:
1. **Desactivar temporalmente el firewall** para probar:
   ```powershell
   netsh advfirewall set allprofiles state off
   # Si funciona, volver a activar:
   netsh advfirewall set allprofiles state on
   ```

2. **Verificar router** (si conexión local):
   - Revisa que el router tenga **port forwarding** del puerto 25565
   - O usa **DMZ** temporalmente para probar

3. **Revisar antivirus**:
   - Algunos antivirus también bloquean puertos
   - Agrega excepción para Java/Minecraft

## ✅ ESTADO ACTUAL

- **Servidor**: ✅ Corriendo correctamente
- **RAM**: ✅ Configurada a 6G-8G 
- **Zerotier**: ✅ Configurado y funcionando
- **Firewall**: ❌ Bloqueando conexiones (requiere admin)
- **Puerto**: 25565 escuchando en TCP/UDP

---
**Nota**: Después de configurar el firewall, tus amigos deberían poder conectarse sin problemas.
