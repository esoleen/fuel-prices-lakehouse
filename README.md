## 📌 Contexte du projet
En France, le prix des carburants peut varier de plus de 20 centimes par litre entre deux stations à quelques kilomètres d'écart - une info publique, mise à jour en continu par le Ministèree de l'économie via [https://data.economie.gouv.fr/](https://data.economie.gouv.fr/explore/assets/prix-des-carburants-en-france-flux-instantane-v2/), mais difficilement exploitable telle quelle (format imbriqué XML->JSON, structure large avec une colonne par carburant, ruptures de stock non structurées).

Ce projet transforme ce flux brut en un modèle de données prêt pour l'analyse, capable d'alimenter un comparateur de prix, un outil d'optimisation de données pour une flotte professionnelle, ou un suivi de ruptures d'approvisionnement en temps réel. 

## 🎯 Objectifs
- Ingérer le flux brut publié par [https://data.economie.gouv.fr/](https://data.economie.gouv.fr/explore/assets/prix-des-carburants-en-france-flux-instantane-v2/) (téléchargement HTTPS, décompression gzip)
- Nettoyer et fiabiliser les données  (gestion des lignes corrompues, encodage, séparateurs)
- Désimbriquer les structures JSON contenues dans les colonnes CSV(services, prix)
- Modéliser les données en schéma en étoille (FAIT_PRIX, FAIT_RUPTURE, DIM_STATION, DIM_CARBURANT, DIM_GEO)
- Gouverner les accès et isoler les environnements dev/prod (Unity Catalog)
- Industrialiser le pipeline (modules python testables, orchestration via DAB-Databricks Asset Bundles, CI/CD)

## Dataset
### Source
- [https://data.economie.gouv.fr/](https://data.economie.gouv.fr/) - Prix des carburants en France, flux instantané V2

## 🏗️ Architecture Médaillon

![Architecture Médaillon](docs/fuel_prices_medaillon_architecture81.png)

Le pipeline suit une architecture en médaillon sur 3 couches Delta Lake, orchestrées par un job Databricks (`resources/carburant.job.yml`) :
- **Bronze** (`fuel_price_etl/notebooks/01_Bronze`) : ingestion historisée des tables brutes (`brze_*` : dim_carburant, dim_geo, dim_station, fait_prix, fait_rupture) avec ajout d'une colonne `date_ingestion` pour tracer chaque chargement.
- **Silver** (`fuel_price_etl/notebooks/02_Silver`) : nettoyage et fiabilisation des données (`slv_*`) - déduplication par clé métier, désimbrication des colonnes `service`, application des règles de qualité et d'intégrité référentielle (ex. rattachement des stations à un département existant dans `dim_geo`).
- **Gold** (`fuel_price_etl/notebooks/03_Gold`) : requêtes SQL d'agrégation (`agg_*.dbquery.ipynb`) exécutées en parallèle après le Silver - prix moyen par département, évolution des prix au niveau national, classement des stations les moins chères, taux de rupture par région.

Le module `src/carburants` (packagé via `pyproject.toml`) fournit les utilitaires Python partagés (`fuel_price_utils.py`), le notebook de contrôle qualité (`00_data_quality.ipynb`) et le point d'entrée `main.py`, montés dans le pipeline DAB (`resources/carburant_etl.pipeline.yml`).

## 📁 Architecture du projet

```
fuel-prices-lakehouse/
├── conf/
│   ├── dev.yml
│   └── prod.yaml
├── docs/
│   ├── fuel_prices_medaillon_architecture.drawio
│   └── fuel_prices_medaillon_architecture.png
├── fixtures/                       
├── fuel_price_etl/
│   ├── dlt/
│   └── notebooks/
│       ├── 01_Bronze/
│       │   └── 01_bronze_fuel_price.ipynb
│       ├── 02_Silver/
│       │   └── 02_silver_fuel_price.ipynb
│       └── 03_Gold/
│           ├── agg_classement_stations_moins_cheres.dbquery.ipynb
│           ├── agg_evolution_prix_national.dbquery.ipynb
│           ├── agg_prix_moyen_par_departement.dbquery.ipynb
│           └── agg_taux_rupture_par_region.dbquery.ipynb
├── resources/                      # Configuration des jobs et pipelines (DAB)
│   ├── carburant.job.yml
│   └── carburant_etl.pipeline.yml
├── src/
│   └── carburants/
│       ├── __init__.py
│       ├── 00_data_quality.ipynb
│       ├── fuel_price_utils.py
│       └── main.py
├── tests/
│   ├── conftest.py
│   ├── sample_taxis_test.py
│   └── unit/
├── databricks.yml
├── pyproject.toml
├── README.md
└── .gitignore
```

## ⚙️ Installation


### Déployer et exécuter le pipeline sur Databricks
```bash
databricks bundle deploy            # déploie le bundle (cible 'dev' par défaut, voir databricks.yml)
databricks bundle run carburant     # lance le job d'orchestration Bronze → Silver → Gold
```
