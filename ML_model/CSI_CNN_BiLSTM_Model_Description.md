# CSI-Based Human & Object Detection using CNN-BiLSTM  
## Model Description & Implementation Details
---
## 1. Introduction
This project implements a deep learning–based CSI (Channel State Information) classification system using a **CNN + BiLSTM hybrid architecture**.  
The goal of the model is to classify CSI signals into **five classes**:
- Background  
- Person  
- Car  
- Dog  
- Cow  
The model is trained and evaluated using CSI data stored in **Parquet format**, and the implementation is optimized for **GPU execution (P100 on Kaggle)**.
---
## 2. Environment Setup & Configuration
To ensure clean execution and reproducibility, multiple environment variables are configured:
- TensorFlow logs and warnings are fully suppressed  
- OneDNN, XLA, and verbose GPU logs are disabled  
- GPU memory growth is enabled  
- Deterministic execution is enforced using a fixed random seed (`SEED = 42`)  
- Mixed precision (`mixed_float16`) is enabled for faster GPU training  
This setup ensures:
- Stable training  
- Reduced console noise  
- Better GPU utilization  
---
## 3. Dataset Description
- **Training file**: `TRAIN.parquet`  
- **Testing file**: `TEST.parquet`  
Each sample contains:
- 500 time steps  
- 52 subcarriers  
Total features per sample:
```
500 × 52 = 26,000
```
The label column is automatically detected (`label`, `class`, `target`, or last column).
---
## 4. Data Validation & Loading
During loading:
- Data is read using **PyArrow**  
- NaN and Infinite values are strictly checked  
- Feature count is validated to ensure exactly **26,000 features**  
- Class distribution is printed for both training and testing sets  
This step guarantees clean and valid input data.
---
## 5. Data Preprocessing
### 5.1 Z-Score Normalization
Each CSI sample is normalized independently using Z-score normalization:
```
X_norm = (X − μ) / σ
```
This helps:
- Remove signal amplitude variations  
- Improve model convergence  
### 5.2 Reshaping
Input is reshaped into 4D tensors for CNN processing:
```
(batch_size, 500, 52, 1)
```
### 5.3 Label Encoding
Labels are converted into **one-hot vectors** for multi-class classification.
---
## 6. Model Architecture (CNN + BiLSTM)
### 6.1 CNN Feature Extraction
The CNN part extracts spatial and temporal CSI patterns:
- Conv2D layers with kernel sizes `(3×3)` and `(5×3)`  
- Batch Normalization after each convolution  
- MaxPooling layers to reduce dimensions  
- Dropout for regularization  
CNN layers progressively increase filters:
```
32 → 64 → 128
```
---
### 6.2 Reshaping for LSTM
CNN output is reshaped into a sequence format so that LSTM can process temporal dependencies.
---
### 6.3 BiLSTM Layers
Two Bidirectional LSTM layers are used:
- **BiLSTM-1**: 256 units (returns sequences)  
- **BiLSTM-2**: 128 units (returns sequences)  
A residual connection is applied between the two LSTM layers to:
- Improve gradient flow  
- Prevent performance degradation  
Layer Normalization is used after residual addition.
---
### 6.4 Classification Head
- Global Average Pooling  
- Dense layer (256 units, GELU)  
- Dropout  
- Dense layer (128 units, GELU)  
- Final Softmax output layer (5 classes)  
The output layer is forced to `float32` for numerical stability.
---
## 7. Training Strategy (Two-Phase Training)
### Phase 1: CNN Frozen
- CNN & BatchNorm layers are frozen  
- Only LSTM and dense layers are trained  
- Learning rate = `3e-4`  
- Epochs = `15`  
**Purpose:**  
Stabilize high level temporal learning first.
---
### Phase 2: CNN Unfrozen
- All CNN layers are unfrozen  
- Full network fine-tuning  
- Learning rate = `5e-5`  
- Epochs = `60`  
**Purpose:**  
Fine-tune spatial and temporal features together.
---
### Training Callbacks Used
- EarlyStopping  
- ReduceLROnPlateau  
- ModelCheckpoint (best model saved)  
---
### Loss Function
- Categorical Cross-Entropy  
- Label smoothing = `0.01`  
---
### Optimizer
- AdamW with weight decay and gradient clipping  
---
## 8. Model Evaluation
The model is evaluated using:
- Accuracy  
- Precision, Recall, F1-score  
- Confusion Matrix (count + normalized)  
**Saved Outputs:**
- `best_csi_model.keras`  
- `confusion_matrix.png`  
- `training_curves.png`  
Training curves clearly show:
- Phase-wise learning behavior  
- Reduced overfitting  
- Stable convergence  
---
## 9. Real-Time Inference Demo
A real-time demo simulates live CSI prediction:
- Normalizes each sample  
- Predicts class and confidence  
- Displays alert status (`ALERT` or `Clear`)  
- Shows prediction correctness  
This demonstrates how the model can be used in real deployment scenarios.
---
## 10. Conclusion
This project successfully demonstrates a robust CSI-based classification system using a **CNN-BiLSTM hybrid model**.  
The two-phase training strategy, mixed precision, and residual BiLSTM connections significantly improve performance and stability.
The model is suitable for:
- Human presence detection  
- Smart surveillance  
- IoT-based activity recognition  
---
