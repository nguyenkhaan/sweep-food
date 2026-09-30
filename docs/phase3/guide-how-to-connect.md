# GUIDE TO CONNECT TWO API SERVICES 

Backend as the front desk. The app talks to the backend. The backend checks request, asks the AI service for recommendations, then turns the AI result into a response the app can use. 

**Flow chart**: 

flowchart LR
    App["App"] -->|"POST /api/recommendations"| Backend["Backend"]
    Backend -->|"POST /api/recommend"| AI["AI service"]
    AI -->|"Ranked recipe IDs and scores"| Backend
    Backend -->|"Recipe details and rankings"| App

    1. The app sends items and preferences. The backend  route in recommendation_router.py, receives them at `POST /api/recommendations`. A pydantic request model checks the field, such as item names, quantites, household size and allergires. 
    2. The Backend prepare the AI Request, converts them iunto the AI request model. The two services have separate models so each side of the connection has a clear contact. 
    3. The HTTP client sends JSON to AI backend. Backend use `httpx.AsyncClient` to send asynchronous to the AI service 
    4. The backend checks and adapts the AI service information. 
