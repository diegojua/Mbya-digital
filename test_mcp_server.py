#!/usr/bin/env python3
"""
Test script para validar MCP Server do JarvisAgency.
Testa importações e disponibilidade de tools.
"""
import sys
import os

def test_mcp_imports():
    """Testa se todos os imports necessários estão disponíveis."""
    print("=" * 60)
    print("🧪 Testando MCP Server — Import Validation")
    print("=" * 60)
    print()

    tests = [
        ("jarvis_agency_os.creative_engine", "generate_creatives"),
        ("jarvis_agency_os.ranker", "rank_creatives"),
        ("jarvis_agency_os.visual_memory", "record_campaign"),
        ("jarvis_agency_os.renderer", "render_html_to_png"),
        ("graphify.engine", "process_briefing"),
        ("xquads.engine", "generate_copy"),
        ("deer_flow.engine", "dispatch_for_approval"),
    ]

    passed = 0
    failed = 0

    for module, func in tests:
        try:
            exec(f"from {module} import {func}")
            print(f"  ✅ {module}.{func}")
            passed += 1
        except ImportError as e:
            print(f"  ❌ {module}.{func} — {str(e)[:60]}")
            failed += 1
        except Exception as e:
            print(f"  ⚠️  {module}.{func} — {type(e).__name__}")
            failed += 1

    print()
    print(f"Result: {passed}/{len(tests)} imports successful")
    print()

    if failed == 0:
        print("✅ All imports OK. MCP server is ready to run.")
        return True
    else:
        print(f"❌ {failed} import(s) failed. Check your environment.")
        return False

def test_mcp_server_start():
    """Testa se o MCP server pode ser instanciado."""
    print("=" * 60)
    print("🚀 Testing MCP Server Instantiation")
    print("=" * 60)
    print()

    try:
        from mcp_agent_agency import mcp
        print("  ✅ MCP server instance created")
        print(f"  ✅ Server name: {mcp.name}")

        # Check tools
        try:
            tools = mcp._tools if hasattr(mcp, '_tools') else {}
            print(f"  ✅ {len(tools)} tools registered")
            for tool_name in tools:
                print(f"     • {tool_name}")
        except Exception as e:
            print(f"  ⚠️  Could not list tools: {e}")

        print()
        print("✅ MCP server is ready!")
        return True
    except Exception as e:
        print(f"  ❌ Failed to instantiate MCP server: {e}")
        print()
        print("❌ MCP server failed to initialize")
        return False

def main():
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, os.getcwd())

    imports_ok = test_mcp_imports()
    print()

    if imports_ok:
        server_ok = test_mcp_server_start()
    else:
        server_ok = False

    print()
    print("=" * 60)
    if imports_ok and server_ok:
        print("🎉 MCP Server Test: PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ MCP Server Test: FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
