import sys
import os
sys.path.append(os.path.dirname(__file__))

from preprocessor import run_preprocessing

X_train, X_test, y_train, y_test, feature_cols = run_preprocessing(
    data_path='data/cleaned.csv',
    mode='binary',
    sample_frac=0.3,   # use 30% during dev, change to 1.0 for final run
    test_size=0.2
)


from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced',  # handles 83/17 imbalance automatically
    random_state=42,
    n_jobs=-1                 # uses all CPU cores
)
rf.fit(X_train, y_train)


from xgboost import XGBClassifier

xgb = XGBClassifier(
    n_estimators=100,
    scale_pos_weight=214858/42406,  # ratio of benign/attack from your output
    random_state=42,
    n_jobs=-1,
    eval_metric='logloss'
)
xgb.fit(X_train, y_train)

from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

for name, model in [('Random Forest', rf), ('XGBoost', xgb)]:
    y_pred = model.predict(X_test)
    print(f'\n=== {name} ===')
    print(classification_report(y_test, y_pred,
          target_names=['BENIGN', 'ATTACK']))

    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=['BENIGN', 'ATTACK'])
    disp.plot()
    plt.title(f'{name} — Confusion Matrix')
    plt.savefig(f'notebooks/{name.lower().replace(" ","_")}_cm.png', dpi=150)
    plt.show()


import pandas as pd
import matplotlib.pyplot as plt

importances = pd.Series(rf.feature_importances_, index=feature_cols)
top20 = importances.sort_values(ascending=False).head(20)

plt.figure(figsize=(10, 7))
top20.plot(kind='barh', color='steelblue')
plt.gca().invert_yaxis()
plt.title('Random Forest — Top 20 Feature Importances')
plt.xlabel('Importance score')
plt.tight_layout()
plt.savefig('notebooks/feature_importances.png', dpi=150)
plt.show()

print(top20.to_string())


import joblib, json

# Save model
joblib.dump(rf, 'models/rf_model.pkl')

# Save feature list — critical for live inference
json.dump(feature_cols, open('models/feature_list.json', 'w'), indent=2)

# Save metrics
from sklearn.metrics import f1_score, precision_score, recall_score
y_pred = rf.predict(X_test)
metrics = {
    'model'    : 'RandomForest',
    'f1'       : f1_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred),
    'recall'   : recall_score(y_test, y_pred),
    'n_estimators': 100
}
json.dump(metrics, open('models/metrics.json', 'w'), indent=2)
print('Model saved.')