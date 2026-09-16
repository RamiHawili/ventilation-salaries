"""
ETAPE 2 du Word - Nettoyage du fichier Cegid.

  2.1  Normalisation des % : Cegid est en 0-100  ->  on divise par 100.
  2.2  Nettoyage Salarié / Nom Prénom : les cases vides des agents éclatés
       sont remplies avec la valeur du dessus (=SI(ESTVIDE...)), puis on
       supprime les lignes à 0. On répète jusqu'à ce qu'il n'y ait plus
       ni vide ni zéro.
  2.4  Coût agent : abandonné (pas de colonne montant dans les fichiers).
"""
import pandas as pd


def clean_cegid(raw):
    """Applique 2.1 et 2.2. Renvoie le Cegid propre (% en décimal)."""
    df = raw.copy()

    # 2.2 - remplir les cases vides avec la valeur du dessus
    df["matricule"] = df["matricule"].ffill()
    df["nom_prenom"] = df["nom_prenom"].ffill()

    # 2.1 - pourcentages en décimal
    df["pct"] = pd.to_numeric(
        df["pct"].astype(str).str.replace(",", ".", regex=False), errors="coerce"
    ) / 100.0

    # 2.2 - supprimer les lignes à 0 (et les matricules restés vides)
    df = df[df["pct"].notna() & (df["pct"] > 0)]
    df = df[df["matricule"].notna()]

    return df[["matricule", "nom_prenom", "agence", "activite", "pct"]].reset_index(drop=True)


def run(cegid_raw):
    """Exécute l'étape 2. Renvoie le Cegid nettoyé."""
    propre = clean_cegid(cegid_raw)
    print(f"   Etape 2 : {len(propre)} lignes conservees, "
          f"{propre['matricule'].nunique()} matricules")
    return propre