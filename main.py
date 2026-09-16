"""
=======================================================================
  FIABILISATION MASSE SALARIALE - Comète (référence) vs Cegid (à corriger)
  LE SEUL FICHIER A LANCER :   python main.py
=======================================================================
  ETAPE 2  nettoyage du Cegid ............ FAIT   (etape2.py)
  ETAPE 3  comparaison Cegid / Comète .... à venir
  ETAPE 4  repérage des retraitements ... à venir
  ETAPE 5  feuille de comparaison ....... à venir
"""
import re
import pandas as pd

import config
import etape2
from style_excel import write_sheet


def _norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def _find_col(df, wanted):
    m = {_norm(c): c for c in df.columns}
    if _norm(wanted) in m:
        return m[_norm(wanted)]
    raise KeyError(f"Colonne '{wanted}' introuvable. Colonnes dispo : {list(df.columns)}")


def _load(path, sheet, colmap):
    """Charge un fichier et renomme les colonnes utiles. Matricule gardé en TEXTE."""
    raw = pd.read_excel(path, sheet_name=sheet, header=0, dtype=str)
    out = pd.DataFrame()
    for canon, src in colmap.items():
        out[canon] = raw[_find_col(raw, src)]
    return out


def main():
    print(">> Chargement des fichiers...")
    # 2.3 - on charge les deux bases : Cegid (à corriger) et Comète (référence)
    cegid_raw = _load(config.CEGID_FILE, config.CEGID_SHEET, config.CEGID_COLS)
    comete = _load(config.COMETE_FILE, config.COMETE_SHEET, config.COMETE_COLS)
    comete["pct"] = pd.to_numeric(comete["pct"], errors="coerce")
    print(f"   Cegid : {len(cegid_raw)} lignes | Comete : {len(comete)} lignes")

    # ETAPE 2 - nettoyage du Cegid
    cegid = etape2.run(cegid_raw)

    # 2.3 - les deux bases dans un même fichier, un onglet chacune
    cg = cegid.rename(columns={"matricule": "Salarié", "nom_prenom": "Nom Prénom",
                               "agence": "Sous-Plan 1", "activite": "Sous-Plan 2", "pct": "%"})
    cm = comete.rename(columns={"matricule": "Matricule", "agence": "ID_Agence",
                                "activite": "ID_Activité", "pct": "%"})
    cg = cg[["Salarié", "Nom Prénom", "%", "Sous-Plan 1", "Sous-Plan 2"]]
    cm = cm[["Matricule", "%", "ID_Agence", "ID_Activité"]]

    with pd.ExcelWriter(config.OUTPUT_FILE, engine="openpyxl") as w:
        write_sheet(w, cg, "Cegid (nettoye)", "Cegid nettoyé - à corriger",
                    "Etape 2 : matricules complétés, lignes parasites retirées, % en décimal",
                    header="vert", text_cols=["Salarié", "Nom Prénom"], pct_cols=["%"])
        write_sheet(w, cm, "Comete (reference)", "Comète - référence du mois",
                    "Base de référence pour la comparaison",
                    header="gris", text_cols=["Matricule"], pct_cols=["%"])

    print(f"\n>> Termine. Fichier ecrit : {config.OUTPUT_FILE}")


if __name__ == "__main__":
    main()