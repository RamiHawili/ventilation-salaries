"""
Configuration du projet : tous les paramètres modifiables sont réunis ici,
pour ne jamais avoir à les chercher dans le code.
"""

# Chemins des fichiers (dans le sous-dossier data/)
CEGID_FILE = "data/VENTILATION DES SALARIES - CEGID.xlsx"
COMETE_FILE = "data/VENTILATION DES SALARIES - COMETE.xlsx"
OUTPUT_FILE = "data/ventilation_salaries_resultat.xlsx"

# Onglet où lire les données dans chaque fichier
CEGID_SHEET = "Page 1"
COMETE_SHEET = "Feuil1"

# Écart de pourcentage toléré lors de la comparaison (étape 3).
# 0.005 = 0,5 point : absorbe les arrondis (33,33 x 3 = 99,99 ; 0,9999... = 1).
TOLERANCE_PCT = 0.001

# Correspondance des colonnes source vers des noms internes communs.
# La recherche des colonnes ignore la casse et les espaces multiples,
# donc "Nom  Prénom" (double espace) est bien reconnu.
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