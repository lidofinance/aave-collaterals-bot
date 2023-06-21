### AAVE collaterals monitoring bot

Prometheus exporter which parses borrowers data from AAVE protocol and calculate risks distribution
based on collateral to loan ratio.

#### Run

`docker compose`

- Create a `.env` file from [`.env.example`](.env.example) and fill in the required variables.
- Execute command:

```bash
docker compose up -d bot
```

`docker`

- Create a `.env` file from [`.env.example`](.env.example) and fill in the required variables.
- Build image:

```bash
docker build -t aave-bot:dev .
```

- Run container:

```bash
docker run -d -P --env-file ./.env aave-bot:dev
```

`dev`

- Expose environment variables presented at `.env.example`.
- Install dependencies via poetry:

```bash
poetry install --with=dev
```

- Execute command:

```bash
python src/main.py
```

#### Zones definition

Risk zones are defined as a ranges of collateral to loan ratios and can be found at
[`src/bot/bins.py`](./src/bot/bins.py) file.

#### The most important exposed metrics

- `{}_collateral_percentage{pair=<pair>, zone=<zone>, bin=<bin>}` is computed percent of collaterals in the given pair,
  zone and bin

#### Visualization

Pre-built grafana dashboards available in the [`grafana` ](./grafana) directory. To run locally use
[`docker-compose.yml`](./docker-compose.yml) file as a reference.

## Release flow

To create a new release:

1. Merge all changes to the `master` branch.
1. After the merge, the `Prepare release draft` action will run automatically. When the action is complete, a release
   draft is created.
1. When you need to release, go to Repo → Releases.
1. Publish the desired release draft manually by clicking the edit button - this release is now the `Latest Published`.
1. After publication, the action to create a release bump will be triggered automatically.
