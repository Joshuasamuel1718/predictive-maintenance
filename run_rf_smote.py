import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. LOAD AND PREPROCESS DATA
# ==========================================
print("Loading dataset...")
df = pd.read_csv("ai4i2020 (1).csv")

# Create Target to match the expected format
df["Target"] = df["Machine failure"]

# Map Failure Type
def get_failure_type(row):
    if row["Machine failure"] == 0:
        return "No Failure"
    if row["TWF"] == 1:
        return "Tool Wear Failure"
    if row["HDF"] == 1:
        return "Heat Dissipation Failure"
    if row["PWF"] == 1:
        return "Power Failure"
    if row["OSF"] == 1:
        return "Overstrain Failure"
    if row["RNF"] == 1:
        return "Random Failures"
    return "Unknown Failure"

df["Failure Type"] = df.apply(get_failure_type, axis=1)

# Drop original individual failure flag columns and redundant columns
df.drop(["Machine failure", "TWF", "HDF", "PWF", "OSF", "RNF"], axis=1, inplace=True)
df.columns = df.columns.str.replace(r"[\[\]<]", "", regex=True)
df.drop(["UDI", "Product ID"], axis=1, inplace=True)

# Feature Engineering
df["Temp Difference"] = df["Process temperature K"] - df["Air temperature K"]
df["Power"] = df["Rotational speed rpm"] * df["Torque Nm"]
df["Strain"] = df["Tool wear min"] * df["Torque Nm"]

# Encode Type column
type_encoder = OrdinalEncoder()
df[["Type"]] = type_encoder.fit_transform(df[["Type"]])

# ==========================================
# 2. MODEL 1: BINARY CLASSIFICATION (FAILURE DETECTION)
# ==========================================
X1 = df.drop(["Target", "Failure Type"], axis=1)
y1 = df["Target"]

X1_train, X1_test, y1_train, y1_test = train_test_split(
    X1, y1, test_size=0.2, random_state=42, stratify=y1
)

# Test various SMOTE oversampling ratios to see impact on Random Forest Accuracy and F1
smote_strategies = {
    "No SMOTE": None,
    "SMOTE (ratio=0.05)": 0.05,
    "SMOTE (ratio=0.10)": 0.10,
    "SMOTE (ratio=0.25)": 0.25,
    "SMOTE (ratio=0.50)": 0.50,
    "SMOTE (ratio=1.00 - Balanced)": "auto"
}

results1 = []

print("\n" + "="*80)
print("  EVALUATING RANDOM FOREST WITH DIFFERENT SMOTE RATIOS (FAILURE DETECTION)")
print("="*80)

best_f1 = 0
best_model1 = None
best_smote_name1 = ""

for name, strategy in smote_strategies.items():
    if strategy is None:
        X_train_res, y_train_res = X1_train, y1_train
    else:
        smote = SMOTE(sampling_strategy=strategy, random_state=42)
        X_train_res, y_train_res = smote.fit_resample(X1_train, y1_train)
    
    # Train Random Forest Classifier
    rf = RandomForestClassifier(n_estimators=500, n_jobs=-1, random_state=42)
    rf.fit(X_train_res, y_train_res)
    
    # Predict and evaluate
    y_pred = rf.predict(X1_test)
    acc = accuracy_score(y1_test, y_pred)
    prec = precision_score(y1_test, y_pred)
    rec = recall_score(y1_test, y_pred)
    f1 = f1_score(y1_test, y_pred)
    
    results1.append({
        "Strategy": name,
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1-Score": f1
    })
    
    # Keep track of the model with the best F1 score
    if f1 > best_f1:
        best_f1 = f1
        best_model1 = rf
        best_smote_name1 = name

# Print Model 1 Results Table
df_results1 = pd.DataFrame(results1)
print(df_results1.to_string(index=False, formatters={
    "Accuracy": "{:.4%}".format,
    "Precision": "{:.4%}".format,
    "Recall": "{:.4%}".format,
    "F1-Score": "{:.4%}".format
}))

