# Oracle Cloud VM Setup - Paso a Paso Final

Estás listo para crear la VM en Oracle Cloud Always Free con tu servidor Minecraft RPG. Aquí está todo lo que necesitas hacer.

## Resumen de configuración

- **Repositorio**: `https://github.com/Estebanporras10/Servidor_Minecraft_zerotier.git`
- **Rama**: `main`
- **ZeroTier Network ID**: `154a350c86a332b5`
- **Memoria**: MIN=12G, MAX=16G (fallback: MIN=8G, MAX=12G)
- **SSH Key**: Generada en `~/.ssh/oracle_mc_server` (privada) y `oracle_mc_server.pub` (pública)

---

## 1. Tu clave SSH pública (copiar y guardar)

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJGgNCM1GeDD1SSYPw6vKPFS03q2u1gCfwf/VrLPIm2X minecraft@oracle-cloud
```

**Guárdala en un archivo de texto seguro** — la vas a pegar en Oracle Cloud.

Tu clave privada está en: `C:\Users\porra\.ssh\oracle_mc_server` (NO la compartas).

---

## 2. Crear la VM en Oracle Cloud

### Opción A: Console Web (recomendada - visual)

1. Abre Oracle Cloud Console → **Compute** → **Instances**
2. Click en **Create instance**
3. Configura así:

   **Image and shape:**
   - Image: **Canonical Ubuntu 22.04 LTS** (o Ubuntu 24.04)
   - Shape: **Ampere (ARM)** → **Ampere Compute 1** (A1.Flex o A1.Compute)
   - OCPU: **4** (máximo recomendado en Always Free)
   - Memory: **24 GB** (si disponible; fallback a 12GB o 8GB)

   **Networking:**
   - VCN: Create new o usa existente
   - Subnet: Create new o selecciona existente
   - Assign public IP: **Yes**

   **Add SSH keys:**
   - Selecciona **Paste SSH key**
   - Pega la clave pública de arriba (el contenido completo)

   **Advanced Options:**
   - Click en **Show Advanced Options**
   - Scroll hasta **Initialization script**
   - Pega el contenido de `cloud-init-oracle.yaml` (sin modificaciones, ya está personalizado)

4. Click en **Create** — la VM se provisiona automáticamente

### Opción B: OCI CLI (línea de comandos)

Si tienes `oci` CLI instalado:

```bash
oci compute instance launch \
  --compartment-id <tu_compartment_ocid> \
  --availability-domain <tu_ad> \
  --image-id <ubuntu_image_ocid> \
  --shape "Ampere.A1.Flex" \
  --shape-config '{"memoryInGBs": 24, "ocpus": 4}' \
  --subnet-id <tu_subnet_ocid> \
  --ssh-authorized-keys-file /path/to/oracle_mc_server.pub \
  --user-data file://cloud-init-oracle.yaml \
  --display-name "minecraft-rpg-server"
```

Reemplaza:
- `<tu_compartment_ocid>`: ID de tu compartimiento
- `<tu_ad>`: Tu availability domain (ej: `tBmgY:US-ASHBURN-AD-1`)
- `<ubuntu_image_ocid>`: OCID de la imagen Ubuntu
- `<tu_subnet_ocid>`: ID de tu subnet

---

## 3. Esperar provisión + Obtener IP pública

- La creación toma ~2-3 minutos
- Una vez creada, ve a **Instance Details**
- Copia la **IP pública**

---

## 4. Conectarte por SSH

En PowerShell o Terminal:

```bash
ssh -i C:\Users\porra\.ssh\oracle_mc_server ubuntu@<IP_PUBLICA>
```

Reemplaza `<IP_PUBLICA>` con la IP de tu VM (ej: `129.154.50.100`).

**Primer acceso (primera vez):**
- Acepta el fingerprint: `Are you sure you want to continue connecting (yes/no)?` → `yes`

---

## 5. Verificar que todo está funcionando

Una vez dentro de la VM:

```bash
# Ver estado del servidor Minecraft
sudo systemctl status minecraft.service

# Ver logs en tiempo real
sudo journalctl -u minecraft.service -f

# Listar procesos Java
ps aux | grep java

