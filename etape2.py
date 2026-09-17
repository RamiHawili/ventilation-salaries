"""
Étape 2 : nettoyage du fichier Cegid.

  2.1 : les pourcentages, écrits de 0 à 100, sont ramenés en décimal (÷ 100).
  2.2 : les cases Salarié / Nom Prénom laissées vides par les agents éclatés
        sont remplies avec la valeur du dessus, puis les lignes fantômes
        (% à 0) sont supprimées.
"""
import pandas as pd


def clean_cegid(raw):
    """Applique les étapes 2.1 et 2.2 et renvoie le Cegid propre."""
    df = raw.copy()

    # 2.2 : recopie le matricule et le nom sur les lignes de continuation
    df["matricule"] = df["matricule"].ffill()
    df["nom_prenom"] = df["nom_prenom"].ffill()

    # 2.1 : conversion des pourcentages en décimal (virgule tolérée)
    df["pct"] = pd.to_numeric(
        df["pct"].astype(str).str.replace(",", ".", regex=False), errors="coerce"
    ) / 100.0

    # 2.2 : élimine les lignes fantômes (% nul, vide ou illisible)
    df = df[df["pct"].notna() & (df["pct"] > 0)]

    return df[["matricule", "nom_prenom", "agence", "activite", "pct"]].reset_index(drop=True)


def run(cegid_raw):
    """Exécute l'étape 2 et renvoie le Cegid nettoyé."""
    propre = clean_cegid(cegid_raw)
    print(f"   Etape 2 : {len(propre)} lignes conservees, "
          f"{propre['matricule'].nunique()} matricules")
    return propre