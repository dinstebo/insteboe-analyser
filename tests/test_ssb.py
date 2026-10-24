"""Tester for omformingen av svar fra SSB. Testene bruker ikke nettverk."""

from insteboe_analyser.ssb import fra_jsonstat, lag_sporring

SVAR = {
    "id": ["Region", "Tid"],
    "dimension": {
        "Region": {"category": {"index": {"0301": 0, "4601": 1}, "label": {"0301": "Oslo", "4601": "Bergen"}}},
        "Tid": {"category": {"index": {"2024": 0, "2025": 1}, "label": {"2024": "2024", "2025": "2025"}}},
    },
    "value": [1, 2, 3, 4],
}


def test_rader_folger_rekkefolgen_i_jsonstat():
    rader = fra_jsonstat(SVAR)
    assert [(r["Region"], r["Tid"], r["verdi"]) for r in rader] == [
        ("Oslo", "2024", 1),
        ("Oslo", "2025", 2),
        ("Bergen", "2024", 3),
        ("Bergen", "2025", 4),
    ]


def test_rader_har_bade_kode_og_etikett():
    rad = fra_jsonstat(SVAR)[2]
    assert rad["Region"] == "Bergen"
    assert rad["Region_kode"] == "4601"


def test_indeks_som_liste_virker():
    svar = {
        "id": ["Tid"],
        "dimension": {"Tid": {"category": {"index": ["2024", "2025"]}}},
        "value": [7, 8],
    }
    assert [r["Tid"] for r in fra_jsonstat(svar)] == ["2024", "2025"]


def test_stjerne_gir_alle_verdier():
    sporring = lag_sporring({"Region": ["*"], "Tid": ["2025"]})
    assert sporring["query"][0]["selection"]["filter"] == "all"
    assert sporring["query"][1]["selection"]["filter"] == "item"
    assert sporring["response"]["format"] == "json-stat2"
