"""
Étape 6 : relevé des cas ATT (attente).

L'affectation ATT (attente) n'existe jamais dans Comète : c'est donc toujours
une situation à vérifier, souvent un agent en attente ayant conservé le %
d'une ancienne mission.

On liste tous les agents ayant de l'ATT dans Cegid (en SS1 ou SS2) et on ajoute
la colonne "Dans Comète ?" :
  Oui : l'agent est dans le relevé du mois, donc déjà traité dans "Comparaison".
  Non : hors périmètre, il n'est corrigé nulle part : à réaffecter à la main.
"""
import pandas as pd


def run(cegid_propre, comete):
    ref = set(comete["matricule"])
    att = cegid_propre[(cegid_propre["agence"] == "ATT") |
                       (cegid_propre["activite"] == "ATT")].copy()

    att["Dans Comète ?"] = att["matricule"].apply(lambda m: "Oui" if m in ref else "Non")
    att = att.rename(columns={
        "matricule": "MATRICULE", "nom_prenom": "Nom Prénom",
        "agence": "SS1", "activite": "SS2", "pct": "%"})
    att = att[["MATRICULE", "Nom Prénom", "SS1", "SS2", "%", "Dans Comète ?"]]
    att = att.sort_values(["Dans Comète ?", "MATRICULE"]).reset_index(drop=True)

    print(f"   Etape 6 : {att['MATRICULE'].nunique()} agent(s) avec de l'ATT "
          f"({(att['Dans Comète ?']=='Non').sum()} ligne(s) hors perimetre)")
    return att