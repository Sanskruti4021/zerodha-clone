# ML Service (experimental)

Python service that powers the Analytics dialog in the Zerodha Clone dashboard.

> Educational project. Predictions are experimental estimates based on
> historical data, not investment advice. Past performance does not
> guarantee future results.

## Setup (Windows, VS Code terminal)

Run step 1 from the repository root.

1. Create the virtual environment (skip this if `ml-service\.venv` already exists):

       python -m venv ml-service\.venv

2. Activate it, install the libraries and check the environment:

       cd ml-service
       .venv\Scripts\Activate.ps1
       python -m pip install --upgrade pip
       pip install --only-binary=numpy,pandas,scikit-learn,scipy,curl_cffi -r requirements.txt
       python src\check_environment.py

If PowerShell blocks the activation script, run
`Set-ExecutionPolicy -Scope Process RemoteSigned` in that terminal and try again.

## Status

- [x] Stage 1B: environment
- [ ] Lock file (created after the environment check passes)
- [ ] Data download, features, training, API (coming next)
