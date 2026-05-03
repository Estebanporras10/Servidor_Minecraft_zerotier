#!/usr/bin/env python3
"""Analyzes mod JAR files to identify client-only mods that shouldn't be on the server"""

import os
import zipfile
import json
from pathlib import Path
from collections import defaultdict

# Known client-only mods (based on their purpose)
CLIENT_ONLY_MODS = {
    'jei',  # Just Enough Items (client UI)
    'emi',  # Equivalent Magnifying Glass (client UI)
    'rei',  # Rough Enchanter Info (client UI)
    'jade',  # Jade (client overlay)
    'mouse_tweaks',  # Mouse Tweaks (client input)
    'inventory_tweaks',  # Inventory Tweaks (client UI)
    'neat',  # Neat (client health bars)
    'entityculling',  # Entity Culling (client optimization)
    'sodium',  # Sodium (client rendering)
    'iris',  # Iris (client shaders)
    'optifine',  # OptiFine (client rendering)
    'betterbiomesblend',  # Better Biomes Blend (client rendering)
    'lambdynlights',  # LambDynamicLights (client rendering)
    'lambdabettergrass',  # Lambda Better Grass (client rendering)
    'minecraftcapes',  # Minecraft Capes (client)
    'logicprojector',  # Logic Projector (client)
    'presence_footsteps',  # Presence Footsteps (client audio)
    'entity_texture_features',  # Entity Texture Features (client only)
    'skin_layers_3d',  # 3D Skin Layers (client only)
    'entity_model_features',  # Entity Model Features (client only)
    'nametag_distance',  # Name Tag Distance (client only)
    'appleskin',  # AppleSkin (client UI)
    'itemphysic',  # ItemPhysic (client rendering)
    'waila',  # WAILA (client UI)
    'modonomicon',  # Modonomicon (could be client-only)
    'crafttweaker',  # CraftTweaker (server, but has client components)
    'connector',  # Connector (for mod compat)
}

mods_dir = Path('d:\\warp_server\\minecraft_server\\server\\mods')

if not mods_dir.exists():
    print(f"Mods directory not found: {mods_dir}")
    exit(1)

problematic_mods = []
client_only_mods = []
unknown_mods = []
server_safe_mods = []

print(f"\n📊 Analyzing {len(list(mods_dir.glob('*.jar')))} mods in {mods_dir}...\n")

for mod_file in sorted(mods_dir.glob('*.jar')):
    mod_name = mod_file.stem.lower()
    
    # Check if it's a known client-only mod
    is_client_only = False
    for client_mod in CLIENT_ONLY_MODS:
        if client_mod in mod_name:
            client_only_mods.append(mod_file.name)
            is_client_only = True
            break
    
    if is_client_only:
        continue
    
    # Try to check the mod's metadata
    try:
        with zipfile.ZipFile(mod_file, 'r') as zip_ref:
            # Look for mods.toml or neoforge.mods.toml
            for config_file in ['META-INF/neoforge.mods.toml', 'META-INF/mods.toml']:
                if config_file in zip_ref.namelist():
                    content = zip_ref.read(config_file).decode('utf-8')
                    # Check if it mentions client-only
                    if 'client' in content.lower() and 'only' in content.lower():
                        client_only_mods.append(mod_file.name)
                        is_client_only = True
                    break
            
            if not is_client_only:
                server_safe_mods.append(mod_file.name)
    except Exception as e:
        unknown_mods.append((mod_file.name, str(e)))

print(f"🔴 CLIENT-ONLY MODS ({len(client_only_mods)}):")
for mod in client_only_mods:
    print(f"  - {mod}")

print(f"\n⚠️  UNKNOWN/PROBLEMATIC MODS ({len(unknown_mods)}):")
for mod, error in unknown_mods[:10]:  # Show first 10
    print(f"  - {mod} ({error})")

print(f"\n✅ SERVER-SAFE MODS ({len(server_safe_mods)}):")
for mod in server_safe_mods[:10]:  # Show first 10
    print(f"  - {mod}")
if len(server_safe_mods) > 10:
    print(f"  ... and {len(server_safe_mods) - 10} more")

# Create a list of mods to remove
print(f"\n\n📝 RECOMMENDED ACTIONS:")
print(f"Remove {len(client_only_mods)} client-only mods")
print(f"Keep {len(server_safe_mods)} server-safe mods")

# Save the client-only list to a file
with open('client_only_mods.txt', 'w') as f:
    for mod in client_only_mods:
        f.write(f"{mod}\n")

print(f"\n✓ Client-only mods list saved to: client_only_mods.txt")
