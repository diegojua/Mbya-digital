"""
Playwright Renderer — Renderiza HTML blueprints hidratados em PNG de alta qualidade.
Suporta feed/carrossel (1080x1080), story (1080x1920) e landing page (1440xfull).
"""
import os
import subprocess
import json


def render_html_to_png(html_path: str, output_path: str,
                       width: int = 1080, height: int = 1080,
                       device_scale: int = 1) -> dict:
    """
    Renderiza um arquivo HTML em PNG usando Playwright via Node.js script.
    Fallback: usa o generate_creatives.js existente no open-design/e2e.
    """
    if not os.path.exists(html_path):
        return {"error": f"HTML não encontrado: {html_path}"}

    # Tentar renderização via script Node.js inline
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    playwright_path = os.path.join(
        root_dir,
        "open-design",
        "node_modules",
        ".pnpm",
        "playwright@1.59.1",
        "node_modules",
        "playwright",
    )
    require_target = playwright_path if os.path.exists(playwright_path) else "playwright"

    node_script = f"""
const {{ chromium }} = require('{require_target}');
(async () => {{
    const browser = await chromium.launch({{ headless: true }});
    const page = await browser.newPage({{
        viewport: {{ width: {width}, height: {height} }},
        deviceScaleFactor: {device_scale}
    }});
    await page.goto('file://{os.path.abspath(html_path)}', {{ waitUntil: 'networkidle' }});
    await page.waitForTimeout(1000);
    await page.screenshot({{ path: '{os.path.abspath(output_path)}', fullPage: false }});
    await browser.close();
    console.log(JSON.stringify({{ status: 'success', path: '{output_path}' }}));
}})();
"""
    script_path = os.path.join(os.path.dirname(output_path), "_render_temp.js")
    try:
        with open(script_path, "w") as f:
            f.write(node_script)

        result = subprocess.run(
            ["node", script_path],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            print(f"📸 Renderizado: {output_path}")
            return {"status": "success", "path": output_path}
        else:
            return {"status": "fallback", "error": result.stderr[:500],
                    "message": "Playwright não disponível. HTML salvo para renderização manual."}
    except FileNotFoundError:
        return {"status": "fallback",
                "message": "Node.js não encontrado. HTML salvo para renderização manual."}
    except subprocess.TimeoutExpired:
        return {"status": "fallback", "message": "Timeout na renderização."}
    except Exception as e:
        return {"status": "fallback", "message": str(e)}
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


def render_batch(html_files: list, output_dir: str,
                 width: int = 1080, height: int = 1080) -> list:
    """Renderiza um batch de HTMLs em PNGs."""
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for html_path in html_files:
        basename = os.path.splitext(os.path.basename(html_path))[0]
        png_path = os.path.join(output_dir, f"{basename}.png")
        result = render_html_to_png(html_path, png_path, width, height)
        result["source_html"] = html_path
        results.append(result)

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        html = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else html.replace(".html", ".png")
        result = render_html_to_png(html, out)
        print(json.dumps(result, indent=2))
