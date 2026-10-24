# Analysene bak tekstene på insteboe.org

Her ligger koden bak tallene i tekstene mine på [insteboe.org](https://insteboe.org).
Målet er at alle tall skal kunne etterprøves. Skriptene henter dataene direkte fra
Statistikkbanken til SSB gjennom det åpne API-et, så du trenger ingen nøkkel eller
nedlastede filer.

| Tekst | Skript | Kilder |
|---|---|---|
| Hvorfor kan ett ekstra soverom koste en million? | [`analyser/soverom.py`](analyser/soverom.py) | SSB-tabell 06515, 06518, 09897, 14545 og 14911 |
| Hvorfor leier vi lagerplass til tingene våre? | [`analyser/lagerplass.py`](analyser/lagerplass.py) | SSB-tabell 05940 og 14545, FEDESSA 2018 og 2025 |

## Hva analysene undersøker

**Soverom.** Blir det uforholdsmessig dyrt å gå fra tre til fire soverom? Skriptet
henter kvadratmeterpriser, predikert husleie etter antall rom og areal, boligmassen
etter antall rom og andelen husholdninger som bor trangt etter antall barn. Hovedfunnet
er at det femte rommet ikke koster mer enn det fjerde når arealet holdes fast. Det som
skiller, er at boliger med fem rom eller flere er sjeldne i byene.

**Lagerplass.** Har nye boliger mindre lagringsplass, og lønner det seg å leie
minilager? Skriptet viser hvordan andelen blokkleiligheter blant nye boliger har
endret seg, hvor mye minilagerbransjen har vokst, og et regneeksempel som sammenligner
renten på en bod med leien for et minilager.

## Kom i gang

Prosjektet bruker [Poetry](https://python-poetry.org) og Python 3.11 eller nyere.
Analysene har ingen avhengigheter utover standardbiblioteket.

```bash
poetry install
poetry run python analyser/soverom.py
poetry run python analyser/lagerplass.py
poetry run pytest
```

## Slik er koden bygget opp

- `src/insteboe_analyser/ssb.py` sender spørringer til SSBs API (PxWebApi v0) og gjør
  om svaret i JSON-stat 2.0 til enkle rader med både koder og tekstetiketter.
- `analyser/` har ett skript per tekst. Årstallene er låst til de årene teksten
  bygger på, slik at resultatet blir det samme senere.
- `tests/` tester omformingen av API-svarene uten å bruke nettverk.

## Forutsetninger og forbehold

Noen tall i tekstene er regneeksempler og ikke målinger. Forutsetningene står som
navngitte konstanter øverst i skriptene, for eksempel rentenivå og valutakurs.
Tallene for minilager kommer fra bransjeforeningen FEDESSA. Rapportene finnes bare
som PDF, så tallene står i koden med kildehenvisning.

SSB kan revidere tall i Statistikkbanken. Små avvik fra tekstene kan derfor
forekomme over tid.

## Lisens

Koden er lisensiert under MIT. Dataene fra SSB er lisensiert under
[NLOD og CC BY 4.0](https://www.ssb.no/diverse/lisens).
