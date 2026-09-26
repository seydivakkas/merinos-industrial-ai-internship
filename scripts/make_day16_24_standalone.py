"""Make Day 16-24 notebooks 100% self-contained standalone.
Zero external file dependencies: no local mini_project imports, no external file reads, direct matplotlib plotting.
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def update_day16():
    nb_p = REPO_ROOT / "day16" / "day16_binary_classification_logistic_regression.ipynb"
    with open(nb_p, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cell0 = '''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc, precision_recall_curve, confusion_matrix, f1_score

# 1. 500 Örneklemli sentetik veri kümesi üretimi (%90 Normal, %10 Kusurlu)
np.random.seed(42)
n_normal, n_defective = 450, 50

# Normal iplik parametreleri
tension_norm = np.random.normal(400, 20, n_normal)
speed_norm = np.random.normal(800, 30, n_normal)
temp_norm = np.random.normal(70, 5, n_normal)
vib_norm = np.random.normal(2.5, 0.4, n_normal)

# Kusurlu iplik parametreleri (yüksek gerginlik ve titreşim)
tension_def = np.random.normal(480, 35, n_defective)
speed_def = np.random.normal(750, 60, n_defective)
temp_def = np.random.normal(88, 8, n_defective)
vib_def = np.random.normal(5.0, 0.8, n_defective)

X = pd.DataFrame({
    "warp_tension_cn": np.concatenate([tension_norm, tension_def]),
    "speed_rpm": np.concatenate([speed_norm, speed_def]),
    "bearing_temp_c": np.concatenate([temp_norm, temp_def]),
    "vibration_mm_s": np.concatenate([vib_norm, vib_def])
})
y = pd.Series(np.concatenate([np.zeros(n_normal, dtype=int), np.ones(n_defective, dtype=int)]))

# 2. Lojistik Regresyon Sınıflandırıcısı Eğitimi
clf = LogisticRegression(random_state=42, max_iter=1000)
clf.fit(X, y)
probs = clf.predict_proba(X)[:, 1]

# 3. 2x2 Teşhis Panelini Doğrudan Çiz
fpr, tpr, _ = roc_curve(y, probs)
roc_auc_val = auc(fpr, tpr)
prec, rec, thresholds = precision_recall_curve(y, probs)
pr_auc_val = auc(rec, prec)
cm = confusion_matrix(y, (probs >= 0.50).astype(int))

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Logistic Regression - Classification Diagnostic Panel (Day 16)", fontsize=13, fontweight="bold")

# ROC Curve
axes[0, 0].plot(fpr, tpr, color="#1f77b4", lw=2, label=f"ROC Curve (AUC = {roc_auc_val:.3f})")
axes[0, 0].plot([0, 1], [0, 1], "k--", alpha=0.5)
axes[0, 0].set_title("1. ROC Eğrisi")
axes[0, 0].set_xlabel("False Positive Rate")
axes[0, 0].set_ylabel("True Positive Rate")
axes[0, 0].legend()
axes[0, 0].grid(True, linestyle="--", alpha=0.5)

# PR Curve
axes[0, 1].plot(rec, prec, color="#2ca02c", lw=2, label=f"PR Curve (AUC = {pr_auc_val:.3f})")
axes[0, 1].set_title("2. Precision-Recall Eğrisi")
axes[0, 1].set_xlabel("Recall")
axes[0, 1].set_ylabel("Precision")
axes[0, 1].legend()
axes[0, 1].grid(True, linestyle="--", alpha=0.5)

# Confusion Matrix Heatmap
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=axes[1, 0], cbar=False)
axes[1, 0].set_title("3. Karar Matrisi (Eşik = 0.50)")
axes[1, 0].set_xlabel("Tahmin Edilen Sınıf")
axes[1, 0].set_ylabel("Gerçek Sınıf")

# Eşik Taraması
sweep_taus = np.linspace(0.1, 0.9, 17)
f1_scores = [f1_score(y, (probs >= t).astype(int), zero_division=0) for t in sweep_taus]
axes[1, 1].plot(sweep_taus, f1_scores, marker="o", color="#d62728", lw=2, label="F1-Score")
axes[1, 1].set_title("4. Eşik Değişimi & F1 Optimizasyonu")
axes[1, 1].set_xlabel("Karar Eşiği (tau)")
axes[1, 1].set_ylabel("F1 Skoru")
axes[1, 1].legend()
axes[1, 1].grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()
print(f"ROC-AUC: {roc_auc_val:.4f} | PR-AUC: {pr_auc_val:.4f}")'''

    cell1 = '''# 4. Öznitelik Katsayıları (beta_j) ve Odds Oranları (OR) Analizi
feature_names = list(X.columns)
betas = clf.coef_[0]
odds_ratios = np.exp(betas)

weights_df = pd.DataFrame({
    "feature_name": feature_names,
    "beta_coefficient": np.round(betas, 4),
    "odds_ratio": np.round(odds_ratios, 4),
    "impact_direction": ["Pozitif (Kusur Riski Artırır)" if b > 0 else "Negatif (Kusur Riski Azaltır)" for b in betas]
}).sort_values(by="odds_ratio", ascending=False)

print(f"Model Sabit Terimi (Intercept, beta_0): {clf.intercept_[0]:.4f}")
print("Öznitelik Katsayıları ve Odds Oranları Sıralaması:")
weights_df'''

    cell2 = '''# 5. Dengesiz Veri Çözümü: Ağırlıklı Lojistik Regresyon ve Maliyet Matrisi Analizi
bal_clf = LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000)
bal_clf.fit(X, y)
bal_probs = bal_clf.predict_proba(X)[:, 1]

def evaluate_cost(y_true, y_pred, cost_fn=10.0, cost_fp=1.0):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    tot_cost = fn * cost_fn + fp * cost_fp
    return rec, prec, tot_cost

rec_base, prec_base, cost_base = evaluate_cost(y, (probs >= 0.50).astype(int))
rec_bal, prec_bal, cost_bal = evaluate_cost(y, (bal_probs >= 0.50).astype(int))

print("=================== STANDART VS DENGELİ MODEL KARŞILAŞTIRMASI ===================")
print(f"Standart Model (tau=0.50) -> Recall: %{rec_base*100:.1f} | Precision: %{prec_base*100:.1f} | Maliyet: {cost_base:.1f} TL")
print(f"Dengeli Model  (tau=0.50) -> Recall: %{rec_bal*100:.1f} | Precision: %{prec_bal*100:.1f} | Maliyet: {cost_bal:.1f} TL")'''

    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    code_cells[0]['source'] = [line + '\n' for line in cell0.split('\n')]
    code_cells[1]['source'] = [line + '\n' for line in cell1.split('\n')]
    code_cells[2]['source'] = [line + '\n' for line in cell2.split('\n')]

    with open(nb_p, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 16 updated.")

def update_day17():
    nb_p = REPO_ROOT / "day17" / "day17_multiclass_defect_classification.ipynb"
    with open(nb_p, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    
    # Cell 0: imports and setup
    cell0 = '''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize

print("Çok Sınıflı Kusur Sınıflandırma Kütüphaneleri Hazır.")'''
    code_cells[0]['source'] = [line + '\n' for line in cell0.split('\n')]

    # Cell 1: data generation
    cell1 = '''# 4. 4 Sınıflı Sentetik Kusur Veri Kümesinin Üretimi ve Sınıf Dağılımı
np.random.seed(42)
n_samples = 1200

# 4 Sınıf: 0: Normal, 1: İplik Kopuşu, 2: Gerginlik Hatası, 3: Yağ Lekesi
n_each = n_samples // 4
X_0 = np.random.normal([400, 800, 70, 2.5], [15, 20, 4, 0.3], (n_each, 4))
X_1 = np.random.normal([200, 750, 72, 6.0], [25, 40, 5, 0.8], (n_each, 4))
X_2 = np.random.normal([580, 820, 85, 4.0], [30, 25, 6, 0.5], (n_each, 4))
X_3 = np.random.normal([395, 790, 95, 2.8], [15, 20, 5, 0.3], (n_each, 4))

X = np.vstack([X_0, X_1, X_2, X_3])
y = np.concatenate([np.full(n_each, i) for i in range(4)])
class_names = ["Normal", "İplik Kopuşu", "Gerginlik Hatası", "Yağ Lekesi"]

print(f"Toplam Üretilen Örnek Sayısı: {len(y)}")
for i, name in enumerate(class_names):
    print(f"  Sınıf {i} ({name}): {(y == i).sum()} örnek")'''
    code_cells[1]['source'] = [line + '\n' for line in cell1.split('\n')]

    # Cell 2: preprocessor
    cell2 = '''# 5. Veri Ön İşleme: Çok Sınıflı Tabakalı Bölümleme ve StandardScaler
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

print(f"Eğitim Seti Boyutu: {X_train_s.shape} | Test Seti Boyutu: {X_test_s.shape}")'''
    code_cells[2]['source'] = [line + '\n' for line in cell2.split('\n')]

    # Cell 3: Multinomial model
    cell3 = '''# 6. Softmax Multinomial Lojistik Regresyon Modelinin Eğitimi
multi_clf = LogisticRegression(solver="lbfgs", max_iter=1000, random_state=42)
multi_clf.fit(X_train_s, y_train)
y_pred = multi_clf.predict(X_test_s)
y_prob = multi_clf.predict_proba(X_test_s)

print("Multinomial Model Eğitildi. Test Doğruluk Skoru:", np.round(multi_clf.score(X_test_s, y_test), 4))'''
    code_cells[3]['source'] = [line + '\n' for line in cell3.split('\n')]

    # Cell 4: OvR model
    cell4 = '''# 7. One-vs-Rest (OvR) Modelinin Eğitimi
from sklearn.multiclass import OneVsRestClassifier
ovr_clf = OneVsRestClassifier(LogisticRegression(solver="liblinear", max_iter=1000, random_state=42))
ovr_clf.fit(X_train_s, y_train)
ovr_score = ovr_clf.score(X_test_s, y_test)
print("One-vs-Rest (OvR) Modeli Test Doğruluk Skoru:", np.round(ovr_score, 4))'''
    code_cells[4]['source'] = [line + '\n' for line in cell4.split('\n')]

    # Cell 5: Confusion Matrix & Metrics
    cell5 = '''# 8. 4x4 Karar Matrisi ve Sınıf Bazlı Başarım Metrikleri
print("Sınıflandırma Raporu (Multinomial Softmax):")
print(classification_report(y_test, y_pred, target_names=class_names))'''
    code_cells[5]['source'] = [line + '\n' for line in cell5.split('\n')]

    # Cell 6: Visualizer
    cell6 = '''# 9. Multiclass ROC-AUC ve 2x2 Teşhis Panelinin Çizimi
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Multiclass Defect Classification Panel (Day 17)", fontsize=13, fontweight="bold")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Purples", xticklabels=class_names, yticklabels=class_names, ax=axes[0, 0])
axes[0, 0].set_title("1. Karar Matrisi (Confusion Matrix)")
axes[0, 0].set_xlabel("Tahmin Edilen Sınıf")
axes[0, 0].set_ylabel("Gerçek Sınıf")

# Multiclass ROC curves
y_test_bin = label_binarize(y_test, classes=[0, 1, 2, 3])
for i, color in zip(range(4), ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
    roc_auc = auc(fpr, tpr)
    axes[0, 1].plot(fpr, tpr, color=color, lw=2, label=f"{class_names[i]} (AUC={roc_auc:.2f})")
axes[0, 1].plot([0, 1], [0, 1], "k--", alpha=0.5)
axes[0, 1].set_title("2. Sınıf Bazlı ROC Eğrileri")
axes[0, 1].set_xlabel("FPR")
axes[0, 1].set_ylabel("TPR")
axes[0, 1].legend(loc="lower right")

# Feature coefficients per class
feature_names = ["Gerginlik", "Hız", "Sıcaklık", "Titreşim"]
coef_df = pd.DataFrame(multi_clf.coef_, index=class_names, columns=feature_names)
sns.heatmap(coef_df, annot=True, fmt=".2f", cmap="vlag", ax=axes[1, 0])
axes[1, 0].set_title("3. Softmax Ağırlık Katsayıları (Beta)")

# Class Probability Distribution for Sample 0
axes[1, 1].bar(class_names, y_prob[0], color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
axes[1, 1].set_title("4. Örnek Numune Olasılık Dağılımı")
axes[1, 1].set_ylabel("Tahmin Olasılığı")
axes[1, 1].set_ylim(0, 1.0)

plt.tight_layout()
plt.show()
print("Multiclass Teşhis Paneli Başarıyla Çizildi.")'''
    code_cells[6]['source'] = [line + '\n' for line in cell6.split('\n')]

    with open(nb_p, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 17 updated.")

def update_day18():
    nb_p = REPO_ROOT / "day18" / "day18_decision_trees_and_random_forest.ipynb"
    with open(nb_p, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    
    cell0 = '''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

print("Ağaç ve Topluluk Öğrenmesi Kütüphaneleri Hazır.")'''
    code_cells[0]['source'] = [line + '\n' for line in cell0.split('\n')]

    cell1 = '''# 4. Sentetik Endüstriyel Veri Üretimi ve Tabakalı Bölme
np.random.seed(42)
n_samples = 1000
# 3 Özellik: çözgü gerginliği, tezgâh devri, motor sıcaklığı
X = np.random.normal([420, 810, 72], [40, 50, 8], (n_samples, 3))
# Kusur koşulu: yüksek gerginlik veya aşırı sıcaklık
y = ((X[:, 0] > 470) | (X[:, 2] > 84)).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
feature_names = ["Gerginlik (cN)", "Devir (RPM)", "Sıcaklık (°C)"]
print(f"Eğitim: {len(y_train)} | Test: {len(y_test)} | Kusur Oranı: %{y.mean()*100:.1f}")'''
    code_cells[1]['source'] = [line + '\n' for line in cell1.split('\n')]

    cell2 = '''# 5. Budanmamış Karar Ağacı Eğitimi ve Overfitting Analizi
dt_unpruned = DecisionTreeClassifier(random_state=42)
dt_unpruned.fit(X_train, y_train)

acc_train_un = dt_unpruned.score(X_train, y_train)
acc_test_un = dt_unpruned.score(X_test, y_test)
print(f"Budanmamış Ağaç -> Eğitim Doğruluk: %{acc_train_un*100:.1f} | Test Doğruluk: %{acc_test_un*100:.1f}")'''
    code_cells[2]['source'] = [line + '\n' for line in cell2.split('\n')]

    cell3 = '''# 6. Minimal Cost-Complexity Pruning (ccp_alpha) Yolu
path = dt_unpruned.cost_complexity_pruning_path(X_train, y_train)
ccp_alphas = path.ccp_alphas[::max(1, len(path.ccp_alphas)//10)]

best_tree = None
best_acc = 0.0
for alpha in ccp_alphas:
    tree = DecisionTreeClassifier(random_state=42, ccp_alpha=alpha)
    tree.fit(X_train, y_train)
    acc = tree.score(X_test, y_test)
    if acc > best_acc:
        best_acc = acc
        best_tree = tree

print(f"Budanmış Ağaç En İyi Test Başarımı: %{best_acc*100:.1f}")'''
    code_cells[3]['source'] = [line + '\n' for line in cell3.split('\n')]

    cell4 = '''# 7. Random Forest Topluluk Modeli Eğitimi ve OOB Hatası
rf = RandomForestClassifier(n_estimators=100, oob_score=True, random_state=42)
rf.fit(X_train, y_train)
rf_test_acc = rf.score(X_test, y_test)
print(f"Random Forest Test Başarımı: %{rf_test_acc*100:.1f} | OOB Skoru: %{rf.oob_score_*100:.1f}")'''
    code_cells[4]['source'] = [line + '\n' for line in cell4.split('\n')]

    cell5 = '''# 8. Gini Saflığı vs Shannon Entropisi Kıyaslaması
dt_gini = DecisionTreeClassifier(criterion="gini", max_depth=4, random_state=42).fit(X_train, y_train)
dt_entropy = DecisionTreeClassifier(criterion="entropy", max_depth=4, random_state=42).fit(X_train, y_train)
print(f"Gini Doğruluk: %{dt_gini.score(X_test, y_test)*100:.1f} | Entropi Doğruluk: %{dt_entropy.score(X_test, y_test)*100:.1f}")'''
    code_cells[5]['source'] = [line + '\n' for line in cell5.split('\n')]

    cell6 = '''# 9. Random Forest MDI (Gini) Öznitelik Önem Dereceleri
importances = rf.feature_importances_
for name, imp in zip(feature_names, importances):
    print(f"  {name}: %{imp*100:.1f}")'''
    code_cells[6]['source'] = [line + '\n' for line in cell6.split('\n')]

    cell7 = '''# 10. Kurumsal 2x2 Model Teşhis Paneli ve Canlı Çıkarım
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Decision Tree & Random Forest Diagnostic Panel (Day 18)", fontsize=13, fontweight="bold")

# Panel 1: Pruning curve
axes[0, 0].plot(ccp_alphas, [DecisionTreeClassifier(random_state=42, ccp_alpha=a).fit(X_train, y_train).score(X_test, y_test) for a in ccp_alphas], "bo-")
axes[0, 0].set_title("1. ccp_alpha Budama Yolu")
axes[0, 0].set_xlabel("ccp_alpha")
axes[0, 0].set_ylabel("Test Doğruluğu")
axes[0, 0].grid(True, linestyle="--", alpha=0.5)

# Panel 2: Feature importances
axes[0, 1].bar(feature_names, importances, color=["#1f77b4", "#ff7f0e", "#2ca02c"])
axes[0, 1].set_title("2. Random Forest MDI Öznitelik Önemi")
axes[0, 1].set_ylabel("Önem Derecesi")

# Panel 3: OOB convergence
oob_scores = []
for n_trees in [10, 25, 50, 75, 100]:
    r = RandomForestClassifier(n_estimators=n_trees, oob_score=True, random_state=42)
    r.fit(X_train, y_train)
    oob_scores.append(r.oob_score_)
axes[1, 0].plot([10, 25, 50, 75, 100], oob_scores, "rs-")
axes[1, 0].set_title("3. Ağaç Sayısı ile OOB Yakınsaması")
axes[1, 0].set_xlabel("Ağaç Sayısı")
axes[1, 0].set_ylabel("OOB Skoru")
axes[1, 0].grid(True, linestyle="--", alpha=0.5)

# Panel 4: Test Accuracies Comparison
models = ["Tek Ağaç (Budanmamış)", "Budanmış Ağaç", "Random Forest"]
accs = [acc_test_un * 100, best_acc * 100, rf_test_acc * 100]
axes[1, 1].bar(models, accs, color=["#e41a1c", "#377eb8", "#4daf4a"])
axes[1, 1].set_title("4. Model Doğruluk Kıyaslaması")
axes[1, 1].set_ylabel("Doğruluk (%)")
axes[1, 1].set_ylim(80, 100)

plt.tight_layout()
plt.show()
print("Day 18 Teşhis Paneli Başarıyla Çizildi.")'''
    code_cells[7]['source'] = [line + '\n' for line in cell7.split('\n')]

    with open(nb_p, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 18 updated.")

def update_day19():
    nb_p = REPO_ROOT / "day19" / "day19_gradient_boosting_xgboost_lightgbm.ipynb"
    with open(nb_p, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    
    cell0 = '''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score

print("Gradient Boosting Kütüphaneleri Hazır.")'''
    code_cells[0]['source'] = [line + '\n' for line in cell0.split('\n')]

    cell1 = '''# 4. Sentetik Endüstriyel Veri Üretimi ve 3 Yönlü Bölme
np.random.seed(42)
n_samples = 1200
X = np.random.normal([410, 800, 75, 3.0], [35, 45, 7, 0.6], (n_samples, 4))
y = ((X[:, 0] > 460) | (X[:, 2] > 86) | (X[:, 3] > 4.2)).astype(int)

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)
print(f"Eğitim: {len(y_train)} | Doğrulama: {len(y_val)} | Test: {len(y_test)}")'''
    code_cells[1]['source'] = [line + '\n' for line in cell1.split('\n')]

    cell2 = '''# 5. Gradient Boosting Modeli Eğitimi ve Erken Durdurma Analizi
gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gb.fit(X_train, y_train)

val_probs = gb.predict_proba(X_val)[:, 1]
test_probs = gb.predict_proba(X_test)[:, 1]
print(f"Gradient Boosting Doğrulama AUC: {roc_auc_score(y_val, val_probs):.4f}")
print(f"Gradient Boosting Test AUC: {roc_auc_score(y_test, test_probs):.4f}")'''
    code_cells[2]['source'] = [line + '\n' for line in cell2.split('\n')]

    cell3 = '''# 6. HistGradientBoosting (Hızlı Leaf-Wise) Modeli Eğitimi
hgb = HistGradientBoostingClassifier(max_iter=100, learning_rate=0.1, max_leaf_nodes=31, random_state=42)
hgb.fit(X_train, y_train)
hgb_test_auc = roc_auc_score(y_test, hgb.predict_proba(X_test)[:, 1])
print(f"HistGradientBoosting Test AUC: {hgb_test_auc:.4f}")'''
    code_cells[3]['source'] = [line + '\n' for line in cell3.split('\n')]

    cell4 = '''# 7. Hiperparametre Grid Taraması (Öğrenme Oranı eta)
learning_rates = [0.01, 0.05, 0.1, 0.2]
lr_results = []
for lr in learning_rates:
    m = GradientBoostingClassifier(n_estimators=50, learning_rate=lr, random_state=42).fit(X_train, y_train)
    lr_results.append(roc_auc_score(y_val, m.predict_proba(X_val)[:, 1]))
print("Öğrenme Oranı Grid Sonuçları:", dict(zip(learning_rates, np.round(lr_results, 4))))'''
    code_cells[4]['source'] = [line + '\n' for line in cell4.split('\n')]

    cell5 = '''# 8. Öznitelik Önem Dereceleri
feature_names = ["Gerginlik", "Devir", "Sıcaklık", "Titreşim"]
imp = gb.feature_importances_
for name, val in zip(feature_names, imp):
    print(f"  {name}: %{val*100:.1f}")'''
    code_cells[5]['source'] = [line + '\n' for line in cell5.split('\n')]

    cell6 = '''# 9. Kurumsal 2x2 Model Teşhis Paneli Grafiğinin Çizilmesi
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Gradient Boosting Diagnostic Panel (Day 19)", fontsize=13, fontweight="bold")

# Panel 1: Stage-by-stage loss
val_losses = [roc_auc_score(y_val, p[:, 1]) for p in gb.staged_predict_proba(X_val)]
axes[0, 0].plot(range(1, len(val_losses) + 1), val_losses, color="#1f77b4", lw=2)
axes[0, 0].set_title("1. İterasyon ile Doğrulama AUC Yakınsaması")
axes[0, 0].set_xlabel("Ağaç Sayısı")
axes[0, 0].set_ylabel("AUC")
axes[0, 0].grid(True, linestyle="--", alpha=0.5)

# Panel 2: Learning rate sweep
axes[0, 1].bar([str(lr) for lr in learning_rates], lr_results, color="#2ca02c")
axes[0, 1].set_title("2. Öğrenme Oranı (Learning Rate) Duyarlılığı")
axes[0, 1].set_ylabel("Doğrulama AUC")
axes[0, 1].set_ylim(0.8, 1.0)

# Panel 3: Feature importances
axes[1, 0].barh(feature_names, imp, color="#ff7f0e")
axes[1, 0].set_title("3. Öznitelik Önem Dereceleri (Gain MDI)")
axes[1, 0].set_xlabel("Bağıl Önem")

# Panel 4: Model comparison
axes[1, 1].bar(["GradientBoosting", "HistGradientBoosting"], [roc_auc_score(y_test, test_probs), hgb_test_auc], color=["#9467bd", "#8c564b"])
axes[1, 1].set_title("4. Test Başarımı Kıyaslaması (AUC)")
axes[1, 1].set_ylim(0.8, 1.0)

plt.tight_layout()
plt.show()'''
    code_cells[6]['source'] = [line + '\n' for line in cell6.split('\n')]

    cell7 = '''# 10. Canlı Çıkarım (Inference Latency & Real-Time Defect Detection)
import time
t0 = time.perf_counter()
for _ in range(100):
    _ = gb.predict_proba(X_test[:10])
lat_ms = (time.perf_counter() - t0) / 100 * 1000
print(f"10 Numune İçin Ortalama Çıkarım Gecikmesi: {lat_ms:.3f} ms")'''
    code_cells[7]['source'] = [line + '\n' for line in cell7.split('\n')]

    with open(nb_p, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 19 updated.")

def update_day20():
    nb_p = REPO_ROOT / "day20" / "day20_support_vector_machines_svm.ipynb"
    with open(nb_p, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    
    cell0 = '''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

print("Destek Vektör Makineleri (SVM) Kütüphaneleri Hazır.")'''
    code_cells[0]['source'] = [line + '\n' for line in cell0.split('\n')]

    cell1 = '''# 4. Sentetik Endüstriyel Veri Üretimi ve StandardScaler Ölçeklemesi
np.random.seed(42)
n = 800
X = np.random.normal([400, 800], [30, 40], (n, 2))
# Non-linear dairesel karar sınırı (merkezden uzaklaşınca hata)
radius = np.sqrt(((X[:, 0] - 400)/30)**2 + ((X[:, 1] - 800)/40)**2)
y = (radius > 1.4).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)
print(f"Eğitim: {len(y_train)} | Test: {len(y_test)} | Kusur Oranı: %{y.mean()*100:.1f}")'''
    code_cells[1]['source'] = [line + '\n' for line in cell1.split('\n')]

    cell2 = '''# 5. Linear SVM Eğitimi ve Destek Vektör Analizi
svm_linear = SVC(kernel="linear", C=1.0, probability=True, random_state=42)
svm_linear.fit(X_train_s, y_train)
print(f"Linear SVM Test Başarımı: %{svm_linear.score(X_test_s, y_test)*100:.1f}")
print(f"Linear Destek Vektörü Sayısı: {len(svm_linear.support_)}")'''
    code_cells[2]['source'] = [line + '\n' for line in cell2.split('\n')]

    cell3 = '''# 6. Polynomial SVM (Cubic Degree=3) Eğitimi
svm_poly = SVC(kernel="poly", degree=3, C=1.0, probability=True, random_state=42)
svm_poly.fit(X_train_s, y_train)
print(f"Polynomial (deg=3) SVM Test Başarımı: %{svm_poly.score(X_test_s, y_test)*100:.1f}")'''
    code_cells[3]['source'] = [line + '\n' for line in cell3.split('\n')]

    cell4 = '''# 7. RBF (Gaussian) SVM Eğitimi ve Sonsuz Boyutlu Hilbert Uzayı
svm_rbf = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
svm_rbf.fit(X_train_s, y_train)
print(f"RBF (Gaussian) SVM Test Başarımı: %{svm_rbf.score(X_test_s, y_test)*100:.1f}")'''
    code_cells[4]['source'] = [line + '\n' for line in cell4.split('\n')]

    cell5 = '''# 8. C ve gamma Hiperparametre Grid Optimizasyonu
C_values = [0.1, 1.0, 10.0]
grid_scores = [SVC(kernel="rbf", C=c, gamma="scale", random_state=42).fit(X_train_s, y_train).score(X_test_s, y_test) for c in C_values]
print("C Parametresi Taraması:", dict(zip(C_values, np.round(grid_scores, 4))))'''
    code_cells[5]['source'] = [line + '\n' for line in cell5.split('\n')]

    cell6 = '''# 9. Kurumsal 2x2 Model Teşhis Paneli ve 2D Karar Sınırları
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("SVM Kernels and Decision Boundaries (Day 20)", fontsize=13, fontweight="bold")

# Grid mesh
xx, yy = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100))
grid = np.c_[xx.ravel(), yy.ravel()]

for idx, (title, model) in enumerate([("Linear", svm_linear), ("Polynomial (deg=3)", svm_poly), ("RBF (Gaussian)", svm_rbf)]):
    ax = axes[idx // 2, idx % 2]
    Z = model.predict(grid).reshape(xx.shape)
    ax.contourf(xx, yy, Z, alpha=0.3, cmap="coolwarm")
    ax.scatter(X_test_s[:, 0], X_test_s[:, 1], c=y_test, cmap="coolwarm", edgecolors="k", s=30)
    ax.set_title(f"{idx+1}. {title} Karar Sınırı")
    ax.grid(True, linestyle="--", alpha=0.3)

# Panel 4: Comparison
accs = [svm_linear.score(X_test_s, y_test)*100, svm_poly.score(X_test_s, y_test)*100, svm_rbf.score(X_test_s, y_test)*100]
axes[1, 1].bar(["Linear", "Poly (d=3)", "RBF"], accs, color=["#377eb8", "#ff7f00", "#4daf4a"])
axes[1, 1].set_title("4. Çekirdek (Kernel) Başarım Kıyaslaması")
axes[1, 1].set_ylabel("Doğruluk (%)")
axes[1, 1].set_ylim(60, 100)

plt.tight_layout()
plt.show()'''
    code_cells[6]['source'] = [line + '\n' for line in cell6.split('\n')]

    cell7 = '''# 10. Canlı Tezgâh Kusur Teşhisi ve Platt Scaling Olasılıkları
sample = np.array([[450, 850]])  # Yüksek gerginlik ve hız
sample_s = scaler.transform(sample)
prob_defect = svm_rbf.predict_proba(sample_s)[0, 1]
print(f"Numune Kusur Olasılığı (Platt Scaling): %{prob_defect*100:.1f}")'''
    code_cells[7]['source'] = [line + '\n' for line in cell7.split('\n')]

    with open(nb_p, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 20 updated.")

def update_day21():
    nb_p = REPO_ROOT / "day21" / "day21_unsupervised_learning_master_benchmark.ipynb"
    with open(nb_p, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    
    cell0 = '''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

print("Denetimsiz Öğrenme ve Kümeleme Kütüphaneleri Hazır.")'''
    code_cells[0]['source'] = [line + '\n' for line in cell0.split('\n')]

    cell1 = '''# Sentetik Endüstriyel Veri Üretimi: 1000 örnek, 30 anomali
np.random.seed(42)
n_normal, n_anomaly = 970, 30
X_norm = np.random.normal([400, 800, 70, 2.5], [15, 20, 4, 0.3], (n_normal, 4))
X_anom = np.random.normal([480, 720, 92, 5.5], [30, 40, 8, 0.8], (n_anomaly, 4))
X = np.vstack([X_norm, X_anom])
y_true = np.concatenate([np.zeros(n_normal, dtype=int), np.ones(n_anomaly, dtype=int)])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"Toplam Veri: {len(X)} | Anomali: {n_anomaly}")'''
    code_cells[1]['source'] = [line + '\n' for line in cell1.split('\n')]

    cell2 = '''# PCA Boyut İndirgeme
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)
print(f"PCA Açıklanan Varyans Oranı: PC1=%{pca.explained_variance_ratio_[0]*100:.1f}, PC2=%{pca.explained_variance_ratio_[1]*100:.1f}")'''
    code_cells[2]['source'] = [line + '\n' for line in cell2.split('\n')]

    cell3 = '''# t-SNE 2D İzdüşümü
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
X_tsne = tsne.fit_transform(X_scaled[:500])
print("t-SNE 2D İzdüşümü Tamamlandı.")'''
    code_cells[3]['source'] = [line + '\n' for line in cell3.split('\n')]

    cell4 = '''# K-Means Kümeleme ve Silhouette Skoru
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
km_labels = kmeans.fit_predict(X_scaled)
sil_km = silhouette_score(X_scaled, km_labels)
print(f"K-Means (k=3) Silhouette Skoru: {sil_km:.4f}")'''
    code_cells[4]['source'] = [line + '\n' for line in cell4.split('\n')]

    cell5 = '''# DBSCAN Yoğunluk Temelli Anomali Tespiti
dbscan = DBSCAN(eps=1.2, min_samples=10)
db_labels = dbscan.fit_predict(X_scaled)
n_noise = (db_labels == -1).sum()
print(f"DBSCAN Tespit Edilen Aykırı/Gürültü Nokta Sayısı: {n_noise}")'''
    code_cells[5]['source'] = [line + '\n' for line in cell5.split('\n')]

    cell6 = '''# 2x2 Master Denetimsiz Öğrenme Teşhis Paneli
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Unsupervised Learning Master Diagnostic Panel (Day 21)", fontsize=13, fontweight="bold")

# 1. PCA 2D
axes[0, 0].scatter(X_pca[:, 0], X_pca[:, 1], c=y_true, cmap="coolwarm", alpha=0.7, s=25)
axes[0, 0].set_title("1. PCA 2D İzdüşümü (Anomaliler)")
axes[0, 0].set_xlabel("PC1")
axes[0, 0].set_ylabel("PC2")
axes[0, 0].grid(True, linestyle="--", alpha=0.4)

# 2. t-SNE 2D
axes[0, 1].scatter(X_tsne[:, 0], X_tsne[:, 1], c=y_true[:500], cmap="viridis", alpha=0.7, s=25)
axes[0, 1].set_title("2. t-SNE Manifold İzdüşümü (500 Örnek)")
axes[0, 1].grid(True, linestyle="--", alpha=0.4)

# 3. K-Means Clusters
axes[1, 0].scatter(X_pca[:, 0], X_pca[:, 1], c=km_labels, cmap="Set1", alpha=0.7, s=25)
axes[1, 0].set_title("3. K-Means Kümeleri (k=3)")
axes[1, 0].set_xlabel("PC1")
axes[1, 0].set_ylabel("PC2")
axes[1, 0].grid(True, linestyle="--", alpha=0.4)

# 4. DBSCAN Anomaly Detection
axes[1, 1].scatter(X_pca[:, 0], X_pca[:, 1], c=(db_labels == -1), cmap="bwr", alpha=0.7, s=25)
axes[1, 1].set_title(f"4. DBSCAN Anomalileri ({n_noise} adet aykırı)")
axes[1, 1].set_xlabel("PC1")
axes[1, 1].set_ylabel("PC2")
axes[1, 1].grid(True, linestyle="--", alpha=0.4)

plt.tight_layout()
plt.show()
print("Master Denetimsiz Öğrenme Paneli Başarıyla Çizildi.")'''
    code_cells[6]['source'] = [line + '\n' for line in cell6.split('\n')]

    # Trim any extra code cells in Day 21
    nb['cells'] = [c for c in nb['cells'] if c.get('cell_type') != 'code' or c in code_cells[:7]]

    with open(nb_p, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print("Day 21 updated.")

def update_day22_24():
    # Common Merinos Technical Corpus (embedded in memory)
    embedded_corpus = '''SAMPLE_MERINOS_CORPUS = [
    {"doc_id": "DOC-001", "title": "Çözgü Gerginliği ve Atkı Kontrolü", "text": "Dokuma tezgâhlarında çözgü gerginliği sensörlerle izlenir. Gerginlik 400 cN seviyesinde tutulmalıdır."},
    {"doc_id": "DOC-002", "title": "Atkı Kopuşu ve Hata Teşhisi", "text": "Elektronik atkı sensörü kopuş algıladığında tezgâhı acil durdurur ve tepe lambasını yakar."},
    {"doc_id": "DOC-003", "title": "CIEDE2000 Renk Farkı Standardı", "text": "İplik partileri arasında renk sapması CIEDE2000 formülü ile hesaplanır. Tolerans Delta E 2.0 altıdır."},
    {"doc_id": "DOC-004", "title": "Jakarlı Halı Deseni ve Simetri", "text": "Merkez madalyon deseni çift yönlü simetriye sahip olmalıdır. Bordür paralelliği denetlenir."},
    {"doc_id": "DOC-005", "title": "Rulman Titreşimi ve Kestirimci Bakım", "text": "Ana mil rulman titreşimi 4.5 mm/s üzerinde ise aşınma başlamıştır, yağlama yapılmalıdır."},
    {"doc_id": "DOC-006", "title": "Halı Segmentasyonu ve Kusur Analizi", "text": "Yapay görme kamerası halı yüzeyindeki yağ lekesi ve desen kaymalarını klasik segmentasyon ile bulur."}
]'''

    # Day 22
    nb22_p = REPO_ROOT / "day22" / "day22_sparse_retrieval_tfidf_bm25.ipynb"
    with open(nb22_p, "r", encoding="utf-8") as f:
        nb22 = json.load(f)
    
    code_cells22 = [c for c in nb22['cells'] if c['cell_type'] == 'code']
    cell22_0 = f'''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import Counter
import math

{embedded_corpus}

def simple_tokenize(text):
    return re.findall(r"\\w+", text.lower())

print("Sparse Retrieval (TF-IDF & BM25) Kütüphaneleri ve Sentetik Külliyat Hazır.")'''
    code_cells22[0]['source'] = [line + '\n' for line in cell22_0.split('\n')]

    cell22_1 = '''# BM25 ve TF-IDF İndeksleme ve Skorlama
class StandaloneBM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.docs = [simple_tokenize(d["text"]) for d in corpus]
        self.doc_lens = [len(d) for d in self.docs]
        self.avgdl = sum(self.doc_lens) / len(self.doc_lens)
        self.df = Counter()
        for doc in self.docs:
            for term in set(doc):
                self.df[term] += 1
        self.N = len(corpus)

    def score(self, query):
        q_terms = simple_tokenize(query)
        scores = []
        for idx, doc in enumerate(self.docs):
            score = 0.0
            doc_len = self.doc_lens[idx]
            counts = Counter(doc)
            for t in q_terms:
                if t in self.df:
                    idf = math.log((self.N - self.df[t] + 0.5) / (self.df[t] + 0.5) + 1.0)
                    tf = counts[t]
                    num = tf * (self.k1 + 1)
                    denom = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                    score += idf * (num / denom)
            scores.append((self.corpus[idx]["doc_id"], self.corpus[idx]["title"], score))
        scores.sort(key=lambda x: x[2], reverse=True)
        return scores

bm25 = StandaloneBM25(SAMPLE_MERINOS_CORPUS)
query = "çözgü gerginliği ayarı"
results = bm25.score(query)
print(f"Sorgu: '{query}' için BM25 İlk 3 Sonuç:")
for doc_id, title, score in results[:3]:
    print(f"  [{doc_id}] {title} -> Skor: {score:.3f}")'''
    code_cells22[1]['source'] = [line + '\n' for line in cell22_1.split('\n')]

    cell22_2 = '''# TF-IDF vs BM25 Karşılaştırmalı Görselleştirme
titles = [r[1][:20] for r in results]
bm25_scores = [r[2] for r in results]

plt.figure(figsize=(9, 4))
plt.barh(titles, bm25_scores, color="#1f77b4")
plt.title(f"Sorgu: '{query}' için Belge BM25 Uygunluk Skorları")
plt.xlabel("BM25 Skoru")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()'''
    code_cells22[2]['source'] = [line + '\n' for line in cell22_2.split('\n')]

    nb22['cells'] = [c for c in nb22['cells'] if c.get('cell_type') != 'code' or c in code_cells22[:3]]
    with open(nb22_p, "w", encoding="utf-8") as f:
        json.dump(nb22, f, indent=2, ensure_ascii=False)
    print("Day 22 updated.")

    # Day 23: Dense Retrieval
    nb23_p = REPO_ROOT / "day23" / "day23_dense_retrieval_biencoder_crossencoder.ipynb"
    with open(nb23_p, "r", encoding="utf-8") as f:
        nb23 = json.load(f)
    code_cells23 = [c for c in nb23['cells'] if c['cell_type'] == 'code']
    
    cell23_0 = embedded_corpus + "\n\n" + """import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Dense Vektör Gösterimi Simülasyonu (TF-IDF tabanlı L2 normalize yoğun vektörler)
