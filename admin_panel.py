from __future__ import annotations

import json
import os
import re
import shlex
import socket
import struct
import subprocess
import sys
import threading
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table


ROOT = Path(__file__).resolve().parent
SERVER_DIR = ROOT / "servidor_rpg"
CONFIG_PATH = ROOT / "panel_config.json"
CONFIG_LOCAL_PATH = ROOT / "panel_config.local.json"
LOG_PATH = SERVER_DIR / "server.log"
EULA_PATH = SERVER_DIR / "eula.txt"
SERVER_PROPERTIES_PATH = SERVER_DIR / "server.properties"
RUN_BAT_PATH = SERVER_DIR / "run.bat"
RUN_SH_PATH = SERVER_DIR / "run.sh"
USER_JVM_ARGS_PATH = SERVER_DIR / "user_jvm_args.txt"
FABRIC_LAUNCHER_JAR_PATH = SERVER_DIR / "fabric-server-launch.jar"
DEFAULT_PORT = 25565
DEFAULT_NETWORK_NAME = ""
DEFAULT_NETWORK_ID = ""

console = Console()


@dataclass
class PanelConfig:
    server_dir: str = str(SERVER_DIR)
    minecraft_version: str = "1.20.1"
    fabric_loader_version: str = "0.19.2"
    java_command: str = "java"
    min_memory: str = "2G"
    max_memory: str = "4G"
    network_name: str = DEFAULT_NETWORK_NAME
    network_id: str = DEFAULT_NETWORK_ID
    port: int = DEFAULT_PORT
    rcon_host: str = "127.0.0.1"
    rcon_port: int = 25575
    rcon_password: str = ""


class RconClient:
    def __init__(self, host: str, port: int, password: str, timeout_seconds: float = 4.0) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.timeout_seconds = timeout_seconds

    def run_command(self, command: str) -> str:
        with socket.create_connection((self.host, self.port), timeout=self.timeout_seconds) as sock:
            sock.settimeout(self.timeout_seconds)

            self._send_packet(sock, request_id=1, packet_type=3, payload=self.password)
            auth_id, _, _ = self._recv_packet(sock)
            if auth_id == -1:
                raise RuntimeError("RCON authentication failed. Check password.")

            self._send_packet(sock, request_id=2, packet_type=2, payload=command)
            response_id, _, response = self._recv_packet(sock)
            if response_id != 2:
                raise RuntimeError("Unexpected RCON response.")

            chunks = [response]
            sock.settimeout(0.2)
            while True:
                try:
                    next_id, _, next_payload = self._recv_packet(sock)
                except socket.timeout:
                    break
                if next_id != 2:
                    break
                chunks.append(next_payload)

        result = "".join(chunks).strip()
        return result or "Command sent successfully (no output returned)."

    @staticmethod
    def _send_packet(sock: socket.socket, request_id: int, packet_type: int, payload: str) -> None:
        payload_bytes = payload.encode("utf-8") + b"\x00\x00"
        packet_length = 8 + len(payload_bytes)
        packet = struct.pack("<iii", packet_length, request_id, packet_type) + payload_bytes
        sock.sendall(packet)

    @staticmethod
    def _recv_exact(sock: socket.socket, size: int) -> bytes:
        data = b""
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                raise RuntimeError("Connection closed while reading RCON response.")
            data += chunk
        return data

    @classmethod
    def _recv_packet(cls, sock: socket.socket) -> tuple[int, int, str]:
        raw_length = cls._recv_exact(sock, 4)
        packet_length = struct.unpack("<i", raw_length)[0]
        if packet_length < 10:
            raise RuntimeError("Invalid RCON packet length received.")

        payload = cls._recv_exact(sock, packet_length)
        request_id, packet_type = struct.unpack("<ii", payload[:8])
        body = payload[8:-2].decode("utf-8", errors="replace")
        return request_id, packet_type, body


