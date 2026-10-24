"""Tallene bak «Hvorfor leier vi lagerplass til tingene våre?».

Kjør med:  poetry run python analyser/lagerplass.py

Boligtallene hentes fra Statistikkbanken til SSB. Tallene for minilager kommer fra
bransjeforeningen FEDESSA og står som konstanter med kilde, fordi rapportene bare
finnes som PDF.
"""

from collections import defaultdict

from insteboe_analyser.ssb import hent_tabell

# FEDESSA European Self Storage Annual Survey 2018, tabell over markedsstørrelse.
FEDESSA_2018_KVM_NORGE = 133_000
FEDESSA_2018_ANLEGG_NORGE = 139
# FEDESSA og CBRE: European Self Storage Industry Report 2025, side om markedsstørrelse.
FEDESSA_2025_KVM_NORGE = 365_000
FEDESSA_2025_BELEGG_NORGE = 0.733
FEDESSA_2025_LEIE_EUR_PER_KVM_AAR = 269  # uten merverdiavgift

# Forutsetninger i regneeksempelet. De er valgt, ikke målt.
EURO_I_KRONER = 11.5
RENTE = 0.05
RENTEFRADRAG = 0.22
BOD_KVM = 3
INNBYGGERE_2025 = 5_600_000  # avrundet

# Store boligbygg (blokker) har bygningstypekoder som begynner på 14.
BLOKK_PREFIKS = "14"


def blokkandel(aar: list[str]) -> None:
    """Tabell 05940: andel fullførte boliger som ligger i store boligbygg."""
    rader = hent_tabell(
        "05940",
        {"Region": ["0"], "Byggeareal": ["*"], "ContentsCode": ["Fullforte"], "Tid": aar},
    )
    totalt: dict[str, float] = defaultdict(float)
    blokk: dict[str, float] = defaultdict(float)
    for rad in rader:
        totalt[rad["Tid"]] += rad["verdi"] or 0
        if rad["Byggeareal_kode"].startswith(BLOKK_PREFIKS):
            blokk[rad["Tid"]] += rad["verdi"] or 0
    print("\nAndel nye boliger i store boligbygg (blokk):")
    for aar_ in sorted(totalt):
        print(f"  {aar_}: {100 * blokk[aar_] / totalt[aar_]:.0f} % av {totalt[aar_]:,.0f} fullførte boliger")


def minilager() -> None:
    vekst = FEDESSA_2025_KVM_NORGE / FEDESSA_2018_KVM_NORGE
    per_person = FEDESSA_2025_KVM_NORGE / INNBYGGERE_2025
    print("\nMinilager i Norge (FEDESSA):")
    print(f"  2018: {FEDESSA_2018_ANLEGG_NORGE} anlegg og {FEDESSA_2018_KVM_NORGE:,} m²")
    print(f"  2025: {FEDESSA_2025_KVM_NORGE:,} m², {FEDESSA_2025_BELEGG_NORGE:.0%} utleid")
    print(f"  Vekst 2018–2025: {vekst:.1f} ganger")
    print(f"  Per innbygger: {per_person:.3f} m² (omtrent {per_person ** 0.5 * 100:.0f} x {per_person ** 0.5 * 100:.0f} cm)")


def bod_mot_lager() -> None:
    """Sammenligner rentekostnaden for en bod med leie av like stort lager."""
    rader = hent_tabell(
        "14545",
        {"Region": ["0301", "4601"], "Boligtype": ["03"], "ContentsCode": ["KvPris"], "Tid": ["2025"]},
    )
    leie_per_kvm = FEDESSA_2025_LEIE_EUR_PER_KVM_AAR * EURO_I_KRONER
    leie = BOD_KVM * leie_per_kvm
    print(f"\nBod på {BOD_KVM} m² mot minilager på {BOD_KVM} m² (kroner per år):")
    print(f"  Minilager: {leie_per_kvm:,.0f} kr per m² og år, {leie:,.0f} kr totalt")
    for rad in rader:
        verdi = BOD_KVM * rad["verdi"]
        rente = verdi * RENTE * (1 - RENTEFRADRAG)
        print(f"  Bod i {rad['Region']}: verdi {verdi:,.0f} kr, rente etter fradrag {rente:,.0f} kr")


if __name__ == "__main__":
    blokkandel(["2000", "2025"])
    minilager()
    bod_mot_lager()