texts = [d["text"] for d in SAMPLE_MERINOS_CORPUS]
vec = TfidfVectorizer()
doc_embeddings = vec.fit_transform(texts).toarray()

query = "atkı kopuşu arızası"
query_vec = vec.transform([query]).toarray()
sims = cosine_similarity(query_vec, doc_embeddings)[0]

ranked = sorted(zip(SAMPLE_MERINOS_CORPUS, sims), key=lambda x: x[1], reverse=True)
print(f"Sorgu: '{query}' için Yoğun Vektör Kosinüs Benzerlikleri:")
for doc, score in ranked[:3]:
    print(f"  [{doc['doc_id']}] {doc['title']} -> Kosinüs Benzerliği: {score:.3f}")

# Görselleştirme
plt.figure(figsize=(9, 4))
plt.barh([r[0]['title'][:22] for r in ranked], [r[1] for r in ranked], color="#2ca02c")
plt.title(f"Dense Retrieval Kosinüs Benzerliği ('{query}')")
plt.xlabel("Kosinüs Benzerliği")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()"""
    code_cells23[0]['source'] = [line + '\n' for line in cell23_0.split('\n')]
    nb23['cells'] = [c for c in nb23['cells'] if c.get('cell_type') != 'code' or c in code_cells23[:1]]
    with open(nb23_p, "w", encoding="utf-8") as f:
        json.dump(nb23, f, indent=2, ensure_ascii=False)
    print("Day 23 updated.")

    # Day 24: Hybrid Retrieval RRF Fusion
    nb24_p = REPO_ROOT / "day24" / "day24_hybrid_retrieval_rrf_fusion.ipynb"
    with open(nb24_p, "r", encoding="utf-8") as f:
        nb24 = json.load(f)
    code_cells24 = [c for c in nb24['cells'] if c['cell_type'] == 'code']
    
    cell24_0 = embedded_corpus + "\n\n" + """import numpy as np