class ServerController:
    def __init__(self, server_dir: Path) -> None:
        self.server_dir = server_dir
        self.process: Optional[subprocess.Popen[str]] = None
        self._log_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def is_external_running(self, port: int) -> bool:
        code, output = run_command(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-NetTCPConnection -State Listen -LocalPort "
                    f"{port} -ErrorAction SilentlyContinue | "
                    "Select-Object -First 1 -ExpandProperty OwningProcess"
                ),
            ]
        )
        if code != 0 or not output:
            return False

        try:
            pid = int(output.splitlines()[-1].strip())
        except ValueError:
            return False

        # If this panel started the process, it's internal, not external.
        if self.process is not None and self.is_running() and self.process.pid == pid:
            return False

        proc_code, proc_output = run_command(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-Process -Id {pid} -ErrorAction SilentlyContinue).ProcessName",
            ]
        )
        if proc_code != 0:
            return False

        process_name = proc_output.strip().lower()
        return process_name in {"java", "javaw"}

    def start(self, config: PanelConfig) -> None:
        with self._lock:
            if self.is_running():
                raise RuntimeError("The server is already running.")
            if self.is_external_running(config.port):
                raise RuntimeError(
                    "A Minecraft server is already running outside the panel (Java window)."
                )

            if not RUN_BAT_PATH.exists():
                raise FileNotFoundError(
                    f"{RUN_BAT_PATH} was not found. Run the Fabric server setup first."
                )

            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            log_file = LOG_PATH.open("a", encoding="utf-8", buffering=1)
            try:
                self.process = subprocess.Popen(
                    ["cmd", "/c", str(RUN_BAT_PATH.name)],
                    cwd=str(self.server_dir),
                    stdin=subprocess.PIPE,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
                )
            except Exception:
                log_file.close()
                raise

    def stop(self) -> None:
        with self._lock:
            if not self.is_running():
                raise RuntimeError("The server is not running.")

            assert self.process is not None
            if self.process.stdin:
                try:
                    self.process.stdin.write("stop\n")
                    self.process.stdin.flush()
                except Exception:
                    pass

            try:
                self.process.wait(timeout=25)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=10)
            finally:
                self.process = None

    def restart(self, config: PanelConfig) -> None:
        if self.is_running():
            self.stop()
        elif self.is_external_running(config.port):
            raise RuntimeError(
                "The server is running outside the panel. Stop it from the Java window first."
            )
        self.start(config)

    def send_command(self, command: str) -> None:
        if not self.is_running() or self.process is None or self.process.stdin is None:
            raise RuntimeError(
                "The server is not managed by this panel. Use the Java server window to run commands."
            )
        self.process.stdin.write(command.rstrip() + "\n")
        self.process.stdin.flush()

    def send_command_via_rcon(self, command: str, config: PanelConfig) -> str:
        command_text = command.strip()
        if command_text.startswith("/"):
            command_text = command_text[1:]

        if not command_text:
            raise ValueError("Command cannot be empty.")

        if not is_rcon_enabled_in_server_properties():
            raise RuntimeError(
                "RCON is disabled in server.properties. Use option 11 to configure it, then restart the server."
            )
        if not config.rcon_password:
            raise RuntimeError(
                "RCON password is missing in panel config. Use option 11 to configure it."
            )

        client = RconClient(config.rcon_host, config.rcon_port, config.rcon_password)
        return client.run_command(command_text)

    def status_label(self, port: int) -> str:
        if self.is_running():
            return "running (panel)"
        if self.is_external_running(port):
            return "running (external java window)"
        return "stopped"


def load_config_from_env() -> dict[str, Any]:
    """Load config values from environment variables."""
    data = {}
    env_mapping = {
        "MC_VERSION": "minecraft_version",
        "FABRIC_VERSION": "fabric_loader_version",
        "JAVA_CMD": "java_command",
        "MIN_MEMORY": "min_memory",
        "MAX_MEMORY": "max_memory",
        "NETWORK_NAME": "network_name",
        "NETWORK_ID": "network_id",
        "MC_PORT": "port",
        "RCON_HOST": "rcon_host",
        "RCON_PORT": "rcon_port",
        "RCON_PASSWORD": "rcon_password",
    }
    for env_key, config_key in env_mapping.items():
        value = os.getenv(env_key)
        if value is not None:
            # Convert port to int if needed
            if config_key in ("port", "rcon_port"):
                try:
                    data[config_key] = int(value)
                except ValueError:
                    pass
            else:
                data[config_key] = value
    return data