# Ver ZeroTier status
sudo zerotier-cli status
```

---

## 6. Autorizar nodo en ZeroTier (importante)

La VM se ha unido automáticamente a tu red ZeroTier, pero necesitas autorizarla:

1. Abre **ZeroTier Central** → Tu red `154a350c86a332b5`
2. En la lista de miembros, busca el nodo nuevo (sin autorizar)
3. Haz click en el **checkbox** para autorizarlo
4. Espera ~30 segundos, luego revisa la IP asignada:

   En la VM:
   ```bash
   sudo zerotier-cli listnetworks
   ```

   Deberías ver tu IP ZeroTier (ej: `10.147.103.XX`)

---

## 7. Conectar jugadores

### Localmente (misma red local - si la VM está en tu LAN):

```
Dirección: <IP_PRIVADA_VM>:25565
```

### Vía ZeroTier (recomendado para amigos remotos):

1. Tus amigos deben estar en tu red ZeroTier `154a350c86a332b5`
2. Autorizados en ZeroTier Central
3. Luego conectan con:

   ```
   Dirección: <IP_ZEROTIER_VM>:25565
   ```

   (La IP que obtuviste en el paso 6)

---

## 8. Ajustes posteriores (si necesario)

### Cambiar memoria después

Si quieres cambiar MIN/MAX memory:

```bash
sudo nano /etc/systemd/system/minecraft.service

# Busca las líneas:
# Environment=MIN_MEMORY=12G
# Environment=MAX_MEMORY=16G

# Edita los valores, guarda (Ctrl+O, Enter, Ctrl+X)

sudo systemctl daemon-reload
sudo systemctl restart minecraft.service
```

### Abrir puertos en firewall de Oracle (si usas IP pública)

En Oracle Cloud Console:

1. Ve a **Virtual Cloud Networks** → Tu VCN
2. **Security Lists** → Selecciona tu security list
3. Click en **Add Ingress Rules**
4. Agrega:
   - Source: `0.0.0.0/0`
   - Protocol: TCP
   - Destination Port: `25565`

### SSH directo a usuario minecraft (opcional)

```bash
sudo su - minecraft
cd /opt/minecraft_server/servidor_rpg
./run.sh
```

---

## 9. Monitoreo 24/7

El servicio systemd está habilitado y se reinicia automáticamente si falla.

Para ver logs históricos:

```bash
# Últimos 500 líneas
sudo journalctl -u minecraft.service -n 500 --no-pager

# Filtrar por hora
sudo journalctl -u minecraft.service --since "2 hours ago"
```

---

## 10. Backup del mundo

El mundo está en `/opt/minecraft_server/servidor_rpg/world/`. Para backups regulares, crea un cron job:

```bash
sudo crontab -e

# Agrega (ejemplo: diario a las 3 AM):
0 3 * * * tar -czf /backups/minecraft_world_$(date +\%Y\%m\%d).tar.gz /opt/minecraft_server/servidor_rpg/world/
```

---

## Solución de problemas

### "Permission denied" al conectar SSH
→ Verifica que usas la clave privada correcta:
```bash
ssh -i C:\Users\porra\.ssh\oracle_mc_server ubuntu@<IP>
```

### Server no está corriendo
```bash
sudo systemctl restart minecraft.service
sudo journalctl -u minecraft.service -f  # Ver errores en tiempo real
```

### ZeroTier IP no asignada
→ Autoriza el nodo en ZeroTier Central y espera 1-2 minutos.

### No puedo conectar desde Minecraft
1. Verifica que usas la IP correcta (local, ZeroTier, o pública)
2. Verifica puerto 25565 abierto: `sudo ss -tuln | grep 25565`
3. Revisa logs del servidor: `sudo journalctl -u minecraft.service -f`

---

## Próximos pasos opcionales

- **Crear systemd timer** para backups automáticos
- **Configurar RCON** desde tu panel admin en Windows
- **Monitoreo avanzado**: instalar Prometheus/Grafana en la VM
- **DNS dinámico**: si tu IP ZeroTier cambia, configura un registro DNS

---

¡Tu servidor Minecraft RPG debería estar en línea en menos de 5 minutos! 🎮🚀
