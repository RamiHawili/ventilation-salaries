"""
Étape 4 : qualification de chaque écart.

Pour chaque matricule en erreur, on compare l'ensemble de ses placements
(SS1/SS2) côté Cegid et côté Comète, et on en déduit la nature de l'erreur :

  4.1, le placement change :
       l'agence (SS1) diffère            : "Erreur d'agence (SS1)"
       seule l'activité (SS2) diffère    : "Erreur d'activité (SS2)"
       les deux diffèrent                : "Erreur d'agence et d'activité (SS1+SS2)"
  4.2, mêmes cases mais partage différent : "Répartition % incorrecte"

Le type n'est renseigné que sur les lignes en erreur (% OK = FAUX).
"""


def _type_erreur(cegid_pl, comete_pl):
    """Déduit le type d'erreur à partir des ensembles de couples (SS1, SS2)."""
    if cegid_pl == comete_pl:
        # mêmes cases des deux côtés : seul le pourcentage diffère
        return "Repartition % incorrecte"
    ag_cegid = {a for a, _ in cegid_pl}
    ag_comete = {a for a, _ in comete_pl}
    act_cegid = {b for _, b in cegid_pl}
    act_comete = {b for _, b in comete_pl}
    if ag_cegid != ag_comete and act_cegid != act_comete:
        return "Erreur d'agence et d'activite (SS1+SS2)"
    if ag_cegid != ag_comete:
        return "Erreur d'agence (SS1)"
    return "Erreur d'activite (SS2)"


def run(comparaison):
    df = comparaison.copy()

    # un type d'erreur par matricule (les lignes correctes restent vides)
    types = {}
    for mat, g in df.groupby("matricule"):
        if not (g["pct_ok"] == "FAUX").any():
            types[mat] = ""
            continue
        cegid_pl = set(map(tuple, g.loc[g["pct_cegid"] > 0, ["agence", "activite"]].values))
        comete_pl = set(map(tuple, g.loc[g["pct_comete"] > 0, ["agence", "activite"]].values))
        types[mat] = _type_erreur(cegid_pl, comete_pl)

    df["type_erreur"] = df["matricule"].map(types)
    df.loc[df["pct_ok"] == "VRAI", "type_erreur"] = ""   # rien sur les lignes correctes

    # récapitulatif console : nombre de matricules par type d'erreur
    recap = (df.loc[df["pct_ok"] == "FAUX"]
               .drop_duplicates("matricule")["type_erreur"].value_counts())
    print("   Etape 4 : types d'erreur (par matricule) :")
    for t, n in recap.items():
        print(f"      - {t:<38}: {n}")
    return df