def load_config() -> PanelConfig:
    """Load config: env vars > local config > default config > defaults."""
    defaults = asdict(PanelConfig())
    
    # Start with environment variables
    data = load_config_from_env()
    
    # Overlay with local config file (if exists)
    if CONFIG_LOCAL_PATH.exists():
        try:
            local_data = json.loads(CONFIG_LOCAL_PATH.read_text(encoding="utf-8"))
            for key, value in local_data.items():
                if key in defaults:
                    data[key] = value
        except json.JSONDecodeError:
            console.print(f"[yellow]Warning: {CONFIG_LOCAL_PATH} has invalid JSON, skipping.[/yellow]")
    
    # Finally overlay with main config file
    if CONFIG_PATH.exists():
        try:
            main_data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            for key, value in main_data.items():
                if key in defaults and key not in data:  # Don't override env/local
                    data[key] = value
        except json.JSONDecodeError:
            console.print(f"[yellow]Warning: {CONFIG_PATH} has invalid JSON, skipping.[/yellow]")
    
    # Merge with defaults and create PanelConfig
    defaults.update(data)
    return PanelConfig(**defaults)


def save_config(config: PanelConfig) -> None:
    CONFIG_PATH.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")


def read_server_properties() -> dict[str, str]:
    if not SERVER_PROPERTIES_PATH.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in SERVER_PROPERTIES_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def update_server_properties(updates: dict[str, str]) -> None:
    lines = []
    if SERVER_PROPERTIES_PATH.exists():
        lines = SERVER_PROPERTIES_PATH.read_text(encoding="utf-8").splitlines()

    found_keys: set[str] = set()
    new_lines: list[str] = []
    for line in lines:
        if line and not line.startswith("#") and "=" in line:
            key, _ = line.split("=", 1)
            trimmed_key = key.strip()
            if trimmed_key in updates:
                new_lines.append(f"{trimmed_key}={updates[trimmed_key]}")
                found_keys.add(trimmed_key)
                continue
        new_lines.append(line)

    for key, value in updates.items():
        if key not in found_keys:
            new_lines.append(f"{key}={value}")

    SERVER_PROPERTIES_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def is_rcon_enabled_in_server_properties() -> bool:
    props = read_server_properties()
    return props.get("enable-rcon", "false").strip().lower() == "true"


def ensure_initial_server_files(config: PanelConfig) -> None:
    SERVER_DIR.mkdir(parents=True, exist_ok=True)
    (SERVER_DIR / "mods").mkdir(parents=True, exist_ok=True)
    if not EULA_PATH.exists():
        EULA_PATH.write_text("eula=true\n", encoding="utf-8")
    if not USER_JVM_ARGS_PATH.exists():
        USER_JVM_ARGS_PATH.write_text(
            "".join(
                [
                    "# Xmx and Xms set the maximum and minimum RAM usage, respectively.\n",
                    "# They can take any number, followed by an M or a G.\n",
                    "# M means Megabyte, G means Gigabyte.\n",
                    "# For example, to set the maximum to 3GB: -Xmx3G\n",
                    "# To set the minimum to 2.5GB: -Xms2500M\n",
                    "\n",
                    f"# Configuración de memoria para el servidor ({config.min_memory} mínimo, {config.max_memory} máximo)\n",
                    f"-Xms{config.min_memory}\n",
                    f"-Xmx{config.max_memory}\n",
                ]
            ),
            encoding="utf-8",
        )
    if not RUN_BAT_PATH.exists():
        RUN_BAT_PATH.write_text(
            "".join(
                [
                    "@echo off\n",
                    "REM Fabric server launcher for Minecraft 1.20.1\n",
                    "java @user_jvm_args.txt -jar fabric-server-launch.jar nogui %*\n",
                    "pause\n",
                ]
            ),
            encoding="utf-8",
        )
    if not RUN_SH_PATH.exists():
        RUN_SH_PATH.write_text(
            "".join(
                [
                    "#!/usr/bin/env sh\n",
                    "# Fabric server launcher for Minecraft 1.20.1\n",
                    "java @user_jvm_args.txt -jar fabric-server-launch.jar nogui \"$@\"\n",
                ]
            ),
            encoding="utf-8",
        )
    if not SERVER_PROPERTIES_PATH.exists():
        SERVER_PROPERTIES_PATH.write_text(
            "".join(
                [
                    f"server-port={config.port}\n",
                    "motd=Warp Server RPG\n",
                    "enable-command-block=true\n",
                    "online-mode=true\n",
                    "allow-flight=true\n",
                    "view-distance=10\n",
                    "simulation-distance=8\n",
                    "max-players=10\n",
                    "enable-rcon=false\n",
                ]
            ),
            encoding="utf-8",
        )


