### Anchor collaterals monitoring bot

Parse borrowers data from Anchor Market and Overseer contract and 
calculate risks distribution based on collateral to loan ratio, see
zones definition below.

#### Zones definition

Risk zones defined as a ranges of collateral to loan ration

| Zone        | >    | <    |
|-------------|------|------|
| A           | 2.5  | ∞    |
| B+          | 1.75 | 2.5  |
| B           | 1.5  | 1.75 |
| B-          | 1.25 | 1.5  |
| C           | 1.1  | 1.25 |
| D           | 1.0  | 1.1  |
| Liquidation | 0    | 1.0  |

#### Exposed metrics

- `{}_collateral_percentage{zone=<zone>}` is computed percent of collaterals in the given zone
- `{}_parser_block` is current parsed block

#### Configuration

Configure bot via the following environment variables:

- `TERRA_LCD` is the URI of LCD ! `lcd.terra.dev` is **not supported** at the moment !
- `BETH_LTV_RATIO` is the ratio for bETH
- `BLUNA_LTV_RATIO` is the ratio for bLUNA
- `EXPORTER_PORT` is the port to expose metrics on

#### Visualisation

Sandbox available at the moment [here](https://grafana.testnet.fi/d/-QOYQiY7z/anchor-bot?orgId=2).
