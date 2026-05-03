# 🌐 GUÍA COMPLETA ZEROTIER PARA AMIGOS

## 📥 PASO 1: INSTALAR ZEROTIER

### Windows:
1. Ir a: https://www.zerotier.com/download/
2. Descargar **ZeroTier One for Windows**
3. Ejecutar el instalador `.msi`
4. Seguir las instrucciones (siguiente, siguiente, instalar)
5. **Reiniciar la PC** (importante)

### Mac:
1. Ir a: https://www.zerotier.com/download/
2. Descargar **ZeroTier One for Macintosh**
3. Abrir el `.pkg` y seguir instrucciones
4. Permitir en Preferencias del Sistema → Seguridad

### Linux (Ubuntu/Debian):
```bash
curl -s https://install.zerotier.com | sudo bash
```

---

## 🔗 PASO 2: UNIRSE A LA RED DEL SERVIDOR

### Después de reiniciar, abrir CMD o PowerShell como Administrador:

**Windows:**
1. Presionar `Win + X`
2. Seleccionar **Windows PowerShell (Administrador)** o **Terminal (Administrador)**
3. Click en **Sí** cuando pregunte por permisos

### Ejecutar comando para unirse a la red:
```powershell
zerotier-cli join 154a350c86a332b5
```

**Debe mostrar:**
```
200 join OK
```

### Verificar que está conectado:
```powershell
zerotier-cli status
```

**Debe mostrar algo como:**
```
200 info 89464430d8 1.16.1 ONLINE
```

### Verificar la IP asignada:
```powershell
zerotier-cli listnetworks
```

**Debe mostrar:**
```
200 listnetworks <nwid> <name> <mac> <status> <type> <dev> <ZT assigned ips>
200 listnetworks 154a350c86a332b5 ZEE-MC xx:xx:xx:xx:xx:xx OK PRIVATE ethernet_xx 10.147.103.xx/24
```

### Verificar en ipconfig:
```powershell
ipconfig | findstr "ZeroTier"
```

**Debe aparecer:**
```
Adaptador de Ethernet ZeroTier One [154a350c86a332b5]:
   Dirección IPv4. . . . . . . . . . . . . . : 10.147.103.xx
```

**Si no aparece, reiniciar la PC.**

---

## 🎮 PASO 3: CONECTARSE AL SERVIDOR MINECRAFT

### 1. Abrir Minecraft 1.20.1 con Fabric Loader 0.19.2 instalado
### 2. Ir a Multiplayer → Add Server
### 3. Ingresar datos:
- **Server Name:** Warp Server
- **Server Address:** `10.147.103.80:25565`

### 4. Click en Done, luego Join Server

---

## ❌ PASO 4: DESINSTALAR / SALIR DE LA RED (Cuando no lo ocupen)

### Opción A: Solo salir de la red (recomendado si van a usar después)
```powershell
zerotier-cli leave 154a350c86a332b5
```

**Resultado:**
```
200 leave OK
```

**Para volver a unirse después:**
```powershell
zerotier-cli join 154a350c86a332b5
```

---

### Opción B: Desinstalar completamente Zerotier

**Windows:**
1. Panel de Control → Programas → Desinstalar programa
2. Buscar **ZeroTier One**
3. Click en Desinstalar
4. Reiniciar PC

**O con PowerShell:**
```powershell
wmic product where name="ZeroTier One" call uninstall
```

**Mac:**
```bash
sudo /Applications/ZeroTier\ One.app/Contents/Resources/uninstall.sh
```

**Linux:**
```bash
sudo apt remove zerotier-one
sudo apt purge zerotier-one
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### "zerotier-cli no se reconoce como comando"
**Solución:** Reiniciar la PC después de instalar

### "200 join OK" pero no aparece IP
**Solución:** Esperar 30 segundos y verificar con:
```powershell
zerotier-cli listnetworks
```
Si dice `ACCESS_DENIED_PRIVATE`, el dueño del servidor debe aprobar la solicitud en el panel web de Zerotier.

### Ping no funciona
**Verificar conexión:**
```powershell
ping 10.147.103.80
```

Si no responde:
1. Verificar que ambos tienen Zerotier ONLINE
2. Verificar que ambos están en la misma red
3. Verificar firewall de Windows

### Minecraft dice "Connection refused"
1. Verificar que el servidor está corriendo
2. Verificar que la IP es correcta: `10.147.103.80:25565`
3. Verificar que tienen Minecraft 1.20.1 con Fabric Loader 0.19.2

---

## 📋 CHECKLIST RÁPIDO

Antes de intentar conectar:
- [ ] Zerotier instalado
- [ ] PC reiniciada después de instalar
- [ ] Unido a red `154a350c86a332b5`
- [ ] Estado muestra `ONLINE`
- [ ] Tiene IP `10.147.103.xx`
- [ ] Ping a `10.147.103.80` funciona
- [ ] Minecraft 1.20.1 + Fabric Loader 0.19.2 instalado
- [ ] Agregado servidor con IP `10.147.103.80:25565`

---

## 💡 NOTAS IMPORTANTES

1. **Zerotier crea una red privada virtual** - es como estar en la misma red local pero por internet
2. **La IP 10.147.103.80** es la IP del servidor dentro de la VPN
3. **Cada persona obtiene una IP diferente** (10.147.103.xx donde xx varía)
4. **No afecta la conexión normal de internet** - solo agrega una red virtual extra
5. **Se puede desactivar sin desinstalar** - solo salir de la red

---

## 🔗 ENLACES ÚTILES

- **Descarga:** https://www.zerotier.com/download/
- **Documentación:** https://docs.zerotier.com/
- **ID de la red:** `154a350c86a332b5`
- **IP del servidor:** `10.147.103.80`

---

**¿Preguntas? Revisar sección de Solución de Problemas arriba.**
