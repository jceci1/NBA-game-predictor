import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load

# Load your dataset
df = pd.read_csv(r'C:\Users\Joseph\Downloads\archive\minimalapproach.csv')

# Separate 'wl' column from the rest of the dataset
X = df.drop('wl', axis=1)
y = df['wl']

n_runs = 100
models = []

for seed in range(n_runs):
    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)
    
    # Create and train the RandomForestClassifier
    model = RandomForestClassifier(n_estimators=107, random_state=seed)
    model.fit(X_train, y_train)
    
    # Save the model
    dump(model, f'random_forest_model_{seed}.joblib')
    models.append(model)
