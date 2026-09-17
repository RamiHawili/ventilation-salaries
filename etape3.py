"""
Étape 3 : comparaison Cegid / Comète (détection des écarts).

Équivaut aux deux tableaux croisés du Word du dernière alternant (matricule en lignes, filtres
SS1/SS2, somme des %) : on regroupe chaque base par matricule x SS1 x SS2,
puis on les met face à face. Deux facteurs sont vérifiés (le coût est abandonné) :

  Matricule OK : le placement (matricule + SS1 + SS2) existe-t-il des deux côtés ?
  % OK         : le pourcentage correspond-il, à la tolérance près ?

Seuls les matricules présents dans Comète (le relevé du mois) sont comparés.
Les corrections porteront toujours sur Cegid (Comète est la référence).
"""
import pandas as pd
import config


def _maille(df):
    """Regroupe par matricule x SS1 x SS2 en sommant les % (comme un TCD)."""
    return df.groupby(["matricule", "agence", "activite"], as_index=False)["pct"].sum()


def run(cegid_propre, comete):
    cegid_m = _maille(cegid_propre)
    comete_m = _maille(comete)

    # périmètre : uniquement les matricules du relevé Comète
    ref = set(comete_m["matricule"])
    cegid_ref = cegid_m[cegid_m["matricule"].isin(ref)]

    # jointure des deux bases sur le trio matricule / SS1 / SS2
    comp = pd.merge(
        cegid_ref, comete_m,
        on=["matricule", "agence", "activite"], how="outer",
        suffixes=("_cegid", "_comete"), indicator=True,
    )
    comp["pct_cegid"] = comp["pct_cegid"].fillna(0)
    comp["pct_comete"] = comp["pct_comete"].fillna(0)
    comp["ecart"] = (comp["pct_cegid"] - comp["pct_comete"]).abs()

    present_2 = comp["_merge"] == "both"   # la case existe dans les deux bases

    # facteur Matricule : le placement est-il présent des deux côtés ?
    comp["matricule_ok"] = present_2.map({True: "VRAI", False: "FAUX"})
    # facteur % : présent des deux côtés ET même pourcentage (tolérance)
    pct_ok = present_2 & (comp["ecart"] <= config.TOLERANCE_PCT)
    comp["pct_ok"] = pct_ok.map({True: "VRAI", False: "FAUX"})

    comp = comp.drop(columns="_merge")
    # les écarts (% OK = FAUX) sont remontés en tête
    comp = comp.sort_values(["pct_ok", "matricule", "agence", "activite"]).reset_index(drop=True)

    n_err = (comp["pct_ok"] == "FAUX").sum()
    print(f"   Etape 3 : {len(comp)} lignes comparees, {n_err} en erreur (facteur % = FAUX)")
    return comp