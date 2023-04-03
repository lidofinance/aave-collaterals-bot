## [1.10.1](https://github.com/lidofinance/aave-collaterals-bot/compare/1.10.0...1.10.1) (2023-04-03)


### Bug Fixes

* cover additional ContractLogicError usages ([b3d57aa](https://github.com/lidofinance/aave-collaterals-bot/commit/b3d57aa57183ed3bda572117844e77f0b5569991))



# [1.10.0](https://github.com/lidofinance/aave-collaterals-bot/compare/1.9.0...1.10.0) (2023-03-30)


### Bug Fixes

* ContractLogicError is not raised from nethermind? response ([e951b3b](https://github.com/lidofinance/aave-collaterals-bot/commit/e951b3b5e4ea2968adc067e9f0378adc25e3c924))


### Features

* support L2s ([1ba581d](https://github.com/lidofinance/aave-collaterals-bot/commit/1ba581db49263fe5acb977163431575a7df1e3e8))



# [1.9.0](https://github.com/lidofinance/aave-collaterals-bot/compare/1.8.0...1.9.0) (2023-03-09)


### Features

* add ability to parse from AAVEv3 ([#53](https://github.com/lidofinance/aave-collaterals-bot/issues/53)) ([3a99932](https://github.com/lidofinance/aave-collaterals-bot/commit/3a9993298c264950e8df60773e65b854bd601a00))



# [1.8.0](https://github.com/lidofinance/aave-collaterals-bot/compare/1.7.1...1.8.0) (2023-02-01)


### Features

* expose provider in metrics ([5a7c4a4](https://github.com/lidofinance/aave-collaterals-bot/commit/5a7c4a4dc44bf7a4599b877aadc21cabe7e9873d))



## [1.7.1](https://github.com/lidofinance/aave-collaterals-bot/compare/1.7.0...1.7.1) (2023-01-13)


### Bug Fixes

* add fallback for eth provider ([0be7534](https://github.com/lidofinance/aave-collaterals-bot/commit/0be7534ad32d4f70cd8b86c3628b1256219714b1))



# [1.7.0](https://github.com/lidofinance/aave-collaterals-bot/compare/1.6.0...1.7.0) (2022-10-14)


### Bug Fixes

* passthrough log level ([0b96ce2](https://github.com/lidofinance/aave-collaterals-bot/commit/0b96ce2adfc26a8feaaf41ee24dd334578014547))
* testnet deploy ([7bb2ccd](https://github.com/lidofinance/aave-collaterals-bot/commit/7bb2ccdd716067560d0872959b019839263b499d))
* update curl version ([49b5d54](https://github.com/lidofinance/aave-collaterals-bot/commit/49b5d54efc9eb320382906a3589ce1004904da0d))
* update Dockerfile for the latest Debian ([1ef7ff6](https://github.com/lidofinance/aave-collaterals-bot/commit/1ef7ff6dc32fb59f1a439b918db80cd3910e6bf5))
* use the given block for calculations ([87e467a](https://github.com/lidofinance/aave-collaterals-bot/commit/87e467a36191598c3c0ca19fcf5a73338f441556))


### Features

* expose collaterals value ([f88f1af](https://github.com/lidofinance/aave-collaterals-bot/commit/f88f1af97ab0296db01e847e79985cee10d702a6))
* **grafana:** update status dashboard ([bfced6c](https://github.com/lidofinance/aave-collaterals-bot/commit/bfced6c4a2e5a964393406905d527fc8773a9efc))
* **metrics:** add metric for cycle finish timestamp ([459b7ad](https://github.com/lidofinance/aave-collaterals-bot/commit/459b7adc379dd48b6ece778d97156d99db4eeae0))
* **metrics:** update status rules ([449c6f0](https://github.com/lidofinance/aave-collaterals-bot/commit/449c6f08358c416f6f0e98eb3419cd226791c237))
* parse `build-info.json` file ([97b7513](https://github.com/lidofinance/aave-collaterals-bot/commit/97b75132f04badaee18e9a0eab109da69c057185))
* **parsing:** add transfer events actors to the list of holders ([0a4d0de](https://github.com/lidofinance/aave-collaterals-bot/commit/0a4d0dec785b5573b3053e85761a22401e5c6e47))
* **parsing:** fetch astETH holders from the blockchain ([3d81bf8](https://github.com/lidofinance/aave-collaterals-bot/commit/3d81bf87f561b6ff8637afe0610526953d2b274b))



# [1.6.0](https://github.com/lidofinance/aave-collaterals-bot/compare/1.5.0...1.6.0) (2022-06-29)


### Bug Fixes

* use the given block for calculations ([6f7100b](https://github.com/lidofinance/aave-collaterals-bot/commit/6f7100b2d9e225a7c77af41b70997d4339638bcf))


### Features

* **parsing:** add transfer events actors to the list of holders ([f4a6d95](https://github.com/lidofinance/aave-collaterals-bot/commit/f4a6d95001939452071ca727cb2b0974f8350060))
* **parsing:** fetch astETH holders from the blockchain ([0f30cfb](https://github.com/lidofinance/aave-collaterals-bot/commit/0f30cfb2de02e90eb5d435a655f72708e8674e62))



# [1.5.0](https://github.com/lidofinance/aave-collaterals-bot/compare/1.4.1...1.5.0) (2022-06-28)


### Bug Fixes

* **analytics:** fix mistakes in bins definitions ([0f1d70a](https://github.com/lidofinance/aave-collaterals-bot/commit/0f1d70ab87137b5e588a14e6929ea3fa5951aa1f))
* **linters:** ts is a good name ([c6640aa](https://github.com/lidofinance/aave-collaterals-bot/commit/c6640aadd2ed6226dc1eca7382083baaa700c1df))
* **parsing:** fetch data from blockchain within the block ([96bdae7](https://github.com/lidofinance/aave-collaterals-bot/commit/96bdae7372e12abe6e7019042d6c6118ce9ca358))


### Features

* **eth:** add retryable middleware ([66291fa](https://github.com/lidofinance/aave-collaterals-bot/commit/66291fac27db698669aaa8d4645648c235f98d9e))
* **eth:** improve metrics middleware ([d25ce83](https://github.com/lidofinance/aave-collaterals-bot/commit/d25ce83175dcfe5d404266ea400bbc9daf2f11f1))
* **grafana:** add status dashboard ([3e09bca](https://github.com/lidofinance/aave-collaterals-bot/commit/3e09bca1e580e6a8e7c1ed27f5a51a723ec5df2b))
* **parser:** get coin price within the given timestamp ([d05bb43](https://github.com/lidofinance/aave-collaterals-bot/commit/d05bb4348f2d7dade6decb0421c8f24d4a25df3c))
* **parsing:** parse eth debt from blockchain ([3903ac6](https://github.com/lidofinance/aave-collaterals-bot/commit/3903ac64b055c4757233f27edbbfa5edf5e9a7d8))



## [1.4.1](https://github.com/lidofinance/aave-collaterals-bot/compare/1.4.0...1.4.1) (2022-06-20)


### Bug Fixes

* **analytics:** fix mistakes in bins definitions ([f2ec77a](https://github.com/lidofinance/aave-collaterals-bot/commit/f2ec77ad31fbc287956ad3baaf62037aaa9e301e))



# [1.4.0](https://github.com/lidofinance/aave-collaterals-bot/compare/1.3.0...1.4.0) (2022-06-13)


### Bug Fixes

* Release flow ([cbd7a49](https://github.com/lidofinance/aave-collaterals-bot/commit/cbd7a49e4319c91cdc08adcdf3e438b826ef1005))


### Features

* **metrics:** add build info metric ([3508fe6](https://github.com/lidofinance/aave-collaterals-bot/commit/3508fe61464421dc83634605e20d3358e9d6ab99))



