from flask import Flask, render_template, jsonify, request
import random
from typing import List
import numpy as np
import os
import json
import sqlite3
import subprocess

app = Flask(__name__)



# Chemin relatif vers le dossier SQLite
db_folder = 'SQLITE'

# Construire le chemin complet vers le fichier mydb.db
db_path = os.path.join(os.path.dirname(__file__), db_folder, 'mydb.db')

# Fonction pour ouvrir la base de données
def ouvrir_base_de_donnees():
    try:
        # Établir une connexion à la base de données
        conn = sqlite3.connect(db_path)
        print("Base de données ouverte avec succès !")
        return conn
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ouverture de la base de données : {e}")
        return None
    
    

def best_fit_heuristic(objets, capacite_bin):
    # Tri des objets par ordre décroissant de taille
    objets_tries = sorted(objets, reverse=True)

    if not objets_tries:
        return []

    # Initialisation des bins avec le premier objet
    bins = [[objets_tries[0]]]

    # Placement des objets restants
    for objet in objets_tries[1:]:
        bin_trouve = False

        # Parcours des bins existants pour trouver le meilleur fit
        for bin in bins:
            if sum(bin) + objet <= capacite_bin:
                bin.append(objet)
                bin_trouve = True
                break

        # Création d'un nouveau bin si aucun fit n'est trouvé
        if not bin_trouve:
            bins.append([objet])

    return bins

def initialiser_population(taille_population, objets, capacite_bin):
    population = []

    for _ in range(taille_population):
        individu = best_fit_heuristic(objets, capacite_bin)
        population.append(individu)

    return population


def fitness(individu, capacite_bin):
    nombre_boites_utilisees = len([bac for bac in individu if bac])  # Nombre de bacs non vides
    return 1 / (1 + nombre_boites_utilisees)

def selection_par_roulette(population, fitness_values):
    probabilites = np.array(fitness_values) / sum(fitness_values)
    indice_selectionne = np.random.choice(range(len(population)), p=probabilites)
    return population[indice_selectionne]


def croisement(parent1, parent2):
    if len(parent1) > 1:
        point_crossover = random.randint(1, len(parent1) - 1)
        enfant = parent1[:point_crossover] + [objet for objet in parent2 if objet not in parent1[:point_crossover]]
        return enfant
    else:
        return parent1  # Si la longueur est inférieure à 2, on ne peut pas effectuer le croisement


def mutation(individu, taux_mutation):
    for i in range(len(individu)):
        if random.random() < taux_mutation:
            j = random.randint(0, len(individu) - 1)
            individu[i], individu[j] = individu[j], individu[i]
    return individu


