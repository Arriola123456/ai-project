"""Build the calibration moments from the thesis pipeline (READ-ONLY on the source).

    python code/extract_moments.py

Reads the outputs of the thesis project Voluntary_Vote_Analysis and writes small
aggregate tables to code/data/. Nothing is ever written to the source folder.
It is not run by the CI (the source .dta files are ~3 GB and stay off the
repository); verify.py only uses the tables it produces.

Outputs (code/data/):
  theta_profiles.csv  tag, edad, b, se   -- theta_a = P(a) - P(69), mesa FE
  band_levels.csv     tag, banda, edad_min, edad_max, turnout, electores
  age_weights.csv     tag, edad, electores -- registered electors by exact age
  fines.csv           tag, fine_pct_uit, share_by_category...
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

SRC = Path(r"C:\Users\manue\OneDrive\Escritorio\Tesis\Voluntary_Vote_Analysis")
OUT = Path(__file__).resolve().parent / "data"
OUT.mkdir(exist_ok=True)

TAGS = ["2001_2V", "2006_1V", "2006_2V", "2011_1V", "2011_2V",
        "2016_1V", "2016_2V", "2021_1V", "2021_2V", "2026_1V"]
BANDS = {1: (18, 19), 2: (20, 29), 3: (30, 39), 4: (40, 49),
         5: (50, 59), 6: (60, 69), 7: (70, 130)}


def theta_profiles():
    frames = []
    for tag in TAGS:
        f = SRC / "4_output" / "2_Tablas" / f"PerfilTodasBandas_edades_{tag}.csv"
        d = pd.read_csv(f)[["edad", "b", "se"]]
        d.insert(0, "tag", tag)
        frames.append(d)
    out = pd.concat(frames).sort_values(["tag", "edad"])
    out.to_csv(OUT / "theta_profiles.csv", index=False)
    return out


def levels_and_weights(tag):
    """Band turnout (sum voters / sum electors) and electors by exact age."""
    path = SRC / "3_temp" / f"Analitica_Todas_Bandas_{tag}.dta"
    _, meta = pyreadstat.read_dta(path, metadataonly=True)
    shares = [c for c in meta.column_names if c[0] == "s" and c[1:].isdigit()]
    df, _ = pyreadstat.read_dta(path, usecols=["ubigeo", "banda", "N", "sufragantes", "turnout"] + shares)
    df = df[df["N"] > 0]
    # band levels
    g = df.groupby("banda")[["sufragantes", "N"]].sum()
    lev = pd.DataFrame({"tag": tag, "banda": g.index.astype(int),
                        "turnout": g["sufragantes"] / g["N"], "electores": g["N"]})
    lev["edad_min"] = lev["banda"].map(lambda b: BANDS[b][0])
    lev["edad_max"] = lev["banda"].map(lambda b: BANDS[b][1])
    # electors by exact age: share of the mesa-band times its electors
    ages = np.array([int(c[1:]) for c in shares])
    w = (df[shares].fillna(0).to_numpy() * df[["N"]].to_numpy()).sum(axis=0)
    aw = pd.DataFrame({"tag": tag, "edad": ages, "electores": w})
    aw = aw[aw["electores"] > 0]
    # sanity: every age sits in the band the ONPE assigns it to
    for b, (lo, hi) in BANDS.items():
        sub = df[df["banda"] == b][[f"s{a}" for a in ages if a < lo or a > hi]]
        assert np.nansum(sub.to_numpy()) < 1e-6, f"{tag}: ages outside band {b}"
    dist = df.groupby("ubigeo")["N"].sum().rename("electores").reset_index()
    return lev, aw, dist


def fines(tag, dist):
    year, rnd = int(tag[:4]), 1 if tag.endswith("1V") else 2
    f, _ = pyreadstat.read_dta(SRC / "3_temp" / "2_Multas_JNE" / "Multas_EG_2001_2026.dta")
    year_col = [c for c in f.columns if c.startswith("a") and c.endswith("o") and len(c) == 3][0]
    f = f[(f[year_col] == year) & (f["vuelta"] == rnd)]
    m = dist.merge(f[["ubigeo", "multa_pct_uit_exante", "clasif_pobreza"]], on="ubigeo", how="left")
    matched = m["multa_pct_uit_exante"].notna()
    wm = np.average(m.loc[matched, "multa_pct_uit_exante"], weights=m.loc[matched, "electores"])
    share = m[matched].groupby("clasif_pobreza")["electores"].sum() / m.loc[matched, "electores"].sum()
    row = {"tag": tag, "fine_pct_uit": wm,
           "electors_matched": m.loc[matched, "electores"].sum() / m["electores"].sum()}
    row.update({f"share_{k.lower().replace(' ', '_')}": v for k, v in share.items()})
    return row


def main():
    th = theta_profiles()
    print(f"theta_profiles: {len(th)} rows, {th.tag.nunique()} elections")
    levs, aws, fns = [], [], []
    for tag in TAGS:
        lev, aw, dist = levels_and_weights(tag)
        levs.append(lev); aws.append(aw); fns.append(fines(tag, dist))
        print(tag, "60-69:", round(lev.loc[lev.banda == 6, "turnout"].item(), 3),
              "70+:", round(lev.loc[lev.banda == 7, "turnout"].item(), 3),
              "fine %UIT:", round(fns[-1]["fine_pct_uit"], 3),
              "matched:", round(fns[-1]["electors_matched"], 4), flush=True)
    pd.concat(levs)[["tag", "banda", "edad_min", "edad_max", "turnout", "electores"]] \
        .to_csv(OUT / "band_levels.csv", index=False)
    pd.concat(aws).to_csv(OUT / "age_weights.csv", index=False)
    pd.DataFrame(fns).to_csv(OUT / "fines.csv", index=False)
    print("OK: wrote", ", ".join(p.name for p in sorted(OUT.glob("*.csv"))))


if __name__ == "__main__":
    main()
