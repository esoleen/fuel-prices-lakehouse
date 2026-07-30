## 📌 Contexte du projet
En France, le prix des carburants peut varier de plus de 20 centimes par litre entre deux stations à quelques kilomètres d'écart - une info publique, mise à jour en continu par le Ministèree de l'économie via [https://data.economie.gouv.fr/](https://data.economie.gouv.fr/), mais difficilement exploitable telle quelle (format imbriqué XML->JSON, structure large avec une colonne par carburant, ruptures de stock non structurées).

Ce projet transforme ce flux brut en un modèle de données prêt pour l'analyse, capable d'alimenter un comparateur de prix, un outil d'optimisation de données pour une flotte professionnelle, ou un suivi de ruptures d'approvisionnement en temps réel. 

## 🎯 Objectifs
- Ingérer le flux brut publié par [https://data.economie.gouv.fr/](https://data.economie.gouv.fr/) (téléchargement HTTPS, décompression gzip)
- Nettoyer et fiabiliser les données  (gestion des lignes corrompues, encodage, séparateurs)
- Désimbriquer les structures JSON contenues dans les colonnes CSV(services, prix)
- Modéliser les données en schéma en étoille (FAIT_PRIX, FAIT_RUPTURE, DIM_STATION, DIM_CARBURANT, DIM_GEO)
- Gouverner les accès et isoler les environnements dev/prod (Unity Catalog)
- Industrialiser le pipeline (modules python testables, orchestration via DAB-Databricks Asset Bundles, CI/CD)

## Dataset
### Source
- [https://data.economie.gouv.fr/](https://data.economie.gouv.fr/) - Prix des carburants en France, flux instantané V2

## 📁 Architecture du projet

```
project/

│
├── conf/
├── notebooks/
├── src/
│      ├── carburants/
            ├── landing
                  ├── file_downloader.py
│                 ├── job_init.py
│           ├── bronze
                 
            ├── silver
                 
            ├── gold                
│
├── tests/
├── requirements.txt
├── databricks.yml
├── README.md
└── .gitignore
