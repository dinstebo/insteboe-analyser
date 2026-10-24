"""Henter tabeller fra Statistikkbanken til SSB gjennom det åpne API-et (PxWebApi v0).

API-et er åpent og krever ingen nøkkel. Svaret kommer som JSON-stat 2.0 og gjøres
om til en liste med rader. Hver rad har tekstetiketten og koden for hver
dimensjon (for eksempel «Region» og «Region_kode») og selve tallet i «verdi».

Dokumentasjon: https://www.ssb.no/api/pxwebapi
"""

from __future__ import annotations

import itertools
import json
import urllib.request
from typing import Any

API_URL = "https://data.ssb.no/api/v0/no/table/{tabell}"


def lag_sporring(utvalg: dict[str, list[str]]) -> dict[str, Any]:
    """Bygger spørringen API-et forventer, med ett utvalg per variabel.

    Verdien ["*"] betyr alle verdier for variabelen.
    """
    return {
        "query": [
            {
                "code": kode,
                "selection": {"filter": "all" if verdier == ["*"] else "item", "values": verdier},
            }
            for kode, verdier in utvalg.items()
        ],
        "response": {"format": "json-stat2"},
    }


def fra_jsonstat(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Gjør et JSON-stat 2.0-svar om til rader med tekstetiketter.

    Verdiene i JSON-stat ligger i én flat liste. Rekkefølgen følger
    dimensjonene i «id», med den siste dimensjonen innerst.
    """
    dimensjoner = data["id"]
    koder = []
    etiketter = []
    for dim in dimensjoner:
        kategori = data["dimension"][dim]["category"]
        indeks = kategori["index"]
        # «index» kan være en ordbok (kode -> posisjon) eller en liste.
        if isinstance(indeks, dict):
            ordnet = sorted(indeks, key=indeks.get)
        else:
            ordnet = list(indeks)
        koder.append(ordnet)
        etiketter.append(kategori.get("label", {k: k for k in ordnet}))

    rader = []
    for kombinasjon, verdi in zip(itertools.product(*koder), data["value"]):
        rad: dict[str, Any] = {}
        for i, (dim, kode) in enumerate(zip(dimensjoner, kombinasjon)):
            rad[dim] = etiketter[i][kode]
            rad[f"{dim}_kode"] = kode
        rad["verdi"] = verdi
        rader.append(rad)
    return rader


def hent_tabell(tabell: str, utvalg: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Henter en tabell fra Statistikkbanken med det oppgitte utvalget."""
    sporring = json.dumps(lag_sporring(utvalg)).encode("utf-8")
    foresporsel = urllib.request.Request(
        API_URL.format(tabell=tabell),
        data=sporring,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(foresporsel, timeout=60) as svar:
        return fra_jsonstat(json.load(svar))
