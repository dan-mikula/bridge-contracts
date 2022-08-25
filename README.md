# Token Bridge Demo

This token bridge demo is built with the Brownie framework.

### Installation
```
pip install eth-brownie
```

### Usage
Rename .envexample to .env and set up your private keys and paths.

#### scripts/00_update_abi_on_frontend_and_listener.py
Takes paths specified in brownie-config.yaml and copies the abi to your frontend and listener.

#### scripts/01_deploy_contracts.py
Contains the deploy scripts. Edit main() to your needs.

### Todo
- More tests
- Deployment and interaction script code refactoring

