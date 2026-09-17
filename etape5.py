"""
Étape 5 : feuille de comparaison (Départ vers Arrivée).

Pour chaque matricule en erreur, on raisonne par écart de % sur chaque case :
écart = % Comète moins % Cegid.
  écart négatif : Cegid a mis trop ici       -> case de Départ  (à vider)
  écart positif : Cegid a mis pas assez ici  -> case d'Arrivée  (à alimenter)

On apparie ensuite les départs et les arrivées d'un même agent, 
ce qui gère aussi les cas à plusieurs départs ou arrivées. 
Chaque ligne produite décrit un transfert : sortir X % d'un SS1/SS2 
(Départ, côté Cegid) vers un autre SS1/SS2 (Arrivée, côté Comète).

Le récapitulatif Débit/Crédit en euros du Word (5.3) est abandonné : pas de montant.
"""
import pandas as pd
import config


def run(comparaison):
    df = comparaison
    err_mats = sorted(df.loc[df["pct_ok"] == "FAUX", "matricule"].unique())

    lignes = []
    for mat in err_mats:
        g = df[df["matricule"] == mat]
        type_err = g.loc[g["type_erreur"] != "", "type_erreur"].iloc[0]

        # sépare les cases en trop (départs) et les cases manquantes (arrivées)
        departs, arrivees = [], []
        for _, r in g.iterrows():
            ecart = round(r["pct_comete"] - r["pct_cegid"], 6)
            if ecart < -config.TOLERANCE_PCT:
                departs.append([r["agence"], r["activite"], -ecart])
            elif ecart > config.TOLERANCE_PCT:
                arrivees.append([r["agence"], r["activite"], ecart])

        # apparie départ et arrivée en transférant le plus petit des deux %
        i = j = 0
        while i < len(departs) and j < len(arrivees):
            dep, arr = departs[i], arrivees[j]
            montant = min(dep[2], arr[2])
            lignes.append({
                "MATRICULE": mat,
                "Départ SS1": dep[0], "Départ SS2": dep[1],
                "Arrivée SS1": arr[0], "Arrivée SS2": arr[1],
                "% déplacé": montant,
                "Commentaire": type_err,
            })
            dep[2] -= montant
            arr[2] -= montant
            if dep[2] <= config.TOLERANCE_PCT:
                i += 1
            if arr[2] <= config.TOLERANCE_PCT:
                j += 1

    result = pd.DataFrame(lignes, columns=[
        "MATRICULE", "Départ SS1", "Départ SS2",
        "Arrivée SS1", "Arrivée SS2", "% déplacé", "Commentaire"])
    print(f"   Etape 5 : {len(result)} lignes de retraitement "
          f"pour {len(err_mats)} matricules en erreur")
    return result