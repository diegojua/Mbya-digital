#!/usr/bin/env python3
"""
Schema Validator para arquivos de configuração do JarvisAgency OS.
Valida design_states.json, constraints.json, creative_ranker.json e design_intelligence.json.
Uso: python3 validate_configs.py
"""
import json
import os
import sys
from pathlib import Path

CONFIG_DIR = Path(__file__).parent / "jarvis_agency_os" / "config"

def validate_design_states():
    """Valida design_states.json."""
    path = CONFIG_DIR / "design_states.json"
    print(f"🔍 Validando {path.name}...")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "states" in data, "Falta campo 'states'"
        assert "fallback_state" in data, "Falta campo 'fallback_state'"

        required_state_fields = {
            "description", "bg_primary", "bg_card", "text_primary",
            "text_muted", "accent", "accent_glow", "border_color",
            "tone", "font_headline", "font_editorial", "cta_style",
            "image_overlay", "niches"
        }

        for state_name, state_data in data["states"].items():
            missing = required_state_fields - set(state_data.keys())
            assert not missing, f"Estado '{state_name}' falta campos: {missing}"
            assert isinstance(state_data["niches"], list), \
                f"Estado '{state_name}' - 'niches' deve ser array"

        print(f"  ✅ {len(data['states'])} estados válidos")
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def validate_constraints():
    """Valida constraints.json."""
    path = CONFIG_DIR / "constraints.json"
    print(f"🔍 Validando {path.name}...")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "forbidden_patterns" in data, "Falta campo 'forbidden_patterns'"
        assert "mandatory_rules" in data, "Falta campo 'mandatory_rules'"
        assert "quality_gates" in data, "Falta campo 'quality_gates'"

        assert isinstance(data["forbidden_patterns"], list), \
            "'forbidden_patterns' deve ser array"
        assert isinstance(data["mandatory_rules"], dict), \
            "'mandatory_rules' deve ser objeto"

        mandatory_sections = {"typography", "layout", "content"}
        missing = mandatory_sections - set(data["mandatory_rules"].keys())
        assert not missing, f"mandatory_rules falta seções: {missing}"

        print(f"  ✅ {len(data['forbidden_patterns'])} padrões proibidos definidos")
        print(f"  ✅ Regras obrigatórias: {', '.join(data['mandatory_rules'].keys())}")
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def validate_creative_ranker():
    """Valida creative_ranker.json."""
    path = CONFIG_DIR / "creative_ranker.json"
    print(f"🔍 Validando {path.name}...")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "dimensions" in data, "Falta campo 'dimensions'"
        assert "scoring" in data, "Falta campo 'scoring'"

        total_weight = sum(d.get("weight", 0) for d in data["dimensions"].values())
        assert 0.99 <= total_weight <= 1.01, \
            f"Pesos das dimensões devem somar 1.0 (atual: {total_weight})"

        for dim_name, dim_data in data["dimensions"].items():
            assert "weight" in dim_data, f"Dimensão '{dim_name}' falta 'weight'"
            assert "description" in dim_data, f"Dimensão '{dim_name}' falta 'description'"
            assert "checks" in dim_data, f"Dimensão '{dim_name}' falta 'checks'"
            assert isinstance(dim_data["checks"], list), \
                f"Dimensão '{dim_name}' - 'checks' deve ser array"

        print(f"  ✅ {len(data['dimensions'])} dimensões de scoring")
        print(f"  ✅ Pesos normalizados (total: {total_weight:.2f})")
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def validate_design_intelligence():
    """Valida design_intelligence.json."""
    path = CONFIG_DIR / "design_intelligence.json"
    print(f"🔍 Validando {path.name}...")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "default_profile" in data, "Falta campo 'default_profile'"
        assert "profiles" in data, "Falta campo 'profiles'"
        assert data["default_profile"] in data["profiles"], \
            "default_profile deve existir em profiles"

        required_profile_fields = {
            "description", "match", "style_keywords", "layout_rules",
            "icon_rules", "anti_patterns", "quality_gates"
        }

        for profile_name, profile in data["profiles"].items():
            missing = required_profile_fields - set(profile.keys())
            assert not missing, f"Perfil '{profile_name}' falta campos: {missing}"
            assert isinstance(profile["match"], list), \
                f"Perfil '{profile_name}' - 'match' deve ser array"
            assert isinstance(profile["quality_gates"], dict), \
                f"Perfil '{profile_name}' - 'quality_gates' deve ser objeto"

        print(f"  ✅ {len(data['profiles'])} perfis de design intelligence válidos")
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def main():
    print("=" * 60)
    print("🔐 JarvisAgency OS — Config Schema Validator")
    print("=" * 60)
    print()

    results = {
        "design_states.json": validate_design_states(),
        "constraints.json": validate_constraints(),
        "creative_ranker.json": validate_creative_ranker(),
        "design_intelligence.json": validate_design_intelligence(),
    }

    print()
    print("=" * 60)
    passed = sum(results.values())
    total = len(results)

    if passed == total:
        print(f"✅ TODOS OS CONFIGS VÁLIDOS ({passed}/{total})")
        print("=" * 60)
        return 0
    else:
        print(f"❌ ERROS ENCONTRADOS ({total - passed} falhas)")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