def get_local_ips() -> list[str]:
    ips: set[str] = set()
    try:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.254.*' -and $_.IPAddress -ne '127.0.0.1' -and $_.InterfaceAlias -notmatch 'ZeroTier|Loopback|vEthernet|WSL|VirtualBox|Hyper-V|Bluetooth|Radmin' } | Select-Object -ExpandProperty IPAddress",
            ],
            capture_output=True,
            text=True,
            shell=False,
        )
        if completed.returncode == 0:
            for line in completed.stdout.splitlines():
                ip = line.strip()
                if ip:
                    ips.add(ip)
    except OSError:
        pass

    if not ips:
        try:
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM):
                ip = info[4][0]
                if not ip.startswith("127."):
                    ips.add(ip)
        except OSError:
            pass

    ips.add("127.0.0.1")
    return sorted(ips)


def run_command(args: list[str], cwd: Optional[Path] = None) -> tuple[int, str]:
    completed = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        shell=False,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output.strip()


def zerotier_cli_exists() -> bool:
    return get_zerotier_cli_path() is not None


def shutil_which(name: str) -> Optional[str]:
    from shutil import which

    return which(name)


def get_zerotier_cli_path() -> Optional[Path]:
    command = shutil_which("zerotier-cli")
    if command:
        return Path(command)

    windows_fallback = Path(r"C:\Program Files (x86)\ZeroTier\One\zerotier-cli.bat")
    if windows_fallback.exists():
        return windows_fallback

    return None


def run_zerotier_command(*args: str) -> tuple[int, str]:
    cli_path = get_zerotier_cli_path()
    if cli_path is None:
        return 1, "zerotier-cli not found"

    if cli_path.suffix.lower() in {".bat", ".cmd"}:
        command = ["cmd", "/c", str(cli_path), *args]
    else:
        command = [str(cli_path), *args]
    return run_command(command)


def get_zerotier_status() -> dict[str, Any]:
    if get_zerotier_cli_path() is None:
        return {"available": False, "status": "zerotier-cli not found", "networks": []}

    code, text = run_zerotier_command("-j", "listnetworks")
    networks: list[dict[str, Any]] = []
    if code == 0 and text:
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                networks = parsed
        except json.JSONDecodeError:
            pass

    if not networks:
        code, text = run_zerotier_command("listnetworks")
        networks = _parse_zerotier_text(text)

    status_code, status_text = run_zerotier_command("status")
    return {
        "available": True,
        "status": status_text if status_code == 0 and status_text else "Unable to read Zerotier status",
        "networks": networks,
    }


def _parse_zerotier_text(text: str) -> list[dict[str, Any]]:
    networks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"[0-9a-fA-F]{16}", line.split()[0]):
            if current:
                networks.append(current)
            parts = line.split()
            current = {"id": parts[0], "line": line, "assignedAddresses": []}
            continue
        if current is not None:
            current.setdefault("line", "")
            current["line"] = f"{current['line']} {line}".strip()
            addresses = re.findall(r"(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?|[0-9a-fA-F:]+/\d{1,3}", line)
            if addresses:
                current.setdefault("assignedAddresses", [])
                current["assignedAddresses"].extend(addresses)
    if current:
        networks.append(current)
    return networks