import matplotlib.pyplot as plt

# Hibrit Arama (Sparse BM25 + Dense Kosinüs) Sıralaması ve RRF Füzyonu
query = "dokuma tezgâhı motor sıcaklığı ve titreşim"

# Simüle edilmiş Sparse ve Dense sıralamaları (1-tabanlı rank)
sparse_ranks = {"DOC-005": 1, "DOC-001": 2, "DOC-002": 3, "DOC-006": 4, "DOC-004": 5, "DOC-003": 6}
dense_ranks  = {"DOC-005": 1, "DOC-002": 2, "DOC-001": 3, "DOC-004": 4, "DOC-006": 5, "DOC-003": 6}

k_rrf = 60
rrf_scores = {}
for doc_id in sparse_ranks:
    s_score = 1.0 / (k_rrf + sparse_ranks[doc_id])
    d_score = 1.0 / (k_rrf + dense_ranks[doc_id])
    rrf_scores[doc_id] = s_score + d_score

ranked_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
print(f"Sorgu: '{query}' için Hibrit RRF Füzyon Sıralaması:")
for doc_id, score in ranked_rrf:
    title = next(d['title'] for d in SAMPLE_MERINOS_CORPUS if d['doc_id'] == doc_id)
    print(f"  [{doc_id}] {title} | RRF Skoru: {score:.5f}")

# Görselleştirme
plt.figure(figsize=(9, 4))
plt.bar([r[0] for r in ranked_rrf], [r[1] for r in ranked_rrf], color="#d62728")
plt.title(f"Reciprocal Rank Fusion (RRF k=60) Hibrit Skor Dağılımı")
plt.ylabel("RRF Skoru")
plt.tight_layout()
plt.show()"""
    code_cells24[0]['source'] = [line + '\n' for line in cell24_0.split('\n')]
    nb24['cells'] = [c for c in nb24['cells'] if c.get('cell_type') != 'code' or c in code_cells24[:1]]
    with open(nb24_p, "w", encoding="utf-8") as f:
        json.dump(nb24, f, indent=2, ensure_ascii=False)
    print("Day 24 updated.")

if __name__ == "__main__":
    update_day16()
    update_day17()
    update_day18()
    update_day19()
    update_day20()
    update_day21()
    update_day22_24()
    print("Day 16-24 successfully updated.")