def algorithme_genetique(objets, capacite_bin, taille_population, taux_mutation, nombre_generations):
    population = initialiser_population(taille_population, objets, capacite_bin)

    meilleure_solution = None
    nombre_boites_utilisees = 0

    for generation in range(nombre_generations):
        fitness_values = [fitness(individu, capacite_bin) for individu in population]

        nouvelle_population = []
        for _ in range(taille_population // 2):
            parent1 = selection_par_roulette(population, fitness_values)
            parent2 = selection_par_roulette(population, fitness_values)

            enfant1 = croisement(parent1, parent2)
            enfant2 = croisement(parent2, parent1)

            enfant1 = mutation(enfant1, taux_mutation)
            enfant2 = mutation(enfant2, taux_mutation)

            nouvelle_population.extend([enfant1, enfant2])

        population = nouvelle_population

        if population:
            meilleure_solution = max(population, key=lambda individu: fitness(individu, capacite_bin))
            nombre_boites_utilisees = 1 / fitness(meilleure_solution, capacite_bin) - 1
            # Faites quelque chose avec la meilleure solution et le nombre de boîtes utilisées
        else:
            # Gérez le cas où la population est vide
            print("La population est vide.")

    return meilleure_solution, nombre_boites_utilisees






def initialiser_loups(nombre_loups, dimension, capacite_maximale):
     return np.random.randint(0, capacite_maximale + 1, (nombre_loups, dimension))


def fitness_loup(loup, objets, capacite_bin):
    bins = [[] for _ in range(len(loup))]

    for objet_taille in objets:
        index_min_bin = np.argmin(loup)

        # Comparer la taille de l'objet avec la capacité restante du bin
        if objet_taille <= loup[index_min_bin]:
            bins[index_min_bin].append(objet_taille)
            loup[index_min_bin] -= objet_taille
        else:
            # Gérer le cas où la capacité restante du bin n'est pas suffisante
            # (peut être adapté selon les exigences du problème)
            index_min_bin = np.argmin([sum(bin) for bin in bins])
            bins[index_min_bin].append(objet_taille)
            loup[index_min_bin] += objet_taille

    surcapacite_totale = sum(max(0, sum(bin) - capacite_bin) for bin in bins)

    # Ajouter la liste des bacs avec leurs contenus à la valeur de fitness
    return surcapacite_totale, bins


def mise_a_jour_position(loup_alpha, loup_beta, loup_delta, a, A, C ,capacite_maximale):
    D_alpha = abs(C * loup_alpha - loup_alpha)
    D_beta = abs(C * loup_beta - loup_beta)
    D_delta = abs(C * loup_delta - loup_delta)

    nouvelle_position = (loup_alpha - a * D_alpha +
                         loup_beta - a * D_beta +
                         loup_delta - a * D_delta) / 3.0

    # Normaliser les valeurs pour rester dans l'intervalle des capacités
    nouvelle_position = np.clip(nouvelle_position, 0, capacite_maximale)

    return nouvelle_position

def algorithme_loups(objets, capacite_bin, nombre_loups, nombre_iterations):
    dimension = len(objets)
    loups = initialiser_loups(nombre_loups, dimension, capacite_bin)

    if loups.size == 0:
        # Gérer le cas où la liste de loups est vide
        return [], float('inf')  # Retourner une valeur par défaut

    meilleur_loup = loups[0]  # Initialiser avec le premier loup
    meilleur_fitness = fitness_loup(meilleur_loup, objets, capacite_bin)

    for iteration in range(nombre_iterations):
        for i in range(nombre_loups):
            fitness = fitness_loup(loups[i], objets, capacite_bin)
            alpha, beta, delta = sorted(range(len(loups)), key=lambda x: fitness_loup(loups[x], objets, capacite_bin))[:3]

            a = 2.0 - iteration * (2.0 / nombre_iterations)  # Mise à jour du coefficient d'atténuation

            nouvelle_position = mise_a_jour_position(loups[alpha], loups[beta], loups[delta], a, np.random.rand(dimension), np.random.rand(dimension),capacite_bin)
            loups[i] = nouvelle_position

        meilleur_loup = min(loups, key=lambda x: fitness_loup(x, objets, capacite_bin))
        meilleur_fitness = fitness_loup(meilleur_loup, objets, capacite_bin)[1]

    return meilleur_loup, meilleur_fitness



  # Votre route principale
@app.route('/')
def home():
    # Ajoutez cette ligne pour exécuter votre script python.py
    subprocess.Popen(["python", "python.py"], cwd=r"C:\Users\bouha\OneDrive\Bureau\Bin-packing-main\app\SQLite")

    return render_template('accueil.html')

@app.route('/index.html')
def index():
    # Ajoutez ici le code pour préparer les données nécessaires à la page index.html
    return render_template('index.html')
    
# Route pour ouvrir la base de données
@app.route('/ouvrir-base-de-donnees')
def ouvrir_base_route():
    conn = ouvrir_base_de_donnees()  # Appel de la fonction qui ouvre la base de données
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM benchmarks")
            data = cursor.fetchall()
            conn.close()

             # Ajouter une instruction d'impression pour afficher les données extraites
            print("Données extraites de la base de données :", data)
            
            return render_template('afficher_benchmarks.html', benchmarks=data)
        except Exception as e:
            return f"Erreur lors de la récupération des données : {e}"
    else:
        return "Erreur lors de l'ouverture de la base de données."
    
    # Route pour lancer l'algorithme


# Route pour lancer l'algorithme
@app.route('/run-algorithm/<algorithme>', methods=['POST'])  # Utiliser POST au lieu de GET
def run_algorithm(algorithme):
    # Récupérer les paramètres depuis la requête
    try:
      data = request.get_json()  # Obtenir les données depuis le corps de la requête
      print(f'Données reçues du client : {data}')

      capacite_bin = int(data.get('capaciteBin', 0))
      dimensions_objets = data.get('dimensionsObjets', [])
      print(f'Données reçues du client : {capacite_bin,dimensions_objets}')
      

      if algorithme == 'genetique':
        # Ajouter les paramètres spécifiques à l'algorithme génétique
        taille_population = int(data.get('parametres', {}).get('taillePopulation', 0))
        nbr_generations = int(data.get('parametres', {}).get('nbrGenerations', 0))
        taux_mutation = float(data.get('parametres', {}).get('tauxMutation', 0.0))


        parametres = {
            'capacite_bin': capacite_bin,
            'dimensions_objets': dimensions_objets,
            'taille_population': taille_population,
            'nbr_generations': nbr_generations,
            'taux_mutation': taux_mutation
                    }

        print(f'Parametres de l algo : {parametres}')
        # Appeler l'algorithme génétique avec les paramètres
        meilleure_solution_genetique, nombre_boites_utilisees_genetique = algorithme_genetique(dimensions_objets, capacite_bin, parametres['taille_population'], parametres['taux_mutation'], parametres['nbr_generations'])
        print("Résultats de l'algorithme :", meilleure_solution_genetique, nombre_boites_utilisees_genetique)
        try:
          return jsonify({"solution": meilleure_solution_genetique, "nombre_boites_utilisees": nombre_boites_utilisees_genetique})
        except Exception as e:
          print("Erreur lors de la conversion en JSON : {e}")
          return jsonify({"erreur": "Erreur lors de la conversion en JSON"}), 500

      elif algorithme == 'loupsgris':
        # Ajouter les paramètres spécifiques à l'algorithme des loups gris
        nombre_loups = int(data.get('parametres', {}).get('nbrLoups', 0))
        nombre_iterations = int(data.get('parametres', {}).get('nbrIterations', 0))

        parametres = {
        'capacite_bin': capacite_bin,
        'dimensions_objets': dimensions_objets,
        'nombre_loups': nombre_loups,
        'nombre_iterations': nombre_iterations,
                    }

        print(f'Parametres de l algo : {parametres}')
        # Appeler l'algorithme des loups gris avec les paramètres
        meilleure_solution_loups, nombre_boites_utilisees_loups = algorithme_loups(dimensions_objets, capacite_bin, parametres['nombre_loups'], parametres['nombre_iterations'])
        print("Résultats de l'algorithme :", meilleure_solution_loups, nombre_boites_utilisees_loups)
        try:
           return jsonify({
                        "solution": meilleure_solution_loups.tolist(),
                        "nombre_boites_utilisees": nombre_boites_utilisees_loups
                        })

        except Exception as e:
            print(f"Erreur lors de la conversion en JSON : {e}")
            return jsonify({"erreur": "Erreur lors de la conversion en JSON"}), 500
      else:
        # Gérer le cas où un algorithme non pris en charge est sélectionné
        return jsonify({"erreur": "Algorithme non pris en charge"}), 400

    except Exception as e:
        print(f'Erreur dans la fonction run_algorithm : {e}')
        return jsonify({"erreur": "Une erreur est survenue lors de l'exécution de l'algorithme"}), 500
    
    
@app.route('/run-algorithm2/<algorithme>', methods=['POST'])  # Utiliser POST au lieu de GET
def run_algorithm2(algorithme):
    # Récupérer les paramètres depuis la requête
    try:
        data = request.get_json()  # Obtenir les données depuis le corps de la requête
        print(f'Données reçues du client : {data}')

        capacite_bin = int(data.get('capaciteBin', 0))
        dimensions_objets = data.get('dimensionsObjets', [])
        print(f'Données reçues du client : {capacite_bin,dimensions_objets}')

        if algorithme == 'genetique':
            # Ajouter les paramètres spécifiques à l'algorithme génétique
            taille_population = int(data.get('parametres', {}).get('taillePopulation', 0))
            nbr_generations = int(data.get('parametres', {}).get('nbrGenerations', 0))
            taux_mutation = float(data.get('parametres', {}).get('tauxMutation', 0.0))

            parametres = {
                'capacite_bin': capacite_bin,
                'dimensions_objets': dimensions_objets,
                'taille_population': taille_population,
                'nbr_generations': nbr_generations,
                'taux_mutation': taux_mutation
            }

            print(f'Parametres de l algo : {parametres}')
            # Appeler l'algorithme génétique avec les paramètres
            meilleure_solution_genetique, nombre_boites_utilisees_genetique = algorithme_genetique(dimensions_objets, capacite_bin, parametres['taille_population'], parametres['taux_mutation'], parametres['nbr_generations'])
            print("Résultats de l'algorithme :", meilleure_solution_genetique, nombre_boites_utilisees_genetique)
            try:
                return jsonify({"solution": meilleure_solution_genetique, "nombre_boites_utilisees": nombre_boites_utilisees_genetique})
            except Exception as e:
                print("Erreur lors de la conversion en JSON : {e}")
                return jsonify({"erreur": "Erreur lors de la conversion en JSON"}), 500

        elif algorithme == 'loupsgris':
            # Ajouter les paramètres spécifiques à l'algorithme des loups gris
            nombre_loups = int(data.get('parametres', {}).get('nbrLoups', 0))
            nombre_iterations = int(data.get('parametres', {}).get('nbrIterations', 0))

            parametres = {
                'capacite_bin': capacite_bin,
                'dimensions_objets': dimensions_objets,
                'nombre_loups': nombre_loups,
                'nombre_iterations': nombre_iterations,
            }

            print(f'Parametres de l algo : {parametres}')
            # Appeler l'algorithme des loups gris avec les paramètres
            meilleure_solution_loups, nombre_boites_utilisees_loups = algorithme_loups(dimensions_objets, capacite_bin, parametres['nombre_loups'], parametres['nombre_iterations'])
            print("Résultats de l'algorithme :", meilleure_solution_loups, nombre_boites_utilisees_loups)
            try:
                return jsonify({
                    "solution": meilleure_solution_loups.tolist(),
                    "nombre_boites_utilisees": nombre_boites_utilisees_loups
                })

            except Exception as e:
                print(f"Erreur lors de la conversion en JSON : {e}")
                return jsonify({"erreur": "Erreur lors de la conversion en JSON"}), 500
        else:
            # Gérer le cas où un algorithme non pris en charge est sélectionné
            return jsonify({"erreur": "Algorithme non pris en charge"}), 400

    except Exception as e:
        print(f'Erreur dans la fonction run_algorithm : {e}')
        return jsonify({"erreur": "Une erreur est survenue lors de l'exécution de l'algorithme"}), 500


@app.route('/enregistrer-donnees', methods=['POST'])
def enregistrer_donnees():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nombre_objets = request.form['nbr_objets']
        capacite_bins = request.form['capacite-bin']
        taille_objets = request.form['dimensions']

        try:
    
            print("Données à enregistrer :", nombre_objets, capacite_bins, taille_objets)  # Ajout de l'instruction print
            # Établir une connexion à la base de données

            conn = sqlite3.connect('mydb.db')
            cur = conn.cursor()

            # Insérer les données dans la table benchmarks
            cur.execute("INSERT INTO benchmarks (nombre_objets, capacite_bins, taille_objets) VALUES (?, ?, ?)",
                        (nombre_objets, capacite_bins, taille_objets))

            # Valider la transaction et fermer la connexion
            conn.commit()
            conn.close()

            # Redirection vers la page d'accueil ou un message de succès
            return redirect('/')
        except Exception as e:
            # En cas d'erreur lors de l'enregistrement des données
            print(f"Erreur lors de l'enregistrement des données : {e}")
            return "Une erreur s'est produite lors de l'enregistrement des données."

    # Gérer le cas où la méthode de requête n'est pas POST
    return "Méthode de requête non autorisée."




if __name__ == '__main__':

    app.run(debug=True)

  
  



