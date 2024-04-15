import sqlite3
import json
import random

# Établir une connexion à la base de données (ou la créer si elle n'existe pas)
conn = sqlite3.connect('mydb.db')

# Créer un objet curseur pour exécuter des requêtes SQL
cur = conn.cursor()



# Requête pour créer la table benchmarks
create_table_query = '''
    CREATE TABLE IF NOT EXISTS benchmarks (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        nombre_objets INTEGER,
        capacite_bins INTEGER,
        taille_objets TEXT
    )
'''

# Exécuter la requête pour créer la table
cur.execute(create_table_query)

# Requête pour supprimer toutes les lignes de la table benchmarks
cur.execute("DELETE FROM benchmarks")

# Réinitialiser la séquence d'ID après la suppression des données
cur.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='benchmarks'")


# Insérer des données dans la table benchmarks
insert_queries = [
    ("Falkenauer U", 120, 150, None),
        ("Falkenauer U", 1000, 150, None),

    ("Falkenauer T", 60, 1000, None),
        ("Falkenauer T",501, 1000, None),

    ("Scholl 1", 50, 120, None),
        ("Scholl 1", 500, 120, None),

    ("Scholl 2", 50, 1000, None),
        ("Scholl 2", 500, 1000, None),

    ("Scholl 3", 50, 100000, None),
        ("Scholl 3", 500 , 100000, None),


    

]

for insert_query in insert_queries:
    # Convertir la liste en format JSON
    taille_objets_json = json.dumps(insert_query[3])
    cur.execute("INSERT INTO benchmarks (nom, nombre_objets, capacite_bins, taille_objets) VALUES (?, ?, ?, ?)",
                (insert_query[0], insert_query[1], insert_query[2], taille_objets_json))

    # Exécuter une requête SELECT pour récupérer toutes les lignes de la table benchmarks
cur.execute("SELECT * FROM benchmarks")

# Récupérer les résultats de la requête
rows = cur.fetchall()

# Afficher les résultats
for row in rows:
    print(row)

# Valider la transaction et fermer la connexion
conn.commit()
conn.close()
