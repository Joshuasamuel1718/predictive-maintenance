import pandas as pd
import pickle

from sklearn.preprocessing import OrdinalEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

# Load dataset
df = pd.read_csv("predictive_maintenance.csv")

# Drop columns
df.drop(["UDI", "Product ID"], axis=1, inplace=True)

# Encode Type
type_encoder = OrdinalEncoder()
df[["Type"]] = type_encoder.fit_transform(df[["Type"]])

# ✅ FIX: use Target (binary)
X = df.drop(["Target", "Failure Type"], axis=1)
y = df["Target"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Handle imbalance
smote = SMOTE(random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# Train model
model = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("F1 Score:", f1_score(y_test, y_pred))

# Save
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(type_encoder, open("type_encoder.pkl", "wb"))

print("✅ Model saved correctly")