def get_zerotier_ips(status: dict[str, Any]) -> list[str]:
    ips: set[str] = set()
    for network in status.get("networks", []):
        for address in network.get("assignedAddresses", []) or []:
            ip = address.split("/")[0]
            if ip:
                ips.add(ip)
    return sorted(ips)


def display_status(config: PanelConfig, controller: ServerController) -> None:
    status = get_zerotier_status()
    vpn_ip_list = get_zerotier_ips(status)
    local_ips = ", ".join(ip for ip in get_local_ips() if ip not in vpn_ip_list)
    vpn_ips = ", ".join(vpn_ip_list) or "No VPN IP detected"
    server_state = controller.status_label(config.port)

    table = Table(title="Minecraft Server Status", show_lines=True)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Server directory", str(config.server_dir))
    table.add_row("Minecraft version", config.minecraft_version)
    table.add_row("Fabric loader version", config.fabric_loader_version)
    table.add_row("Server state", server_state)
    table.add_row("Local IPs", local_ips)
    table.add_row("VPN IPs", vpn_ips)
    table.add_row("Zerotier", status["status"])
    table.add_row("Network ID", config.network_id or "Not configured")
    table.add_row("Port", str(config.port))
    table.add_row(
        "RCON",
        f"{config.rcon_host}:{config.rcon_port} ({'enabled' if is_rcon_enabled_in_server_properties() else 'disabled'})",
    )
    console.print(table)


def show_connection_instructions(config: PanelConfig, controller: ServerController) -> None:
    status = get_zerotier_status()
    vpn_ips = get_zerotier_ips(status)
    local_ips = [ip for ip in get_local_ips() if ip not in vpn_ips]

    local_text = "\n".join(f"- {ip}:{config.port}" for ip in local_ips)
    vpn_text = "\n".join(f"- {ip}:{config.port}" for ip in vpn_ips) if vpn_ips else "- No VPN IP detected yet"

    console.print(
        Panel(
            f"Local connection:\n{local_text}\n\nZerotier connection:\n{vpn_text}\n\nServer folder: {SERVER_DIR}",
            title="Connection Instructions",
            border_style="green",
        )
    )


def open_config_location() -> None:
    if not SERVER_DIR.exists():
        SERVER_DIR.mkdir(parents=True, exist_ok=True)
    os.startfile(str(SERVER_DIR))


def open_file_in_editor(path: Path) -> None:
    if path.exists():
        os.startfile(str(path))
    else:
        console.print(f"[yellow]File not found:[/yellow] {path}")


def join_zerotier_network(config: PanelConfig) -> None:
    if not zerotier_cli_exists():
        raise RuntimeError("zerotier-cli is not installed or not available.")

    network_id = Prompt.ask("Zerotier network ID", default=config.network_id or "")
    if not network_id:
        raise ValueError("Network ID is required.")

    code, output = run_zerotier_command("join", network_id)
    if code != 0:
        raise RuntimeError(output or "Unable to join Zerotier network.")

    config.network_id = network_id
    save_config(config)


def leave_zerotier_network(config: PanelConfig) -> None:
    if not zerotier_cli_exists():
        raise RuntimeError("zerotier-cli is not installed or not available.")

    network_id = Prompt.ask("Zerotier network ID", default=config.network_id or "")
    if not network_id:
        raise ValueError("Network ID is required.")

    code, output = run_zerotier_command("leave", network_id)
    if code != 0:
        raise RuntimeError(output or "Unable to leave Zerotier network.")


def prompt_server_command(controller: ServerController, config: PanelConfig) -> None:
    command = Prompt.ask("Minecraft command", default="list")
    command_text = command.strip()
    if command_text.startswith("/"):
        command_text = command_text[1:]

    if controller.is_running():
        controller.send_command(command_text)
        console.print("[green]Command sent to server process managed by panel.[/green]")
        return

    if controller.is_external_running(config.port):
        response = controller.send_command_via_rcon(command_text, config)
        console.print(Panel(response, title="RCON Response", border_style="green"))
        return

    raise RuntimeError("Server is not running.")


