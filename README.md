Tourist-Hotspot-Detection-Using-Geo-Data
A machine-learning project that classifies tourist destinations based on whether they are family-friendly using Random Forest, SVM, and Logistic Regression algorithms. Includes data preprocessing, model training, evaluation, and a simple UI/Flask integration.
Tourist Destination Family-Friendliness Classification  
A Machine Learning project that predicts whether a tourist destination is **Family Friendly** or **Not Family Friendly** based on features collected from global and Indian tourism datasets.

---

## Project Overview
This project builds an intelligent ML-based system that helps travellers answer a common question:

### **“Is this destination good for families?”**

It uses real-world tourism data, trains machine learning models, and provides a prediction using a simple Flask web interface.

---

# Features
- ✔ Predicts if a tourist place is **Family Friendly**  
- ✔ ML models: **Logistic Regression**, **Random Forest**
- ✔ Clean and updated dataset for global & Indian locations  
- ✔ Flask application (`app.py`) to run predictions  
- ✔ Data cleaning, preprocessing, and model training included  
- ✔ Supports adding new destinations to improve accuracy  

---

# Project Structure
Tourist/
│── app.py # Flask web app
│── train.py # Model training script
│── liter.py # Utility functions
│── logistic_regression_model.pkl # Trained model
│── random_forest_model.pkl # Trained model
│── City.csv
│── raw_data_India.csv
│── global_tourism_spots.csv
│── global_tourism_spots_extended_final_v3.csv
│── tourist_places_dataset.csv
│── updated_tourist_places_dataset.csv
│── README.md


---

## 🧠 Machine Learning Models Used
Two models were trained to identify family-friendly places:

### **1️⃣ Logistic Regression**
- Lightweight  
- Works well with simple linear patterns

### **2️⃣ Random Forest (Best performing model)**
- Handles complex tourism data  
- Works well with non-linear features  
- Achieved highest accuracy

---

## 📊 Dataset Description
Your project uses multiple datasets:

| File | Description |
|------|-------------|
| `City.csv` | List of cities and basic attributes |
| `raw_data_India.csv` | Raw Indian tourism data |
| `global_tourism_spots.csv` | Global tourism features |
| `global_tourism_spots_extended_final_v3.csv` | Cleaned and extended dataset |
| `tourist_places_dataset.csv` | Final dataset used for training |
| `updated_tourist_places_dataset.csv` | Updated improved dataset |

---

## 🛠 Installation & Setup

### **1️⃣ Clone the repository**
```bash
git clone https://github.com/your-username/Tourist.git
cd Tourist

## Install required libraries

Create a virtual environment (recommended):

pip install virtualenv
virtualenv venv
source venv/bin/activate     # (Windows: venv\Scripts\activate)


Install dependencies:

pip install pandas numpy scikit-learn flask

▶️ How to Run the Project
Run the Flask app
python app.py


Then open your browser and go to:

http://127.0.0.1:5000/


Enter the place details → get prediction instantly.

🧩 Training the Model Again

If you want to retrain the model:

python train.py


This will:

Load the dataset

Preprocess the features

Train Logistic Regression + Random Forest

Save the new .pkl model files

📍 Google Maps Integration (Optional)

You can extend this project by adding:

Google Maps search

Displaying destination location

Auto-fetching rating, reviews, family score

Adding Places API

For now, the system only predicts based on dataset features.

🔄 System Flow Diagram
User Input → Data Preprocessing → ML Model → Prediction → Result (Family / Not Family)

📈 Example Prediction Output

Input: Theme park, high safety, family activities, clean environment

Output: ✔ Recommended for Families

Input: Night club, alcohol allowed, adult-focused activities

Output: ✖ Not Suitable for Families

🌟 Future Enhancements

Integration with Google Maps API

Adding live reviews sentiment analysis

Deploying on Heroku / Render / AWS

Adding a beautiful UI dashboard

Expanding dataset for more countries
##  Conclusion

This project demonstrates how machine learning can classify tourist destinations as family-friendly using real data and simple algorithms. The Random Forest model provides excellent accuracy, making this a reliable recommendation tool for travellers.
