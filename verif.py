"""
Contrôles de fiabilité du pipeline (à lancer séparément : python verif.py).

Rejoue les étapes 2 à 6 sur les fichiers du dossier data/, puis vérifie six
points clés. Chaque contrôle affiche VALIDE ou ECHEC, et un verdict global
tombe à la fin. À relancer chaque mois après avoir remplacé les fichiers.
"""
import pandas as pd

import config
import etape2
import etape3
import etape4
import etape5
import etape6
from main import _load   # on réutilise le même chargeur que le programme principal

TOL = config.TOLERANCE_PCT


def _pipeline():
    """Rejoue tout le traitement et renvoie les résultats intermédiaires."""
    cegid_raw = _load(config.CEGID_FILE, config.CEGID_SHEET, config.CEGID_COLS)
    comete = _load(config.COMETE_FILE, config.COMETE_SHEET, config.COMETE_COLS)
    comete["pct"] = pd.to_numeric(comete["pct"], errors="coerce")

    cegid = etape2.run(cegid_raw)
    comparaison = etape4.run(etape3.run(cegid, comete))
    noms = dict(zip(cegid["matricule"], cegid["nom_prenom"]))
    retraitement = etape5.run(comparaison, noms)
    cas_att = etape6.run(cegid, comete)
    return cegid, comete, comparaison, retraitement, cas_att


def verifier():
    cegid, comete, comp, retr, att = _pipeline()
    resultats = []   # (nom du test, ok, detail)

    # 1) Nettoyage : aucune ligne fantôme ni matricule vide en sortie
    ok = (cegid["pct"] > 0).all() and cegid["matricule"].notna().all()
    resultats.append(("Nettoyage (aucune ligne a 0 ni matricule vide)", ok,
                      f"{len(cegid)} lignes propres"))

    # 2) Complétude : tout agent en erreur figure dans la feuille de retraitement
    err_mats = set(comp.loc[comp["pct_ok"] == "FAUX", "matricule"])
    manquants = err_mats - set(retr["MATRICULE"])
    resultats.append(("Completude (aucun agent en erreur oublie)", not manquants,
                      f"{len(err_mats)} agents en erreur, {len(manquants)} oublie(s)"))

    # 3) Conservation : par agent, ce qui part = ce qui arrive = somme des transferts
    souci = []
    for m in err_mats:
        g = comp[comp["matricule"] == m]
        depart = (g["pct_cegid"] - g["pct_comete"]).clip(lower=0).sum()
        arrivee = (g["pct_comete"] - g["pct_cegid"]).clip(lower=0).sum()
        transferts = retr.loc[retr["MATRICULE"] == m, "% déplacé"].sum()
        if abs(depart - arrivee) > 0.01 or abs(transferts - depart) > 0.01:
            souci.append(m)
    resultats.append(("Conservation (depart = arrivee = transferts)", not souci,
                      f"{len(souci)} agent(s) desequilibre(s)"))

    # 4) Totaux Comète : chaque agent du périmètre fait environ 100 %
    tot = comete.groupby("matricule")["pct"].sum()
    hors = tot[(tot - 1).abs() > 0.01]
    resultats.append(("Totaux Comete (~100 % par agent)", len(hors) == 0,
                      f"{len(hors)} agent(s) hors 100 %"))

    # 5) ATT : tous les ATT du Cegid sont remontés dans l'onglet dédié
    att_cegid = set(cegid.loc[(cegid["agence"] == "ATT") |
                              (cegid["activite"] == "ATT"), "matricule"])
    att_manquants = att_cegid - set(att["MATRICULE"])
    resultats.append(("Cas ATT (tous remontes)", not att_manquants,
                      f"{len(att_cegid)} agent(s) ATT, {len(att_manquants)} oublie(s)"))

    # 6) % déplacé : toutes les valeurs strictement positives
    ok_pct = (retr["% déplacé"] > 0).all() if len(retr) else True
    resultats.append(("Coherence (tous les % deplaces > 0)", ok_pct,
                      f"{len(retr)} lignes de retraitement"))

    # Affichage
    print("\n==================== CONTROLES ====================")
    for nom, ok, detail in resultats:
        etat = "VALIDE" if ok else "ECHEC "
        print(f"  [{etat}] {nom:<48} ({detail})")
    print("===================================================")
    if all(ok for _, ok, _ in resultats):
        print(">> TOUT EST VALIDE : le traitement est fiable.")
    else:
        n = sum(1 for _, ok, _ in resultats if not ok)
        print(f">> {n} controle(s) en ECHEC : a examiner avant d'utiliser le fichier.")


if __name__ == "__main__":
    verifier()