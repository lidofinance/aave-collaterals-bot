### AAVE collaterals monitoring bot

Prometheus exporter, which parses borrowers' data from AAVE protocol and calculates risks distribution based on
collateral to loan ratio.

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

Risk zones are defined as ranges of collateral-to-loan ratios and can be found at [`src/bot/bins.py`](./src/bot/bins.py)
file.

#### The most important exposed metrics

- `{}_collaterals{pair=<pair>,zone=<zone>,bin=<bin>}` is the amount of the collaterals in the selected zone and bin
  nominated in a base collateral unit, e.g stMATIC
- `{}_collaterals_values{pair=<pair>,zone=<zone>,bin=<bin>}` is the value of the collaterals in a pool's base unit, e.g.
  USD

#### Visualization

Pre-built grafana dashboards available in the [`grafana` ](./grafana) directory. To run locally use
[`docker-compose.yml`](./docker-compose.yml) file as a reference.

#### Alerting

The exporter was built primarily for alerting purposes. Therefore, in the `./prometheus` directory, predefined rules and
the related tests are located. `status.rule` is created for monitoring the status of the exporter. `zones_changes.rule`
defines rules for monitoring collaterals.

docker-compose configuration allows running the setup for alerting via Alertmanager by sending alerts to Discord.
Configure webhook parameters in `./alertmanager-discord/alertmanager-discord.yml` and start the full docker-compose
stack via command `docker compose up -d`.

#### Additional networks

The bot supports fetching collaterals of the markets working on the networks that differ from Ethereum. Definitions of
markets to fetch are located in `./src/bot/worker.py`. To define the new one, follow the structure of the `Worker` class
in the file. To run the workers on the selected network, provide the node endpoint with the chain ID chosen to let the
bot determine the markets to fetch for.

## Release flow

To create a new release:

1. Merge all changes to the `master` branch.
1. After the merge, the `Prepare release draft` action will run automatically. When the action is complete, a release
   draft is created.
1. When you need to release, go to Repo → Releases.
1. Publish the desired release draft manually by clicking the edit button - this release is now the `Latest Published`.
1. After publication, the action to create a release bump will be triggered automatically.
