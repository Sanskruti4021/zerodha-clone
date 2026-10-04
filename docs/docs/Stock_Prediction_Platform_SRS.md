Software Requirements Specification
Zerodha-Inspired Stock Prediction Platform
Project Type: Full-Stack Web Application with Machine Learning Integration
Purpose: Integration of an ML-based stock prediction system into an existing frontend, backend, and dashboard
application.
Important: The project already contains nine manually added companies/stocks. These existing companies and their
current functionality must be preserved and used as the initial supported stock universe for ML integration.
1. Purpose
The purpose of this project is to develop a full-stack stock-market analysis and prediction platform inspired by modern
trading dashboards. The system combines stock-market data, an existing frontend, backend, dashboard, and
Machine Learning-based stock prediction.
The platform is intended for educational and analytical purposes and must not present predictions as guaranteed
financial outcomes or financial advice.
2. Existing System
Frontend: Existing user interface for stock search, stock information, charts, dashboard, watchlist, portfolio and other
implemented features.
Backend: Existing APIs, business logic, database communication and authentication where implemented.
Dashboard: Existing visualization and analytics interface.
Existing Stock Universe: Nine companies/stocks were manually added during the original Web Development
implementation. Their names, symbols, display cards, charts and existing functionality must be preserved.
Current Problem: Frontend, backend and dashboard currently need to be started manually and separately. The
project also does not yet have an integrated ML prediction pipeline.
3. Proposed System
The proposed system integrates the existing frontend, backend, dashboard and ML prediction functionality into one
maintainable architecture.
The ML component should work with the existing nine companies initially. The system should also be designed so
additional companies can be added later without rewriting the ML logic.
Primary objective: A single master launcher should start the complete application.
4. Functional Requirements
FR-01: Preserve all existing frontend functionality.
FR-02: Preserve all existing backend APIs and business logic unless a change is required for ML integration.
FR-03: Preserve the existing nine companies/stocks.
FR-04: Identify the exact names, symbols, storage mechanism and data flow of the existing nine companies before
modifying the application.
FR-05: Support ML prediction for each of the nine existing companies.
FR-06: Connect the frontend to the backend prediction API.
FR-07: Connect the backend to the ML prediction logic/service.
FR-08: Display prediction results in the existing stock/dashboard experience.
FR-09: Handle invalid symbols, missing data and ML failures gracefully.
FR-10: Provide one master startup file that launches all required services.
5. Existing Nine Companies
The nine companies are part of the existing application and must not be removed or unnecessarily replaced.
If their current prices/data are static or manually entered, preserve that data for the existing UI while keeping it
separate from historical data used for ML training.
If the existing project already uses a market-data API, reuse it where appropriate rather than introducing another
provider unnecessarily.
The final architecture should maintain a centralized and extensible representation of company name and stock
symbol where appropriate.
6. Machine Learning Module
The ML pipeline should contain: historical data collection, data cleaning, feature engineering, chronological train/test
split, model training, evaluation, model saving, model loading and prediction.
Potential features include Open, High, Low, Close, Volume, returns, moving averages, exponential moving averages,
RSI, MACD, volatility and momentum. Only features that can be obtained reliably should be used.
The initial prediction target should preferably be the next trading day's closing price or next trading day's direction
(UP/DOWN), depending on the available data and architecture.
The first implementation should use a sensible baseline model such as Random Forest, Gradient Boosting, Linear
Regression or Logistic Regression as appropriate. The model architecture must remain replaceable.
7. Time-Series Data Handling
Stock data is time-series data. The project must avoid obvious future-data leakage.
Training and testing should preferably use chronological splitting, with older observations used for training and newer
observations used for testing.
Do not randomly shuffle time-series data without a strong technical justification.
8. Model Training and Storage
The system must not retrain the model on every prediction request.
Preferred lifecycle: Train Model ® Evaluate Model ® Save Model ® Load Model ® Make Prediction.
Trained model artifacts should be stored in an appropriate ML models directory and large generated artifacts should
not be unnecessarily committed to Git.
9. Prediction API
The prediction functionality may be integrated directly into the existing backend or implemented as a lightweight ML
service if that better fits the current architecture.
Example endpoint: POST /predict.
Example request: { symbol: 'EXISTING_SYMBOL' }.
The actual API structure must be adapted to the existing backend and stock-data architecture.
10. Frontend and Dashboard Integration
ML prediction should be integrated into the existing stock details/dashboard experience rather than creating an
unrelated standalone application.
Possible displayed information includes current price, predicted price, expected direction, prediction date, model used
and relevant model-performance information.
Actual market data and ML estimates must be visually distinguishable.
Predictions must be labelled as estimates and must not be presented as guaranteed future prices.
11. Database Requirements
The existing database architecture should be preserved.
If appropriate, a minimal prediction-history structure may store symbol, prediction, prediction date, model and created
timestamp.
No unnecessary database redesign should be performed.
12. Master Application Launcher
A master entry point should be created in the project root, preferably run.py unless the existing architecture makes
another choice more appropriate.
Running python run.py should start the required frontend, backend and ML service(s) without requiring the user to
manually open multiple terminals.
The launcher should discover or use the actual ports and commands found during repository inspection, display
service URLs, report startup failures, monitor child processes and terminate them on CTRL+C.
Use relative paths. Do not hardcode machine-specific paths such as C:\Users\...
13. Configuration and Security
Use environment variables for secrets and configuration where appropriate.
Create or update .env.example.
Never commit real API keys, passwords or database credentials.
Do not expose secrets in frontend code.
Validate API inputs and configure CORS appropriately.
14. Error Handling
The application should handle invalid stock symbols, missing market data, API timeouts, missing models, prediction
failures, backend/ML service failures, invalid requests and database errors.
Users should receive understandable error messages while internal logs contain useful debugging information.
15. Performance and Maintainability
Do not retrain models for every prediction request.
Keep the ML pipeline modular so models can be changed later.
Use small, clear functions, sensible naming, limited duplication and comments only where useful.
Do not introduce unnecessary dependencies or technologies.
16. Documentation Requirements
README.md must explain project architecture, prerequisites, installation, environment variables, ML setup, model
training, running the complete project, individual service commands, API endpoints, testing, troubleshooting and ML
limitations.
Create docs/ARCHITECTURE_AUDIT.md describing the discovered frontend, backend, dashboard, database, APIs,
stock-data source, ML status and startup commands.
Create docs/ML_ARCHITECTURE.md describing data flow, feature engineering, model, training, prediction, API
communication and model storage.
17. Validation and Testing
Existing Application: Frontend, backend, dashboard, existing APIs and database functionality must continue to
work.
ML: Verify data loading, feature generation, training, evaluation, model saving/loading and prediction.
Integration: Verify Frontend ® Backend ® ML ® Prediction ® Backend ® Frontend.
Nine Companies: Test each existing company for UI visibility, existing data, symbol recognition, historical ML data,
feature generation, prediction API response and frontend display.
Master Launcher: Verify python run.py starts all required services and CTRL+C terminates child processes.
18. Final Acceptance Criteria
All existing nine companies remain available.
Existing frontend, backend and dashboard functionality remains usable.
ML prediction works for the nine supported companies.
ML model can be trained, saved and loaded.
Frontend can display predictions returned through the application architecture.
Errors are handled cleanly.
Configuration and secrets are documented safely.
One master launcher starts the complete project.
README and ML architecture documentation are complete.
Predictions are clearly described as estimates and not guaranteed financial outcomes.
19. Future Enhancements
Additional companies can be added without rewriting ML logic.
Future enhancements may include UP/DOWN classification, multiple model comparison, prediction confidence,
additional technical indicators, prediction history, backtesting, scheduled retraining and model-performance
dashboards.
20. High-Level Architecture
Existing Frontend
|
v
Existing Backend API
|
+-------------> Existing Database / Market Data
|
v
ML Prediction Layer
|
v
Trained Stock Prediction Model
|
v
Prediction Response
|
v
Existing Frontend / Dashboard
Document Note
This SRS is intended to guide integration into the existing project. It does not require a complete rewrite. Existing
architecture, technologies and nine manually added companies should be inspected first and preserved wherever
possible.