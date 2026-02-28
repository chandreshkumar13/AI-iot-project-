# Animal Crossing Detection Using Wireless CSI

## 📌 Project Overview
This project aims to detect animal crossings on rural roads using wireless Channel State Information (CSI) signal variations. Instead of camera-based systems, we analyze wireless signal distortions caused by movement to detect and classify animal crossings in real-time.

## 🚧 Problem Statement
Animal crossings on rural highways lead to:
- Vehicle–animal collisions
- Wildlife fatalities
- Driver safety risks
- Poor visibility challenges (fog, night, rain)

Camera-based systems fail under low-light and harsh weather conditions.

## 💡 Proposed Solution
We use wireless signal distortion (CSI / RSSI variation) to:
- Detect movement near the road
- Classify object size (small / medium / large)
- Trigger real-time alerts
- Store detection logs in cloud database

## 🏗️ System Architecture
WiFi Signal → Signal Processing → Feature Extraction → ML Model → Backend API → Cloud Database → Dashboard → Alert System

## 🛠️ Tech Stack
- Python (ML & Backend)
- Scikit-learn (Random Forest Model)
- Flask (Backend API)
- MongoDB Atlas (Cloud Database)
- React.js (Frontend Dashboard)
- Render / Vercel (Cloud Deployment)

## 🎯 Key Objectives
- Reliable wireless-based movement detection
- Real-time classification of animal size
- Cloud-based monitoring system
- Reduction of wildlife collisions

## 📁 Project Structure
