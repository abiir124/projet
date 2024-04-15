// script.js
document.addEventListener('DOMContentLoaded', function () {
    var taillePopulationContainer = document.getElementById('taillePopulationContainer');
    var nbrGenerationsContainer = document.getElementById('nbrGenerationsContainer');
    var tauxMutationContainer = document.getElementById('tauxMutationContainer');
    var nbrLoupsContainer = document.getElementById('nbrLoupsContainer');
    var nbrIterationsContainer = document.getElementById('nbrIterationsContainer');

    var radioButtons = document.querySelectorAll('input[name="algorithme"]');

    radioButtons.forEach(function (radioButton) {
        radioButton.addEventListener('change', function () {
            if (this.value === 'genetique') {
                // Afficher les champs spécifiques à l'algorithme génétique
                taillePopulationContainer.style.display = 'flex';
                nbrGenerationsContainer.style.display = 'flex';
                tauxMutationContainer.style.display = 'flex';
                nbrLoupsContainer.style.display = 'none';
                nbrIterationsContainer.style.display = 'none';
            } else if (this.value === 'loupsgris') {
                // Afficher les champs spécifiques à l'algorithme des loups gris
                taillePopulationContainer.style.display = 'none';
                nbrGenerationsContainer.style.display = 'none';
                tauxMutationContainer.style.display = 'none';
                nbrLoupsContainer.style.display = 'flex';
                nbrIterationsContainer.style.display = 'flex';
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Récupérer le bouton et ajouter un gestionnaire d'événements
    const commencerBtn = document.getElementById('commencerBtn');
    commencerBtn.addEventListener('click', function () {
        // Ajoutez le console.log pour vérifier si le bouton est cliqué
        console.log("Bouton Commencer cliqué");

        // Récupérer les valeurs des champs
        const capaciteBin = parseInt(document.getElementById('capacite-bin').value);
        const dimensionsObjets = JSON.parse(document.getElementById('dimensions').value).map(Number);

        // Récupérer la valeur de l'algorithme sélectionné
        const algorithmeSelectionne = document.querySelector('input[name="algorithme"]:checked').id;
        let parametres = {};

        if (algorithmeSelectionne === 'genetique') {
            parametres.taillePopulation = parseInt(document.getElementById('Taille population').value);
            parametres.nbrGenerations = parseInt(document.getElementById('Nombres générations').value);
            parametres.tauxMutation = parseFloat(document.getElementById('Taux mutation').value);
            console.log("Données envoyées au serveur :", parametres);
            console.log("Données envoyées au serveur :", dimensionsObjets);

        } else if (algorithmeSelectionne === 'loupsgris') {
            parametres.nbrLoups = parseInt(document.getElementById('Nombres loups').value);
            parametres.nbrIterations = parseInt(document.getElementById('Nombres itérations').value);
            console.log("Données envoyées au serveur :", parametres);


        } else {
            console.error('Algorithme non pris en charge.');
            return;
        }

        fetch(`/run-algorithm/${algorithmeSelectionne}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                capaciteBin: capaciteBin,
                dimensionsObjets: dimensionsObjets,
                parametres
            }),
        })

            .then(response => response.json())
            .then(resultat => {
                // Vérifier si resultat.solution existe et est un tableau
                if (resultat.solution && Array.isArray(resultat.solution)) {
                    // Afficher les résultats dans votre structure HTML
                    const nbrElement = document.querySelector('.nbr-bin span');
                    const affichage1Element = document.querySelector('.affichage1');

                    // Afficher le nombre de boîtes utilisées dans le premier bloc
                    nbrElement.textContent = `Nombre de bacs : ${resultat.nombre_boites_utilisees}`;

                    // Vous devrez personnaliser cette partie selon le format de vos résultats
                    // Par exemple, si resultat.solution contient un tableau de boîtes, vous pouvez le parcourir et l'afficher.
                    resultat.solution.forEach((boite, index) => {
                        const boiteDiv = document.createElement('div');
                        boiteDiv.textContent = `Boîte ${index + 1}: [${boite.map(objet => objet[0]).join(', ')}]`;
                        affichage1Element.appendChild(boiteDiv);
                    });

                    // Afficher la disposition des objets dans le deuxième bloc
                    const dispositionElement = document.querySelector('.disposition .affichage1 span');
                    dispositionElement.textContent = `Liste des bins : \n${JSON.stringify(resultat.solution)}`;

                    console.log(`Résultats de l'algorithme ${algorithmeSelectionne}:`, resultat);
                } else {
                    console.error('Erreur lors de la récupération des résultats de l\'algorithme. La solution n\'est pas un tableau.');
                }
            })
            .catch(error => console.error('Erreur lors de l\'appel API:', error));

    });
});



$(document).ready(function () {
    $("#enregistrer-db-btn").click(function (event) {
        event.preventDefault(); // Empêcher le comportement par défaut du lien

        // Récupérer les valeurs des champs de formulaire
        var nbrObjets = $("#nbr_objets").val();
        var capaciteBin = $("#capacite-bin").val();
        var dimensions = $("#dimensions").val();

        // Créer un objet contenant les données à envoyer
        var formData = {
            nbr_objets: nbrObjets,
            capacite_bin: capaciteBin,
            dimensions: dimensions
        };

        // Envoyer les données au serveur Flask via une requête AJAX
        $.ajax({
            type: "POST",
            url: "/enregistrer-donnees", // L'URL de la route Flask pour enregistrer les données
            data: formData, // Les données à envoyer au serveur
            success: function (response) {
                // Traiter la réponse du serveur si nécessaire
                console.log(response);
            },
            error: function (error) {
                // Gérer les erreurs
                console.error("Erreur lors de l'envoi des données :", error);
            }
        });
    });
});
