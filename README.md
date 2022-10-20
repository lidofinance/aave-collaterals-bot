### AAVE collaterals monitoring bot

Parse borrowers data from AAVE protocol and calculate risks distribution
based on collateral to loan ratio, see zones definition below.

#### Zones definition

Risk zones defined as a ranges of collateral to loan ration

##### Bin 1

AAVE users with >=80% collaterals - stETH and  >=80% debt - ETH

| Zone        | >    | <    |
|-------------|------|------|
| A           | 1.42 | ∞    |
| B+          | 1.21 | 1.42 |
| B           | 1.14 | 1.21 |
| B-          | 1.07 | 1.14 |
| C           | 1.03 | 1.07 |
| D           | 1.00 | 1.03 |
| Liquidation | 0    | 1.00 |

##### Bin 2

AAVE users with stETH collateral and >=80% debt - not ETH

| Zone        | >    | <    |
|-------------|------|------|
| A           | 2.50 | ∞    |
| B+          | 1.75 | 2.50 |
| B           | 1.50 | 1.75 |
| B-          | 1.25 | 1.50 |
| C           | 1.10 | 1.25 |
| D           | 1.00 | 1.10 |
| Liquidation | 0    | 1.00 |

##### Bin 3

All the others AAVE users with stETH collateral

| Zone        | >    | <    |
|-------------|------|------|
| A           | 2.50 | ∞    |
| B+          | 1.75 | 2.50 |
| B           | 1.50 | 1.75 |
| B-          | 1.25 | 1.50 |
| C           | 1.10 | 1.25 |
| D           | 1.00 | 1.10 |
| Liquidation | 0    | 1.00 |

#### Exposed metrics

- `{}_collateral_percentage{zone=<zone>, bin=<bin>}` is computed percent of collaterals in the given zone and bin

#### Configuration

Configure bot via the following environment variables:

- `NODE_ENDPOINT` is ETH1 endpoint
- `PARSE_INTERVAL` is a delay in seconds between API fetches
- `EXPORTER_PORT` is the port to expose metrics on
- `LOG_FORMAT` is one of {"simple", "json"}

#### Visualisation

Dashboard available [here](https://grafana-automation.lido.fi/d/wYiKGhynz/aave-bot?orgId=1).

## Release flow

To create new release:

1. Merge all changes to the `master` branch
1. Navigate to Repo => Actions
1. Run action "Prepare release" action against `master` branch
1. When action execution is finished, navigate to Repo => Pull requests
1. Find pull request named "chore(release): X.X.X" review and merge it with "Rebase and merge" (or "Squash and merge")
1. After merge release action will be triggered automatically
1. Navigate to Repo => Actions and see last actions logs for further details 