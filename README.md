# Animal Crossing WiFi CSI Dataset
## Introduction
This project uses the Animal Crossing WiFi CSI dataset, which is an open dataset published on Zenodo in August 2023. The dataset was released along with the research paper titled *"Detection and Classification of Animal Crossings on Roads Using IoT Based WiFi Sensing"*, submitted to IEEE LATINCOM 2023.
This repository is created as part of a **student academic project** to understand and experiment with WiFi-based sensing and machine learning techniques.
---
## Dataset Description
The dataset contains WiFi Channel State Information (CSI) amplitude data.
- Each sample contains **500 CSI frames**
- Sampling duration: **5 seconds**
- Sampling frequency: **100 Hz**
- Each frame has **52 WiFi subcarriers**
- Total features per sample: **26,000 (500 × 52)**
Only amplitude values are included in the dataset.
---
## Data Collection Setup
- **Hardware Used**: ESP32 WiFi microcontroller boards
- **Placement**:
  - Height from ground: **70 cm**
  - Distance between transmitter and receiver: **12 meters**
Data was collected in four different outdoor environments:
- Paved rural road
- Unpaved rural road
- Pasture
- Gravel road
This helps reduce environmental bias in the dataset.
---
## Preprocessing Steps
The following preprocessing steps were applied to the CSI data:
1. Non-zero amplitude values were converted to decibel (dB) scale.
2. Zero or null values were set to zero to avoid negative infinity values.
3. A running mean filter was applied to reduce noise and smooth the signal.
4. Zero-valued subcarriers were excluded from the running mean computation.
---
## Class Labels
| Label | Description |
|------:|------------|
| 0 | Background noise |
| 1 | Person |
| 2 | Car |
| 3 | Dog |
| 4 | Cow |
---
## Dataset Files
The dataset is provided in Parquet format.
- `TRAIN.parquet` – Training dataset (365.4 MB)
- `TEST.parquet` – Testing dataset (108.4 MB)
---
## How to Load the Dataset
```python
import pandas as pd
train_data = pd.read_parquet("TRAIN.parquet")
test_data = pd.read_parquet("TEST.parquet")
```
Each row represents one CSI sample along with its class label.
---
## Intended Use
This dataset can be used for:
- Machine learning classification
- Deep learning models such as CNN, LSTM, and BiLSTM
- WiFi-based sensing research
- Academic mini-projects and final-year projects
---
## License
The dataset is released under the **Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0)** license.
---
## Citation
Samuel Vieira Ducca (2023).  
Animal Crossing WiFi CSI, Version 1.0.0.  
Zenodo. DOI: 10.5281/zenodo.8266462
---
## Note
This repository is maintained **for educational purposes only**.
thank you
