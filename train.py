import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
df = pd.read_csv("updated_tourist_places_dataset.csv")

# Drop unnecessary columns
df = df.drop(columns=['Google Maps Link', 'Address'])

# Define target and features
target_column = 'Family-Friendly'
X = df.drop(target_column, axis=1)
y = df[target_column]

# Encode features and target
X = pd.get_dummies(X)
le = LabelEncoder()
y = le.fit_transform(y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Logistic Regression
lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X_train, y_train)
print("Logistic Regression Accuracy:", accuracy_score(y_test, lr_model.predict(X_test)))

# Save Logistic Regression model
joblib.dump(lr_model, "logistic_regression_model.pkl")

# Support Vector Classifier
svc_model = SVC()
svc_model.fit(X_train, y_train)
print("SVC Accuracy:", accuracy_score(y_test, svc_model.predict(X_test)))

# Save SVC model
joblib.dump(svc_model, "svc_model.pkl")

# Random Forest
rf_model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
rf_model.fit(X_train, y_train)
print("Random Forest Accuracy:", accuracy_score(y_test, rf_model.predict(X_test)))

# Save Random Forest model
joblib.dump(rf_model, "random_forest_model.pkl")
