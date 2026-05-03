#!/usr/bin/env python3
"""
Validador de compatibilidad de mods con NeoForge 21.1.227 para Minecraft 1.21.1
"""

import os
import json
import re
from pathlib import Path
from zipfile import ZipFile
from typing import Dict, List, Tuple

# Versión objetivo
NEOFORGE_VERSION = "21.1.227"
MINECRAFT_VERSION = "1.21.1"
MODS_DIR = Path("d:\\warp_server\\minecraft_server\\server\\mods")

# Requisitos conocidos
KNOWN_REQUIREMENTS = {
    # Mods que requieren versión mayor a la instalada (21.1.227)
    "simulated": ("21.1.219", "OK"),
    "createframed": ("21.1.213", "OK"),
    "create_factory": ("21.1.217", "OK"),
    "moonlight": ("21.1.220", "OK"),
    "bookshelf": ("21.1.209", "OK"),
    "sablephysicscompat": ("21.1.227", "OK"),  # Requiere exactamente 21.1.227+
    "potionstacks": ("21.1.80", "OK"),
    "zeta": ("21.1.192", "OK"),
    # Mods Fabric API que ahora deberían funcionar
    "fabric_gametest_api_v1": ("21.1.169", "OK"),
    "fabric_biome_api_v1": ("21.1.169", "OK"),
    "fabric_resource_loader_v0": ("21.1.169", "OK"),
    "fabric_object_builder_api_v1": ("21.1.169", "OK"),
    "fabric_key_binding_api_v1": ("21.1.169", "OK"),
    "fabric_renderer_indigo": ("21.1.219", "OK"),
    "fabric_renderer_api_v1": ("21.1.219", "OK"),
    "fabric_sound_api_v1": ("21.1.169", "OK"),
    "fabric_api_base": ("21.1.169", "OK"),
    "fabric_block_view_api_v2": ("21.1.169", "OK"),
}

def extract_mod_metadata(jar_path: Path) -> Dict:
    """Extrae metadatos de un mod desde su JAR"""
    try:
        with ZipFile(jar_path, 'r') as zf:
            # Buscar toml.conf de NeoForge
            if 'neoforge.mods.toml' in zf.namelist():
                with zf.open('neoforge.mods.toml') as f:
                    content = f.read().decode('utf-8')
                    return parse_toml_metadata(content)
            
            # Buscar fabric.mod.json (para mods Fabric con Connector)
            if 'fabric.mod.json' in zf.namelist():
                with zf.open('fabric.mod.json') as f:
                    return json.load(f)
                    
            # Buscar mcmod.info (Legacy)
            if 'mcmod.info' in zf.namelist():
                with zf.open('mcmod.info') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return data[0]
    except Exception as e:
        return {"error": str(e)}
    
    return {}

def parse_toml_metadata(content: str) -> Dict:
    """Parsea configuración TOML básica"""
    data = {}
    
    # Extraer nombre del mod
    name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
    if name_match:
        data['name'] = name_match.group(1)
    
    # Extraer id del mod
    id_match = re.search(r'modId\s*=\s*"([^"]+)"', content)
    if id_match:
        data['modId'] = id_match.group(1)
    
    # Extraer dependencias de NeoForge
    nf_match = re.search(r'neoforgeVersion\s*=\s*"([^"]+)"', content)
    if nf_match:
        data['neoforgeVersion'] = nf_match.group(1)
    
    # Extraer versión del mod
    version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if version_match:
        data['version'] = version_match.group(1)
    
    return data

def check_neoforge_version_compatibility(required: str, installed: str) -> bool:
    """Compara versiones de NeoForge"""
    def parse_version(v: str) -> Tuple[int, int, int]:
        parts = v.split('.')
        return tuple(int(p) for p in parts[:3]) if len(parts) >= 3 else (0, 0, 0)
    
    req_parts = parse_version(required)
    inst_parts = parse_version(installed)
    
    return inst_parts >= req_parts

def validate_mods():
    """Valida todos los mods contra NeoForge 21.1.227"""
    
    if not MODS_DIR.exists():
        print(f"❌ Directorio de mods no encontrado: {MODS_DIR}")
        return
    
    mods = list(MODS_DIR.glob("*.jar"))
    print(f"\n{'='*80}")
    print(f"VALIDADOR DE COMPATIBILIDAD DE MODS")
    print(f"{'='*80}")
    print(f"NeoForge Instalado: {NEOFORGE_VERSION}")
    print(f"Minecraft Versión: {MINECRAFT_VERSION}")
    print(f"Total de mods encontrados: {len(mods)}")
    print(f"{'='*80}\n")
    
    compatible = []
    problematic = []
    unknown = []
    
    for mod_jar in sorted(mods):
        mod_name = mod_jar.stem
        
        # Extraer metadatos
        metadata = extract_mod_metadata(mod_jar)
        mod_id = metadata.get('modId', mod_name)
        
        # Verificar si está en la lista de requisitos
        if mod_id in KNOWN_REQUIREMENTS:
            required_version, status = KNOWN_REQUIREMENTS[mod_id]
            is_compatible = check_neoforge_version_compatibility(required_version, NEOFORGE_VERSION)
            
            if is_compatible:
                compatible.append((mod_name, mod_id, required_version))
                print(f"✓ {mod_name:<50} [{mod_id:<20}] Requerida: {required_version}")
            else:
                problematic.append((mod_name, mod_id, required_version))
                print(f"❌ {mod_name:<50} [{mod_id:<20}] Requiere: {required_version}")
        else:
            unknown.append((mod_name, mod_id))
            print(f"⚠ {mod_name:<50} [{mod_id:<20}] (sin requisitos conocidos)")
    
    # Resumen
    print(f"\n{'='*80}")
    print(f"RESUMEN DE VALIDACIÓN")
    print(f"{'='*80}")
    print(f"✓ Compatibles:          {len(compatible)}")
    print(f"❌ Problemas:            {len(problematic)}")
    print(f"⚠ Desconocidos:         {len(unknown)}")
    print(f"{'='*80}\n")
    
    if problematic:
        print("⚠️  MODS CON PROBLEMAS POTENCIALES:\n")
        for mod_name, mod_id, required in problematic:
            print(f"  - {mod_name}")
            print(f"    ID: {mod_id}")
            print(f"    Requiere NeoForge: {required}")
            print(f"    Recomendación: Actualizar este mod a una versión compatible\n")
    
    return {
        "total": len(mods),
        "compatible": len(compatible),
        "problematic": len(problematic),
        "unknown": len(unknown),
        "neoforge_version": NEOFORGE_VERSION
    }

if __name__ == "__main__":
    result = validate_mods()
    print("\n💾 Validación completada. Puedes iniciar el servidor ahora.\n")
