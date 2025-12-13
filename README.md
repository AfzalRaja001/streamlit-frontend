# Gurgaon Real Estate Frontend

A lightweight Streamlit frontend that communicates with the FastAPI backend for property analytics and predictions.

**Live Demo:** [https://real-estate-frontend-latest.onrender.com/](https://real-estate-frontend-latest.onrender.com/)

**Docker Image:** [docker.io/afzal023/real-estate-frontend:latest](https://hub.docker.com/r/afzal023/real-estate-frontend)

## Features

- 💰 **Price Predictor** - AI-powered property price predictions via API
- 📊 **Analytics Module** - Interactive data visualizations and market insights
- 🏠 **Recommend Apartments** - Find similar properties and search by location
- 📈 **Price Sensitivity** - Analyze how features impact property prices

## Deployment

### Docker Deployment (Render/Cloud)

The application is containerized and available on Docker Hub.

**Pull the image:**
```bash
docker pull afzal023/real-estate-frontend:latest
```

**Run the container:**
You **must** provide the `API_URL` environment variable pointing to the deployed backend.

```bash
docker run -p 8501:8501 \
  -e API_URL="https://real-estate-fastapi-latest.onrender.com" \
  afzal023/real-estate-frontend:latest
```

**Deploying on Render:**
1. Create a new **Web Service**.
2. Select **"Deploy an existing image from a registry"**.
3. Image URL: `afzal023/real-estate-frontend:latest`
4. **Environment Variables:**
   - Key: `API_URL`
   - Value: `https://real-estate-fastapi-latest.onrender.com`

---

## Local Development

### Prerequisites

1. **FastAPI Backend** must be running (locally or remotely).
   - If running locally: `http://localhost:8000`
   - If using deployed backend: `https://real-estate-fastapi-latest.onrender.com`

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

The app prioritizes configuration in this order:
1. **Environment Variable** `API_URL` (Best for Docker/Production)
2. **Secrets File** `.streamlit/secrets.toml` (Best for Local Development)
3. **Default Fallback** (Hardcoded default)

**To run locally pointing to your deployed backend (Recommended for testing):**
Create `.streamlit/secrets.toml`:
```toml
API_URL = "https://real-estate-fastapi-latest.onrender.com"
```

### Running the App
```bash
streamlit run Home.py
```
The app will open at `http://localhost:8501`

---

## Architecture

This frontend is designed to be **lightweight and fast**:
- All heavy model computations are done on the **FastAPI backend**.
- Analytics uses pre-processed data for instant visualization.
- API calls are cached to minimize network requests.
- **Dockerized** for easy deployment anywhere.

## Project Structure

```
Streamlit Frontend/
├── Home.py                    # Main page
├── config.py                  # Configuration
├── api_client.py              # API communication utilities
├── requirements.txt           # Dependencies
├── Dockerfile                 # Docker configuration
├── .dockerignore              # Docker build exclusions
├── pages/
│   ├── 1_Price Predictor.py          # Price prediction page
│   ├── 2_Analytics Module.py         # Analytics dashboard
│   ├── 3_Recommend Appartments.py    # Recommendations page
│   └── 4_Price Sensitivity.py        # Sensitivity analysis page
└── README.md                  # This file
```