print("\n>>> Best Failure Detection Model: {} (F1-Score: {:.4%}, Accuracy: {:.4%})".format(
    best_smote_name1, best_f1, df_results1.loc[df_results1["Strategy"] == best_smote_name1, "Accuracy"].values[0]
))

# Save the best binary classification model
pickle.dump(best_model1, open("model1.pkl", "wb"))


# ==========================================
# 3. MODEL 2: MULTI-CLASS CLASSIFICATION (FAILURE TYPE)
# ==========================================
df_fail = df[df["Target"] == 1]
X2 = df_fail.drop(["Target", "Failure Type"], axis=1)
y2 = df_fail["Failure Type"]

failure_encoder = LabelEncoder()
y2_encoded = failure_encoder.fit_transform(y2)

X2_train, X2_test, y2_train, y2_test = train_test_split(
    X2, y2_encoded, test_size=0.2, random_state=42, stratify=y2_encoded
)

# Apply SMOTE to Failure Types to balance rare types (like Random Failures)
# Using k_neighbors=6 because the minority class has very few samples in train split
print("\n" + "="*80)
print("  EVALUATING RANDOM FOREST WITH MULTI-CLASS SMOTE (FAILURE TYPE CLASSIFICATION)")
print("="*80)

# Without SMOTE
rf2_no_smote = RandomForestClassifier(n_estimators=100, min_samples_leaf=2, min_samples_split=5, n_jobs=-1, random_state=42)
rf2_no_smote.fit(X2_train, y2_train)
y2_pred_no_smote = rf2_no_smote.predict(X2_test)

# With SMOTE
smote2 = SMOTE(k_neighbors=6, sampling_strategy='auto', random_state=42)
X2_train_res, y2_train_res = smote2.fit_resample(X2_train, y2_train)

rf2_smote = RandomForestClassifier(n_estimators=100, min_samples_leaf=2, min_samples_split=5, n_jobs=-1, random_state=42)
rf2_smote.fit(X2_train_res, y2_train_res)
y2_pred_smote = rf2_smote.predict(X2_test)

# Compare Results
results2 = [
    {
        "Strategy": "No SMOTE (Imbalanced Types)",
        "Accuracy": accuracy_score(y2_test, y2_pred_no_smote),
        "Macro Precision": precision_score(y2_test, y2_pred_no_smote, average='macro'),
        "Macro Recall": recall_score(y2_test, y2_pred_no_smote, average='macro'),
        "Macro F1-Score": f1_score(y2_test, y2_pred_no_smote, average='macro')
    },
    {
        "Strategy": "SMOTE Enabled (Balanced Types)",
        "Accuracy": accuracy_score(y2_test, y2_pred_smote),
        "Macro Precision": precision_score(y2_test, y2_pred_smote, average='macro'),
        "Macro Recall": recall_score(y2_test, y2_pred_smote, average='macro'),
        "Macro F1-Score": f1_score(y2_test, y2_pred_smote, average='macro')
    }
]

df_results2 = pd.DataFrame(results2)
print(df_results2.to_string(index=False, formatters={
    "Accuracy": "{:.4%}".format,
    "Macro Precision": "{:.4%}".format,
    "Macro Recall": "{:.4%}".format,
    "Macro F1-Score": "{:.4%}".format
}))

# Save the best model
pickle.dump(rf2_smote, open("model2.pkl", "wb"))
pickle.dump(type_encoder, open("type_encoder.pkl", "wb"))
pickle.dump(failure_encoder, open("failure_encoder.pkl", "wb"))

print("\n" + "="*80)
print("  DETAILED CLASSIFICATION REPORT FOR BEST MODELS")
print("="*80)
print("\n- FAILURE DETECTION REPORT (Binary classification):")
print(classification_report(y1_test, best_model1.predict(X1_test), target_names=["No Failure", "Failure"]))

print("\n- FAILURE TYPE REPORT (Multi-class classification):")
print(classification_report(y2_test, y2_pred_smote, target_names=failure_encoder.classes_))

print("\nAll optimal Random Forest + SMOTE models generated & saved to disk successfully!")
