"""
Capture screenshots of the redesigned Sentinel UI across viewports.
Run inside the ai-vuln-scanner container; outputs to docs/screenshots/.
"""
import os
import asyncio
from playwright.async_api import async_playwright

OUT_DIR = '/app/docs/screenshots/redesign'
os.makedirs(OUT_DIR, exist_ok=True)

# Routes (we resolve scan_id at runtime for /results)
ROUTES = [
    ('dashboard',     '/'),
    ('scan',          '/scan/new'),
    ('history',       '/history/'),
    ('tasks',         '/tasks/'),
]

VIEWPORTS = [
    ('desktop', 1440, 900),
    ('laptop',  1024, 768),
    ('mobile',  390,  844),
]

BASE = 'http://localhost:5000'


async def main():
    # Resolve a scan_id for the results page.
    import sqlite3
    db_path = '/app/instance/scanner.db'
    scan_id = None
    if os.path.exists(db_path):
        con = sqlite3.connect(db_path)
        row = con.execute(
            "SELECT id FROM scans ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row:
            scan_id = row[0]
        con.close()

    routes = list(ROUTES)
    if scan_id:
        routes.append(('results', f'/results/{scan_id}'))

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=['--no-sandbox'])
        for vp_name, vw, vh in VIEWPORTS:
            ctx = await browser.new_context(viewport={'width': vw, 'height': vh})
            page = await ctx.new_page()
            for slug, path in routes:
                url = BASE + path
                try:
                    await page.goto(url, wait_until='networkidle', timeout=15000)
                    await page.wait_for_timeout(400)
                    out = f'{OUT_DIR}/{slug}__{vp_name}.png'
                    await page.screenshot(path=out, full_page=True)
                    print(f'[OK]  {vp_name:7s}  {path:25s}  -> {out}')
                except Exception as e:
                    print(f'[ERR] {vp_name:7s}  {path:25s}  {e}')
            await ctx.close()
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
