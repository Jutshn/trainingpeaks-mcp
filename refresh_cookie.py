"""
Loggt sich headless bei TrainingPeaks ein und schreibt den Wert des
Production_tpAuth-Cookies in eine Datei.

WICHTIG: Die exakten Feld-Selektoren der TrainingPeaks-Login-Seite wurden
NICHT live getestet (kein Netzwerkzugriff im Erstellungs-Kontext). Bitte
beim ersten Lauf lokal mit `headless=False` gegenprüfen und ggf. anpassen,
siehe TESTEN weiter unten.
"""

import argparse
import os
import sys

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://home.trainingpeaks.com/login"
COOKIE_NAME = "Production_tpAuth"
COOKIE_DOMAIN_HINT = "trainingpeaks.com"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Datei, in die der Cookie-Wert geschrieben wird")
    parser.add_argument(
        "--headless",
        action="store_true",
        default=os.environ.get("CI", "").lower() == "true",
        help="Headless-Modus (Standard: an, wenn CI=true gesetzt ist)",
    )
    args = parser.parse_args()

    username = os.environ["TP_USERNAME"]
    password = os.environ["TP_PASSWORD"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL, wait_until="networkidle")

        # --- Login-Formular ---
        # Diese Selektoren sind ein plausibler Startpunkt, aber ungetestet.
        # Beim ersten lokalen Testlauf (--headless weglassen) prüfen und anpassen.
        page.fill("input[name='Username'], input#username, input[type='email']", username)
        page.fill("input[name='Password'], input#password, input[type='password']", password)
        page.click("button[type='submit']")

        # Warten, bis der Login durch ist (Redirect auf app.trainingpeaks.com o.ä.)
        page.wait_for_load_state("networkidle", timeout=30000)

        cookies = context.cookies()
        target = next(
            (c for c in cookies if c["name"] == COOKIE_NAME and COOKIE_DOMAIN_HINT in c["domain"]),
            None,
        )

        browser.close()

        if not target:
            print(
                f"FEHLER: Cookie '{COOKIE_NAME}' wurde nach dem Login nicht gefunden. "
                f"Gefundene Cookie-Namen: {[c['name'] for c in cookies]}",
                file=sys.stderr,
            )
            return 1

        with open(args.output, "w") as f:
            f.write(target["value"])

        print(f"Cookie erfolgreich extrahiert und in {args.output} gespeichert.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
