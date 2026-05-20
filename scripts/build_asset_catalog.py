import os
import json
import re

def normalize_niche(name):
    # Remove numbers at the beginning, extensions, and common words to isolate the core niche
    clean = re.sub(r'^\d+[\s\-]*', '', name)
    clean = clean.replace('.zip', '')
    clean = clean.replace('PACK', '').strip()
    clean = clean.lower()
    return clean

def build_catalog(assets_dir, output_file):
    catalog = {}

    templates_dir = os.path.join(assets_dir, "Templates")

    # Dynamically find the pages and PSD dir to avoid encoding issues
    pages_dir_name = None
    psd_dir_name = None
    for item in os.listdir(templates_dir):
        if "P" in item and "GINAS" in item:
            pages_dir_name = item
        if "PSD" in item:
            psd_dir_name = item

    if not pages_dir_name or not psd_dir_name:
        print("Diretórios PÁGINAS ou PSD não encontrados.")
        return

    pages_dir = os.path.join(templates_dir, pages_dir_name)
    psd_dir = os.path.join(templates_dir, psd_dir_name)

    # Mapeando Páginas Premium
    for item in os.listdir(pages_dir):
        if os.path.isdir(os.path.join(pages_dir, item)):
            niche = normalize_niche(item)
            if niche not in catalog:
                catalog[niche] = {}
            catalog[niche]["page"] = os.path.join(pages_dir_name, item)

    # Mapeando PSDs
    for item in os.listdir(psd_dir):
        if item.endswith('.zip'):
            niche = normalize_niche(item)
            # Find the closest matching niche in catalog (or create new)
            matched = False
            for existing_niche in catalog.keys():
                if niche in existing_niche or existing_niche in niche:
                    catalog[existing_niche]["psd"] = os.path.join(psd_dir_name, item)
                    matched = True
                    break

            if not matched:
                if niche not in catalog:
                    catalog[niche] = {}
                catalog[niche]["psd"] = os.path.join(psd_dir_name, item)

    # Typebot fixed path
    catalog["global_automation"] = {
        "typebot": "Templates/+2000 FLUXOS TYPEBOT-20240906T165442Z-001.zip"
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=4, ensure_ascii=False)

    print(f"Catálogo gerado com sucesso em: {output_file}")
    print(f"Total de nichos indexados: {len(catalog)}")

if __name__ == "__main__":
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets_globais")
    workspace_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace")

    os.makedirs(workspace_dir, exist_ok=True)
    output_file = os.path.join(workspace_dir, "asset_catalog.json")

    build_catalog(assets_dir, output_file)
