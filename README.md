# Gurgaon Real Estate Frontend

A lightweight Streamlit frontend that communicates with the FastAPI backend for property analytics and predictions.

## Features

- 💰 **Price Predictor** - AI-powered property price predictions via API
- 📊 **Analytics Module** - Interactive data visualizations and market insights
- 🏠 **Recommend Apartments** - Find similar properties and search by location
- 📈 **Price Sensitivity** - Analyze how features impact property prices

## Architecture

This frontend is designed to be **lightweight and fast**:
- All heavy computations done on the FastAPI backend
- Analytics uses pre-processed cached data for instant visualization
- API calls are cached to minimize network requests
- Clean separation of concerns between frontend and backend

## Setup

### Prerequisites

1. **FastAPI Backend** must be running:
   ```bash
   cd ../FastAPIs
   uvicorn app:app --reload
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Frontend

```bash
streamlit run Home.py
```

The app will open at `http://localhost:8501`

## Configuration

### API URL

By default, the app connects to `http://localhost:8000`

To change this, create a `.streamlit/secrets.toml` file:

```toml
API_URL = "http://your-api-url:8000"
```

Or set it in `config.py`

## Project Structure

```
Streamlit Frontend/
├── Home.py                    # Main page
├── config.py                  # Configuration
├── api_client.py              # API communication utilities
├── requirements.txt           # Dependencies
├── pages/
│   ├── 1_Price Predictor.py          # Price prediction page
│   ├── 2_Analytics Module.py         # Analytics dashboard
│   ├── 3_Recommend Appartments.py    # Recommendations page
│   └── 4_Price Sensitivity.py        # Sensitivity analysis page
└── README.md                  # This file
```

## API Endpoints Used

### Price Predictor
- `GET /options` - Get dropdown options
- `POST /predict-price` - Predict property price

### Analytics Module
- Uses cached CSV data for visualizations
- Optional API health check

### Recommend Apartments
- `GET /properties` - List all properties
- `GET /locations` - List searchable locations
- `POST /recommend` - Get property recommendations
- `POST /search-by-location` - Search by location radius

### Price Sensitivity
- `GET /options` - Get dropdown options
- `POST /predict-price` - Predict prices for sensitivity analysis

## Features Comparison

| Feature | Original Streamlit App | Frontend (API-based) |
|---------|----------------------|---------------------|
| Price Prediction | ✅ Local model | ✅ Via API |
| Analytics | ✅ Local data | ✅ Cached CSV |
| Recommendations | ✅ Local model | ✅ Via API |
| Location Search | ✅ Local data | ✅ Via API |
| Price Sensitivity | ✅ Local model | ✅ Via API |
| **Size** | Heavy (models + data) | **Lightweight (API only)** |
| **Performance** | Local compute | **Backend compute** |

## Advantages

1. **Lightweight** - No model files needed in frontend
2. **Fast** - Backend handles all heavy lifting
3. **Scalable** - Backend can be scaled independently
4. **Maintainable** - Clear separation of concerns
5. **Flexible** - Easy to swap backends or add features

## Error Handling

- Automatic API health checks
- User-friendly error messages
- Fallback to cached data when possible
- Graceful degradation if API is unavailable

## Caching Strategy

- API responses cached for 5 minutes (configurable)
- Reduces unnecessary API calls
- Improves response time
- Can be cleared with `st.cache_data.clear()`

## Development

### Adding New Features

1. Add API endpoint in FastAPI backend
2. Add client function in `api_client.py`
3. Create/update page in `pages/`
4. Update this README

### Testing

1. Start FastAPI backend
2. Run Streamlit frontend
3. Test all features
4. Check API logs for errors

## Troubleshooting

### Cannot connect to API
- Ensure FastAPI is running on `http://localhost:8000`
- Check firewall settings
- Verify API_URL in config

### Slow performance
- Check network latency
- Increase cache TTL
- Optimize API endpoints

### Missing data
- Ensure CSV files are in correct location
- Check file paths in Analytics Module
- Verify API responses

## Production Deployment

### Frontend
```bash
streamlit run Home.py --server.port 8501 --server.address 0.0.0.0
```

### Backend
Ensure FastAPI is deployed and accessible

### Environment Variables
Set `API_URL` to production backend URL

## Notes

- Analytics Module uses local CSV data for fast visualization
- All predictions and recommendations use API calls
- Session state used for UI preferences
- Responsive design for various screen sizes

## Support

For issues or questions:
1. Check FastAPI logs
2. Verify API is running
3. Check browser console for errors
4. Review Streamlit logs

---


