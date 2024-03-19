from joblib import load
import numpy as np
import pandas as pd

# Load the new dataset for predictions

comment_char = '#'

df2 = pd.read_csv(
    r'C:\Users\Joseph\OneDrive\Desktop\web scraper\predictiontest.csv',
    comment=comment_char
)


# Load the models
models = [load(f'random_forest_model_{i}.joblib') for i in range(100)]

# Initialize an array to hold all prediction probabilities
all_prediction_probabilities = []

# Get prediction probabilities from each model
for model in models:
    prediction_probabilities = model.predict_proba(df2)
    all_prediction_probabilities.append(prediction_probabilities)

# Convert the list to a NumPy array for easier calculation of mean probabilities
all_prediction_probabilities = np.array(all_prediction_probabilities)

# Calculate the mean prediction probabilities across all the loaded models
mean_prediction_probabilities = np.mean(all_prediction_probabilities, axis=0)

# Assuming class '0' is loss and class '1' is win in your binary classification
loss_class_index = list(models[0].classes_).index(0) if 0 in models[0].classes_ else None
win_class_index = list(models[0].classes_).index(1) if 1 in models[0].classes_ else None

# Print the mean probabilities with labels
for i, mean_probs in enumerate(mean_prediction_probabilities):
    loss_prob = mean_probs[loss_class_index] * 100 if loss_class_index is not None else None
    win_prob = mean_probs[win_class_index] * 100 if win_class_index is not None else None
    print(f"Average Prediction {i + 1}: Loss Probability = {loss_prob:.2f}%, Win Probability = {win_prob:.2f}%")
