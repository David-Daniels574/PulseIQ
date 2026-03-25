"""
Star Rating Forecasting Service
Uses XGBoost model to predict future ratings based on city, category, current rating, and sentiment
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
import sys

logger = logging.getLogger(__name__)

# --- Custom Label Encoder Class (MUST be defined here for joblib to load the object) ---
class UnseenLabelTransformer:
    """
    Custom class to wrap LabelEncoder, ensuring robustness for unseen categorical data.
    This class must be defined here for joblib to successfully load the pickled object.
    """
    def __init__(self, encoder, unknown_label_index):
        self.encoder = encoder
        self.unknown_label_index = unknown_label_index

    def transform(self, y):
        known_labels = set(self.encoder.classes_)
        
        # Check if the UNSEEN_LABEL placeholder exists in the encoder classes.
        if '__UNSEEN_LABEL__' not in known_labels:
            # Manually extend the encoder's classes to include the placeholder 
            known_labels_list = list(self.encoder.classes_)
            if self.unknown_label_index == len(known_labels_list):
                known_labels_list.append('__UNSEEN_LABEL__')
                self.encoder.classes_ = np.array(known_labels_list)

        # Assign the placeholder label to any label not seen in the training data
        transformed_labels = [
            label if label in known_labels else '__UNSEEN_LABEL__' 
            for label in y
        ]
        
        # Now transform using the modified encoder
        return self.encoder.transform(transformed_labels)


# Inject this module into sys.modules as __main__ so pickle can find the class
# This is the key trick to make unpickling work
current_module = sys.modules[__name__]
sys.modules['__main__'] = current_module
sys.modules['__mp_main__'] = current_module

# Now import joblib after setting up module references
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'global_star_forecast.pkl')
ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'global_encoder.pkl')


def load_xgboost_model():
    """Load the trained XGBoost model from pickle file"""
    try:
        model = joblib.load(MODEL_PATH)
        logger.info(f"✅ XGBoost model loaded successfully from {MODEL_PATH}")
        return model
    except FileNotFoundError:
        logger.error(f"❌ Model file not found at {MODEL_PATH}")
        raise
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        raise


def load_encoder():
    """Load the label encoders for categorical features (returns tuple of city and category transformers)"""
    try:
        # Load using joblib - the module remapping above ensures the class is found
        encoders = joblib.load(ENCODER_PATH)
        # Expecting a tuple: (le_city_transformer, le_category_transformer)
        logger.info(f"✅ Encoders loaded successfully from {ENCODER_PATH}")
        return encoders
    except FileNotFoundError:
        logger.error(f"❌ Encoder file not found at {ENCODER_PATH}")
        raise
    except Exception as e:
        logger.error(f"❌ Error loading encoder: {e}")
        raise


def generate_rating_forecast(
    city: str,
    category: str,
    current_rating: float,
    sentiment_score: float,
    months_ahead: int = 6
) -> List[Dict[str, Any]]:
    """
    Generate star rating forecast for next N months using XGBoost model
    
    Args:
        city: City name (e.g., "San Francisco", "Mumbai")
        category: Business category (e.g., "Vegan Street Food", "Restaurant")
        current_rating: Current average rating (1.0 to 5.0)
        sentiment_score: Sentiment score from ABSA (0.0 to 1.0)
        months_ahead: Number of months to forecast (default: 6)
        
    Returns:
        List of forecast data points with month names and predicted ratings
    """
    try:
        # Load model and encoders
        model = load_xgboost_model()
        le_city_transformer, le_category_transformer = load_encoder()
        
        # Generate predictions for each month
        predictions = []
        
        # Start with current month
        current_month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        from datetime import datetime
        current_year = datetime.now().year
        current_month_idx = datetime.now().month - 1
        
        for i in range(months_ahead):
            month_idx = (current_month_idx + i) % 12
            month_name = current_month_names[month_idx]
            
            # Calculate year (handle year transitions)
            year = current_year + ((current_month_idx + i) // 12)
            month_of_year = month_idx + 1  # 1-12
            
            # Encode categorical features
            try:
                city_encoded = le_city_transformer.transform([city])[0]
                category_encoded = le_category_transformer.transform([category])[0]
            except Exception as enc_error:
                logger.warning(f"⚠️ Encoding error: {enc_error}. Using default values.")
                # Fallback: use encoded values for unknown categories
                city_encoded = 0
                category_encoded = 0
            
            # Prepare input features matching the training format:
            # ['previous_month_rating', 'previous_month_sentiment', 'review_count_monthly', 
            #  'month_of_year', 'year', 'city_encoded', 'category_encoded']
            input_data = pd.DataFrame([[
                current_rating,          # previous_month_rating
                sentiment_score,         # previous_month_sentiment
                50,                      # review_count_monthly (estimated)
                month_of_year,          # month_of_year (1-12)
                year,                   # year
                city_encoded,           # city_encoded
                category_encoded        # category_encoded
            ]], columns=[
                'previous_month_rating', 
                'previous_month_sentiment',
                'review_count_monthly',
                'month_of_year',
                'year',
                'city_encoded', 
                'category_encoded'
            ])
            
            # Generate prediction
            predicted_rating = float(model.predict(input_data)[0])  # Convert numpy to Python float
            
            # Add slight variation for future months (trend simulation)
            # You can adjust this based on your model's actual behavior
            trend_adjustment = (i * 0.02) if sentiment_score > 0.7 else (i * -0.01)
            predicted_rating = min(5.0, max(1.0, predicted_rating + trend_adjustment))
            
            predictions.append({
                'month': month_name,
                'forecast': round(float(predicted_rating), 2),  # Ensure Python float
                'actual': round(float(current_rating), 2) if i == 0 else None
            })
            
            # Update rating for next iteration (use predicted value)
            current_rating = predicted_rating
        
        logger.info(f"✅ Generated {len(predictions)} months of forecast for {city} - {category}")
        return predictions
        
    except Exception as e:
        logger.error(f"❌ Error generating forecast: {e}")
        raise


def get_forecast_summary(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics from forecast predictions
    
    Args:
        predictions: List of prediction dictionaries
        
    Returns:
        Summary statistics including trend, final rating, and change
    """
    if not predictions:
        return {}
    
    first_rating = predictions[0].get('actual') or predictions[0]['forecast']
    last_rating = predictions[-1]['forecast']
    
    rating_change = last_rating - first_rating
    percentage_change = (rating_change / first_rating) * 100
    
    trend = "improving" if rating_change > 0.05 else "declining" if rating_change < -0.05 else "stable"
    
    return {
        "current_rating": round(first_rating, 2),
        "predicted_rating": round(last_rating, 2),
        "rating_change": round(rating_change, 2),
        "percentage_change": round(percentage_change, 1),
        "trend": trend,
        "confidence": "high" if abs(rating_change) < 0.3 else "medium"
    }
