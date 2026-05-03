# Minecraft Server and Zerotier Panel

This workspace contains a Minecraft server panel for Fabric 1.20.1 and a server directory prepared for local and VPN play.

## Files

- `admin_panel.py`: Rich-based admin panel for starting, stopping, restarting, sending commands, showing IPs, and managing Zerotier.
- `run_admin_panel.bat`: launcher that always starts the panel from the project root.
- `requirements.txt`: Python dependency list.
- `servidor_rpg/`: Fabric server runtime folder for the new server.
- `servidor_create/`: backup copy of the previous server.
- `panel_config.example.json`: Example configuration template (safe to commit).
- `.gitignore`: Excludes sensitive files and large assets from version control.

## Setup

1. Install Python dependencies:

   ```powershell
   py -3 -m pip install -r requirements.txt
   ```

2. **Configure your server** (sensitive credentials):
   - Copy `panel_config.example.json` to `panel_config.local.json`
   - Edit `panel_config.local.json` with your actual values:
     - `rcon_password`: Strong password for server commands
     - `network_id`: Your Zerotier network ID (if using ZeroTier)
     - `min_memory`, `max_memory`: Adjust for your system
   - **Do NOT commit** `panel_config.local.json` — it's in `.gitignore`

3. Alternatively, set environment variables (for cloud deployments):
   ```powershell
   $env:RCON_PASSWORD = "your_strong_password"
   $env:NETWORK_ID = "your_zerotier_id"
   $env:MAX_MEMORY = "8G"
   ```
   See `load_config_from_env()` in `admin_panel.py` for all supported env vars.

4. `servidor_rpg/` is already prepared as a Fabric 1.20.1 server.
5. Add your Fabric mods to `servidor_rpg/mods/`.
6. Make sure `eula.txt` has `eula=true`.
7. Start the panel:

   ```powershell
   run_admin_panel.bat
   ```

## Configuration Priority

The panel reads configuration in this order (first found wins):

1. **Environment variables** (e.g., `RCON_PASSWORD`, `NETWORK_ID`)
2. **Local config file** (`panel_config.local.json`)
3. **Main config file** (`panel_config.json`)
4. **Built-in defaults** (fallback values)

This allows you to keep secrets out of version control while supporting secure cloud deployments.

## Security

- **Never commit** `panel_config.json` or `panel_config.local.json` with real passwords/IDs
- Use `panel_config.example.json` as a template
- For shared repositories, set secrets via GitHub Secrets or cloud provider vaults
- Rotate `rcon_password` if it's ever exposed
- Keep the repository private if possible

## Zerotier

The panel can join or leave a Zerotier network once the CLI is installed and a network ID is configured in your local config or environment.