def setup_rcon(config: PanelConfig, controller: ServerController) -> None:
    server_running = controller.is_running() or controller.is_external_running(config.port)
    if server_running:
        console.print(
            "[yellow]Server is running. RCON settings will be saved now and applied after restart.[/yellow]"
        )

    password = Prompt.ask("RCON password (required)", password=True, default=config.rcon_password or "")
    if not password:
        raise ValueError("RCON password is required.")

    host = Prompt.ask("RCON host", default=config.rcon_host)
    port_text = Prompt.ask("RCON port", default=str(config.rcon_port))
    try:
        port_value = int(port_text)
    except ValueError as exc:
        raise ValueError("RCON port must be a valid number.") from exc

    config.rcon_host = host.strip() or "127.0.0.1"
    config.rcon_port = port_value
    config.rcon_password = password
    save_config(config)

    update_server_properties(
        {
            "enable-rcon": "true",
            "rcon.password": password,
            "rcon.port": str(port_value),
            "broadcast-rcon-to-ops": "true",
        }
    )

    if server_running:
        console.print(
            "[green]RCON configured. Restart the server once from the Java window to activate it.[/green]"
        )
    else:
        console.print("[green]RCON configured. Start or restart the server for changes to take effect.[/green]")


def maybe_bootstrap_server(config: PanelConfig) -> None:
    if not RUN_BAT_PATH.exists() and FABRIC_LAUNCHER_JAR_PATH.exists():
        console.print("[yellow]run.bat not found yet. The Fabric server launcher is ready to use.[/yellow]")


def main() -> None:
    config = load_config()
    save_config(config)
    ensure_initial_server_files(config)
    controller = ServerController(SERVER_DIR)

    console.print(
        Panel(
            f"Minecraft server panel\nVersion: {config.minecraft_version}\nFabric loader: {config.fabric_loader_version}\nServer dir: {SERVER_DIR}",
            title="Warp Server",
            border_style="blue",
        )
    )

    while True:
        display_status(config, controller)
        console.print(
            "\n".join(
                [
                    "[1] Start server",
                    "[2] Stop server",
                    "[3] Restart server",
                    "[4] Join Zerotier network",
                    "[5] Leave Zerotier network",
                    "[6] Open config folder",
                    "[7] Open server.properties",
                    "[8] Refresh status",
                    "[9] Send command to server",
                    "[10] Show connection instructions",
                    "[11] Setup RCON for external control",
                    "[0] Exit",
                ]
            )
        )

        choice = Prompt.ask("Choose an option", default="8")
        try:
            if choice == "1":
                controller.start(config)
                console.print("[green]Server started.[/green]")
            elif choice == "2":
                if controller.is_running():
                    controller.stop()
                    console.print("[green]Server stopped.[/green]")
                elif controller.is_external_running(config.port):
                    console.print(
                        "[yellow]Server is running in an external Java window. Stop it there.[/yellow]"
                    )
                else:
                    console.print("[yellow]Server is already stopped.[/yellow]")
            elif choice == "3":
                controller.restart(config)
                console.print("[green]Server restarted.[/green]")
            elif choice == "4":
                join_zerotier_network(config)
                console.print("[green]Joined Zerotier network.[/green]")
            elif choice == "5":
                leave_zerotier_network(config)
                console.print("[green]Left Zerotier network.[/green]")
            elif choice == "6":
                open_config_location()
            elif choice == "7":
                open_file_in_editor(SERVER_PROPERTIES_PATH)
            elif choice == "8":
                continue
            elif choice == "9":
                prompt_server_command(controller, config)
            elif choice == "10":
                show_connection_instructions(config, controller)
            elif choice == "11":
                setup_rcon(config, controller)
            elif choice == "0":
                if controller.is_running() and Confirm.ask("Server is running. Stop it before exiting?", default=True):
                    controller.stop()
                break
            else:
                console.print("[red]Invalid option.[/red]")
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")

        console.print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
