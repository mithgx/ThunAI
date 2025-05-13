import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Dummy dataset
X_train = np.array([
    [13.0827, 80.2707, 5000, 10, 5],  # Example: Chennai
    [13.0102, 80.2332, 8000, 20, 15],  # High-risk area
    [13.1203, 80.2002, 3000, 5, 2],   # Low-risk area
])
y_train = ["Orange", "Red", "Green"]  # Labels: risk levels

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the model
with open("location_risk_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved successfully!")