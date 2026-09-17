"""
=======================================================================
  FIABILISATION MASSE SALARIALE : Comète (référence) contre Cegid (à corriger)
  Fichier unique à lancer :   python main.py
=======================================================================

  Rôle de ce fichier : c'est l'orchestre. Il charge les deux bases,
  enchaîne les étapes 2 à 6, puis écrit un classeur Excel à cinq onglets.
  Chaque étape vit dans son propre fichier ; ici on ne fait que les appeler
  dans l'ordre et mettre en forme le résultat.

  Enchaînement des étapes :
    Étape 2 : nettoyage du Cegid                       (etape2.py)
    Étape 3 : comparaison Cegid / Comète               (etape3.py)
    Étape 4 : qualification des écarts (type d'erreur) (etape4.py)
    Étape 5 : feuille de retraitement Départ->Arrivée  (etape5.py)
    Étape 6 : relevé des cas ATT (attente)             (etape6.py)

  Onglets produits dans le classeur de sortie :
    Cegid (nettoye) . Comete (reference) . Erreurs détectées .
    Comparaison . Cas ATT (à vérifier)
"""
import re
import pandas as pd

import config
import etape2
import etape3
import etape4
import etape5
import etape6
from style_excel import write_sheet


# =====================================================================
#  OUTILS DE LECTURE DES FICHIERS
# =====================================================================

def _norm(s):
    """Normalise un nom de colonne : minuscules, espaces multiples réduits."""
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def _find_col(df, wanted):
    """
    Retrouve la vraie colonne du fichier correspondant au nom voulu,
    en ignorant la casse et les espaces multiples (ex. "Nom  Prénom").
    Lève une erreur explicite si la colonne est introuvable.
    """
    m = {_norm(c): c for c in df.columns}
    if _norm(wanted) in m:
        return m[_norm(wanted)]
    raise KeyError(f"Colonne '{wanted}' introuvable. Colonnes dispo : {list(df.columns)}")


def _load(path, sheet, colmap):
    """
    Charge un onglet Excel et ne garde que les colonnes utiles, renommées
    avec les noms internes communs (matricule, nom_prenom, pct, agence, activite).
    Le matricule est lu en TEXTE (dtype=str) pour conserver les zéros de tête.
    """
    raw = pd.read_excel(path, sheet_name=sheet, header=0, dtype=str)
    out = pd.DataFrame()
    for canon, src in colmap.items():
        out[canon] = raw[_find_col(raw, src)]
    return out


# =====================================================================
#  PROGRAMME PRINCIPAL
# =====================================================================

