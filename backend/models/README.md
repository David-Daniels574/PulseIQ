# Star Forecasting Model

This directory contains the XGBoost model for predicting star ratings.

## Setup Instructions

1. **Place your model file here:**
   ```
   growkaro_absa/models/star_forecasting_model.pkl
   ```

2. **Model Requirements:**
   - Must be a trained XGBoost model saved as a pickle file
   - Expected input features:
     - `City`: string (e.g., "San Francisco", "Mumbai")
     - `Category`: string (e.g., "Vegan Street Food", "Restaurant")
     - `Rating`: float (current rating, 1.0-5.0)
     - `Sentiment`: float (sentiment score, 0.0-1.0)
   
3. **Model Training Example:**
   ```python
   import xgboost as xgb
   import pickle
   import pandas as pd
   
   # Your training code here
   # model = xgb.XGBRegressor(...)
   # model.fit(X_train, y_train)
   
   # Save the model
   with open('star_forecasting_model.pkl', 'wb') as f:
       pickle.dump(model, f)
   ```

4. **Install Dependencies:**
   ```bash
   cd growkaro_absa
   pip install -r requirements.txt
   ```

## API Usage

Once the model is in place, the forecast endpoint will be available:

```bash
POST http://localhost:8000/forecast
```

**Request Body:**
```json
{
  "business_name": "Your Business",
  "city": "San Francisco",
  "category": "Vegan Street Food",
  "current_rating": 4.60,
  "sentiment_score": 0.92,
  "months_ahead": 6
}
```

**Response:**
```json
{
  "status": "success",
  "forecast_data": [
    {"month": "Jan", "forecast": 4.62, "actual": 4.60},
    {"month": "Feb", "forecast": 4.64, "actual": null},
    ...
  ],
  "summary": {
    "current_rating": 4.60,
    "predicted_rating": 4.75,
    "rating_change": 0.15,
    "percentage_change": 3.3,
    "trend": "improving",
    "confidence": "high"
  }
}
```

## Frontend Integration

The forecast is automatically displayed in the Market Intelligence tab of the dashboard. It uses:
- Current rating from ABSA analysis
- Sentiment score from overall sentiment
- Business category and location from user input

## Troubleshooting

If you see "Model file not found" error:
1. Verify the file is named exactly `star_forecasting_model.pkl`
2. Ensure it's in the `growkaro_absa/models/` directory
3. Check file permissions (should be readable)
4. Restart the FastAPI server after placing the file
