import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import os

class PTSDModel:
    def __init__(self):
        # Use the absolute path to reference the model and scaler
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
        
        try:
            self.model = joblib.load(os.path.join(model_path, "linear_regression_model.pkl"))
            self.scaler = joblib.load(os.path.join(model_path, "scaler.pkl"))
            print("Pre-trained model and scaler loaded successfully.")
        except FileNotFoundError:
            print("No pre-trained model found. Please train the model first.")
            self.model = LinearRegression()
            self.scaler = StandardScaler()

    def fit(self, X_train, y_train):
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_train_scaled, y_train)

    def predict(self, input_data):
        # Input data should be scaled before making predictions
        input_scaled = self.scaler.transform(input_data)
        prediction = self.model.predict(input_scaled)
        return np.round(prediction * 100, 2)  # Convert to percentage
