"""Réglages du projet - la seule zone à modifier au besoin."""

CEGID_FILE = "data/VENTILATION DES SALARIES - CEGID.xlsx"
COMETE_FILE = "data/VENTILATION DES SALARIES - COMETE.xlsx"
OUTPUT_FILE = "data/ventilation_salaries_resultat.xlsx"

CEGID_SHEET = "Page 1"
COMETE_SHEET = "Feuil1"

# Correspondance des colonnes (la recherche ignore casse et doubles espaces)
CEGID_COLS = {
    "matricule": "Salarié",
    "nom_prenom": "Nom Prénom",
    "pct": "%",
    "agence": "Sous-Plan 1",
    "activite": "Sous-Plan 2",
}
COMETE_COLS = {
    "matricule": "Matricule",
    "pct": "%",
    "agence": "ID_Agence",
    "activite": "ID_Activité",
}