def main():

    # -----------------------------------------------------------------
    #  Chargement des deux bases
    #  Cegid  = fichier à corriger  |  Comète = référence du mois
    # -----------------------------------------------------------------
    print(">> Chargement des fichiers...")
    cegid_raw = _load(config.CEGID_FILE, config.CEGID_SHEET, config.CEGID_COLS)
    comete = _load(config.COMETE_FILE, config.COMETE_SHEET, config.COMETE_COLS)
    # le % de Comète est déjà en décimal : on le convertit juste en nombre
    comete["pct"] = pd.to_numeric(comete["pct"], errors="coerce")
    print(f"   Cegid : {len(cegid_raw)} lignes | Comete : {len(comete)} lignes")

    # -----------------------------------------------------------------
    #  Enchaînement des traitements (étapes 2 à 6)
    # -----------------------------------------------------------------
    cegid = etape2.run(cegid_raw)              # 2 : nettoyage du Cegid
    comparaison = etape3.run(cegid, comete)    # 3 : comparaison des deux bases
    comparaison = etape4.run(comparaison)      # 4 : type d'erreur par écart
    retraitement = etape5.run(comparaison)     # 5 : feuille Départ -> Arrivée
    cas_att = etape6.run(cegid, comete)        # 6 : relevé des cas ATT

    # -----------------------------------------------------------------
    #  Préparation des tableaux pour l'affichage
    #  (on remet des noms de colonnes lisibles avant d'écrire l'Excel)
    # -----------------------------------------------------------------

    # Onglet 1 : Cegid nettoyé, avec ses noms de colonnes d'origine
    cg = cegid.rename(columns={"matricule": "Salarié", "nom_prenom": "Nom Prénom",
                               "agence": "Sous-Plan 1", "activite": "Sous-Plan 2", "pct": "%"})
    cg = cg[["Salarié", "Nom Prénom", "%", "Sous-Plan 1", "Sous-Plan 2"]]

    # Onglet 2 : Comète (référence), avec ses noms d'origine
    cm = comete.rename(columns={"matricule": "Matricule", "agence": "ID_Agence",
                                "activite": "ID_Activité", "pct": "%"})
    cm = cm[["Matricule", "%", "ID_Agence", "ID_Activité"]]

    # Onglet 3 : comparaison (étapes 3 et 4)
    comp = comparaison.rename(columns={
        "matricule": "MATRICULE", "agence": "SS1", "activite": "SS2",
        "pct_cegid": "% Cegid", "pct_comete": "% Comète",
        "matricule_ok": "Matricule OK", "pct_ok": "% OK",
        "type_erreur": "Type d'erreur"})
    comp = comp[["MATRICULE", "SS1", "SS2", "% Comète", "% Cegid",
                 "Matricule OK", "% OK", "Type d'erreur"]]

    # -----------------------------------------------------------------
    #  Écriture du classeur de sortie
    # -----------------------------------------------------------------
    with pd.ExcelWriter(config.OUTPUT_FILE, engine="openpyxl") as w:

        # Onglet 1 : le Cegid nettoyé (en-tête vert = données de travail)
        write_sheet(w, cg, "Cegid (nettoye)", "Cegid nettoyé : à corriger",
                    "Étape 2 : matricules des agents éclatés recopiés, lignes fantômes (0 %) supprimées, pourcentages convertis de 0-100 en décimal",
                    header="vert", text_cols=["Salarié", "Nom Prénom"], pct_cols=["%"],
                    min_width=18)

        # Onglet 2 : la base Comète de référence
        write_sheet(w, cm, "Comete (reference)", "Comète : référence du mois",
                    "Base de référence pour la comparaison",
                    header="gris", text_cols=["Matricule"], pct_cols=["%"],
                    min_width=20)

        # Onglet 3 : les écarts détectés, avec les verdicts VRAI/FAUX et le type
        write_sheet(w, comp, "Erreurs détectées", "Erreurs détectées (Cegid / Comète)",
                    "Étapes 3 et 4 : facteurs Matricule et % (VRAI/FAUX), avec le type d'erreur",
                    header="gris", text_cols=["MATRICULE"],
                    pct_cols=["% Comète", "% Cegid"], min_width=20)

        # Onglet 4 : la feuille de retraitement (ce qui doit bouger, d'où vers où)
        write_sheet(w, retraitement, "Comparaison", "Comparaison : retraitements (Départ -> Arrivée)",
                    "Étape 5 : pourcentage à déplacer de Cegid (Départ) vers Comète (Arrivée)",
                    header="gris", text_cols=["MATRICULE"], pct_cols=["% déplacé"],
                    min_width=18)

        # Onglet 5 : les cas ATT (attente), à vérifier manuellement
        note_att = ("Agents affectés en ATT (attente) dans Cegid. L'attente n'existe pas dans Comète : "
                    "toujours à vérifier. "
                    "Colonne « Dans Comète ? » : Oui = déjà traité dans l'onglet Comparaison ; "
                    "Non = hors périmètre (absent de l'export du mois précédent), à réaffecter à la main.")
        write_sheet(w, cas_att, "Cas ATT (à vérifier)", "Cas ATT (attente) : à vérifier",
                    note_att, header="gris", text_cols=["MATRICULE"], pct_cols=["%"],
                    min_width=18)

    print(f"\n>> Termine. Fichier ecrit : {config.OUTPUT_FILE}")


if __name__ == "__main__":
    main()