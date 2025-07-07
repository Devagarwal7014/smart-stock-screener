import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

df = pd.read_csv("stock_training_data.csv")

# Define features including technical + fundamental
features = [
    "roe", "opm", "pb", "de_ratio", "fcf", "eps_growth", "revenue_growth",
    "RSI", "50_MA", "200_MA", "Price_Momentum_30", "Volatility"
]
X = df[features]
y = df["is_undervalued"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("📊 Report:\n", classification_report(y_test, y_pred))

# Save the trained model
joblib.dump(model, "ai_model.joblib")
print("💾 Model saved as ai_model.joblib")
