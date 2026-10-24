"""Tallene bak «Hvorfor kan ett ekstra soverom koste en million?».

Kjør med:  poetry run python analyser/soverom.py

Alle tall hentes fra Statistikkbanken til SSB. Årstallene er låst til de årene
teksten bygger på, slik at resultatet kan gjenskapes.
"""

from collections import defaultdict

from insteboe_analyser.ssb import hent_tabell

KOMMUNER = {"0301": "Oslo", "4601": "Bergen", "4624": "Bjørnafjorden"}
ALLE_ROM = ["1", "2", "3", "4", "5", "6", "7", "8"]
FEM_ROM_ELLER_FLERE = {"5 rom", "6 rom", "7 rom", "8 rom eller flere"}


def prosent(del_: float, helhet: float) -> str:
    return f"{100 * del_ / helhet:.0f} %"


def kvadratmeterpris() -> dict[str, float]:
    """Tabell 14545: snittpris per kvadratmeter for blokkleiligheter i 2025."""
    rader = hent_tabell(
        "14545",
        {"Region": ["0301", "4601"], "Boligtype": ["03"], "ContentsCode": ["KvPris"], "Tid": ["2025"]},
    )
    return {rad["Region"]: rad["verdi"] for rad in rader}


def regneeksempel(priser: dict[str, float]) -> None:
    print("\nRegneeksempel: hva koster 15–20 kvadratmeter ekstra?")
    for region, pris in priser.items():
        print(f"  {region}: {pris:,.0f} kr/m², 15–20 m² = {15 * pris / 1e6:.1f}–{20 * pris / 1e6:.1f} mill. kr")


def leie_etter_rom() -> None:
    """Tabell 09897: predikert månedsleie for 100 m² med tre, fire og fem rom."""
    utvalg = ["3.100", "4.100", "5.100"]
    rader = hent_tabell(
        "09897",
        {"Soner2": ["01.02", "03.02"], "AntRomBRA": utvalg, "ContentsCode": ["Husleie"], "Tid": ["2025"]},
    )
    print("\nPredikert månedsleie for 100 m² (2025):")
    for rad in rader:
        print(f"  {rad['Soner2']}: {rad['AntRomBRA']}: {rad['verdi']:,.0f} kr")


def andel_store_boliger(tabell: str, ekstra: dict[str, list[str]], tittel: str) -> None:
    """Andel boliger med fem rom eller flere."""
    rader = hent_tabell(
        tabell,
        {"Region": list(KOMMUNER), "AntRom": ALLE_ROM, "Tid": ["2026"], **ekstra},
    )
    totalt: dict[str, float] = defaultdict(float)
    store: dict[str, float] = defaultdict(float)
    for rad in rader:
        totalt[rad["Region"]] += rad["verdi"] or 0
        if rad["AntRom"] in FEM_ROM_ELLER_FLERE:
            store[rad["Region"]] += rad["verdi"] or 0
    print(f"\n{tittel}")
    for region in totalt:
        print(f"  {region}: {prosent(store[region], totalt[region])} har fem rom eller flere")


def trangboddhet() -> None:
    """Tabell 14911: andel husholdninger som bor trangt, etter antall barn (2025)."""
    rader = hent_tabell(
        "14911",
        {
            "Region": list(KOMMUNER),
            "Trangboddhet": ["1"],
            "AntBarn": ["02", "03+"],
            "ContentsCode": ["HusholdningProsent"],
            "Tid": ["2025"],
        },
    )
    print("\nAndel husholdninger som bor trangt (2025):")
    for rad in rader:
        print(f"  {rad['Region']}, {rad['AntBarn']}: {rad['verdi']:.0f} %")


def rentekostnad(laan: float = 1_000_000, rente: float = 0.05, fradrag: float = 0.22) -> None:
    """Rentekostnad etter skattefradrag. Renten er en forutsetning, ikke et faktisk tall."""
    aarlig = laan * rente
    print(f"\nRente på {laan:,.0f} kr med {rente:.0%} rente:")
    print(f"  {aarlig:,.0f} kr i året før fradrag, {aarlig * (1 - fradrag) / 12:,.0f} kr i måneden etter fradrag")


if __name__ == "__main__":
    regneeksempel(kvadratmeterpris())
    leie_etter_rom()
    andel_store_boliger(
        "06515",
        {"BygnType": ["01", "02", "03", "04", "05", "999"]},
        "Alle boliger (2026):",
    )
    andel_store_boliger("06518", {"ByggeAar2": ["13"]}, "Boliger bygget i 2021 eller senere:")
    trangboddhet()
    rentekostnad()
