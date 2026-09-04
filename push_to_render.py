"""
Setzt TP_AUTH_COOKIE als Umgebungsvariable auf dem Render-Service und
stößt anschließend ein Redeploy an, damit der neue Wert übernommen wird.
"""

import argparse
import os
import sys

import requests

RENDER_API_BASE = "https://api.render.com/v1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cookie-file", required=True)
    args = parser.parse_args()

    api_key = os.environ["RENDER_API_KEY"]
    service_id = os.environ["RENDER_SERVICE_ID"]

    with open(args.cookie_file) as f:
        cookie_value = f.read().strip()

    if not cookie_value:
        print("FEHLER: Cookie-Datei ist leer.", file=sys.stderr)
        return 1

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # 1. Env-Var setzen
    r = requests.put(
        f"{RENDER_API_BASE}/services/{service_id}/env-vars/TP_AUTH_COOKIE",
        headers=headers,
        json={"value": cookie_value},
        timeout=30,
    )
    r.raise_for_status()
    print("Umgebungsvariable TP_AUTH_COOKIE erfolgreich aktualisiert.")

    # 2. Deploy anstoßen, damit der neue Wert geladen wird
    r = requests.post(
        f"{RENDER_API_BASE}/services/{service_id}/deploys",
        headers=headers,
        json={},
        timeout=30,
    )
    r.raise_for_status()
    deploy_id = r.json().get("id", "unbekannt")
    print(f"Redeploy angestoßen (deploy id: {deploy_id}).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
