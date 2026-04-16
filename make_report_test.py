# TBC ...
from make_report import calculate_align_stats

from pytest import fail

def test_calculate_align_stats():
    for t in [
        {
            "qlen": 10,
            "alnlen": 10,
            "reflen": 10,
            "nins": 0,
            "ndel": 0,
            "editdist": 0,
            "softclips": 0,
            "want_identity": 1,
            "want_coverage": 1,
        },
        {
            "qlen": 10,
            "alnlen": 10,
            "reflen": 10,
            "nins": 0,
            "ndel": 0,
            "editdist": 0,
            "softclips": 0,
            "want_identity": 1,
            "want_coverage": 1,
        },
    ]:
        id, cov = calculate_align_stats(t["qlen"], t["alnlen"],
                                        t["reflen"], t["nins"], t["ndel"],
                                        t["editdist"], t["softclips"])

        if cov != t["want_coverage"]:
            fail(f"Wanted coverage {t['want_coverage']} but got {cov}")

        if id != t["want_identity"]:
            fail(f"Wanted identity {t['want_identity']} but got {id}")

