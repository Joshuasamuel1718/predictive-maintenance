import pandas as pd
import pickle

from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

# ==============================
# LOAD DATA
# ==============================
df = pd.read_csv("ai4i2020 (1).csv")

# Create Target and Failure Type to match the expected format
df["Target"] = df["Machine failure"]

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

# Drop the extra one-hot encoded columns
df.drop(["Machine failure", "TWF", "HDF", "PWF", "OSF", "RNF"], axis=1, inplace=True)

# Clean column names for XGBoost
df.columns = df.columns.str.replace(r"[\[\]<]", "", regex=True)

# Drop unnecessary columns
df.drop(["UDI", "Product ID"], axis=1, inplace=True)

# ==============================
# FEATURE ENGINEERING (IMPORTANT)
# ==============================
df["Temp Difference"] = df["Process temperature K"] - df["Air temperature K"]
# Add physical rules features for AI4I dataset
df["Power"] = df["Rotational speed rpm"] * df["Torque Nm"]
df["Strain"] = df["Tool wear min"] * df["Torque Nm"]

# ==============================
# ENCODING
# ==============================
type_encoder = OrdinalEncoder()
df[["Type"]] = type_encoder.fit_transform(df[["Type"]])

# ==============================
# MODEL 1: FAILURE DETECTION
# ==============================
X1 = df.drop(["Target", "Failure Type"], axis=1)
y1 = df["Target"]

X1_train, X1_test, y1_train, y1_test = train_test_split(
    X1, y1, test_size=0.2, random_state=42, stratify=y1
)

# Apply tuned SMOTE to Model 1 training data to reduce False Negatives without increasing False Positives
smote1 = SMOTE(sampling_strategy=0.05, random_state=42)
X1_train_res, y1_train_res = smote1.fit_resample(X1_train, y1_train)

# Calculate scale_pos_weight for imbalance (re-calibrated for resampled data)
scale_pos_weight = len(y1_train_res[y1_train_res==0]) / len(y1_train_res[y1_train_res==1])

print("- Model 1 (Failure Detection) Comparison")
# Random Forest
rf_model1 = RandomForestClassifier(n_estimators=500, n_jobs=-1, random_state=42)
rf_model1.fit(X1_train_res, y1_train_res)
rf_y1_pred = rf_model1.predict(X1_test)
print(f"Random Forest -> Accuracy: {accuracy_score(y1_test, rf_y1_pred):.4f} | F1: {f1_score(y1_test, rf_y1_pred):.4f}")

# XGBoost
xgb_model1 = XGBClassifier(n_estimators=500, learning_rate=0.05, max_depth=6, scale_pos_weight=scale_pos_weight, eval_metric='logloss', random_state=42)
xgb_model1.fit(X1_train_res, y1_train_res)
xgb_y1_pred = xgb_model1.predict(X1_test)
print(f"XGBoost       -> Accuracy: {accuracy_score(y1_test, xgb_y1_pred):.4f} | F1: {f1_score(y1_test, xgb_y1_pred):.4f}")

print("\nConfusion Matrix (XGBoost):\n", confusion_matrix(y1_test, xgb_y1_pred))

# ==============================
# MODEL 2: FAILURE TYPE
# ==============================
df_fail = df[df["Target"] == 1]
X2 = df_fail.drop(["Target", "Failure Type"], axis=1)
y2 = df_fail["Failure Type"]

failure_encoder = LabelEncoder()
y2 = failure_encoder.fit_transform(y2)

X2_train, X2_test, y2_train, y2_test = train_test_split(
    X2, y2, test_size=0.2, random_state=42, stratify=y2
)

# Apply tuned multi-class SMOTE with k_neighbors=6 to handle the rare "Random Failures" class
smote2 = SMOTE(k_neighbors=6, sampling_strategy='auto', random_state=42)
X2_train_res, y2_train_res = smote2.fit_resample(X2_train, y2_train)

print("\n- Model 2 (Failure Type) Comparison")
# Random Forest
rf_model2 = RandomForestClassifier(n_estimators=100, min_samples_leaf=2, min_samples_split=5, n_jobs=-1, random_state=42)
rf_model2.fit(X2_train_res, y2_train_res)
rf_y2_pred = rf_model2.predict(X2_test)
print(f"Random Forest -> Accuracy: {accuracy_score(y2_test, rf_y2_pred):.4f} | F1 (macro): {f1_score(y2_test, rf_y2_pred, average='macro'):.4f}")

# XGBoost
xgb_model2 = XGBClassifier(n_estimators=500, learning_rate=0.05, max_depth=6, eval_metric='mlogloss', random_state=42)
xgb_model2.fit(X2_train_res, y2_train_res)
xgb_y2_pred = xgb_model2.predict(X2_test)
print(f"XGBoost       -> Accuracy: {accuracy_score(y2_test, xgb_y2_pred):.4f} | F1 (macro): {f1_score(y2_test, xgb_y2_pred, average='macro'):.4f}")

print("\nConfusion Matrix (XGBoost):\n", confusion_matrix(y2_test, xgb_y2_pred))

# ==============================
# 💾 SAVE MODELS
# ==============================
# Keeping the superior Random Forest framework over XGBoost
pickle.dump(rf_model1, open("model1.pkl", "wb"))
pickle.dump(rf_model2, open("model2.pkl", "wb"))
pickle.dump(type_encoder, open("type_encoder.pkl", "wb"))
pickle.dump(failure_encoder, open("failure_encoder.pkl", "wb"))

print("\n PERFECT MODELS GENERATED AND SAVED SUCCESSFULLY")