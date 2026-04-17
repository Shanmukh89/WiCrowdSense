# WiCrowdSense

**Wi-Fi Based Crowd Density Estimation System Using ESP32**

WiCrowdSense uses Wi-Fi signal sensing across a network of ESP32 modules to accurately estimate the number of people inside a room. By recording perturbations in Received Signal Strength (RSSI) and Channel State Information (CSI), it serves as a low-cost, scalable, and privacy-preserving alternative to camera systems.

## Overview

Human bodies absorb, reflect, and scatter Wi-Fi signals. By analyzing these disruptions across multiple spatial links, we can train a machine learning model to estimate crowding.

- **Hardware**: Four ESP32 modules transmitting packets in the corners of a room.
- **Data Pipeline**: Raw PCAP captures $\rightarrow$ Signal Processing (RSSI, CSI Amplitude, Variance, Entropy) $\rightarrow$ Aggregation $\rightarrow$ ML Inference.
- **Dashboard**: A static HTML/JS dashboard styled to immediately display telemetry and inference estimations.

## Project Structure

- `data_sett/`: Raw data captured spanning baseline measurements (0 to 4 people).
- `train_model.py`: Processing script that normalizes and extracts features across links to train the estimation model.
- `client/`: Houses the dashboard environment.
  - `client/index.html`: The static dashboard visualizing inference updates.

## Getting Started

1. **Dashboard Setup**: 
   Simply load the static dashboard using any HTTP server:
   ```bash
   cd client
   npx serve .
   ```
   Or launch directly by navigating to `client/index.html`.

2. **Model Training**:
   Run the training pipeline against the captured sample sets:
   ```bash
   python train_model.py
   ```

## Privacy & Scalability
This project emphasizes anonymity by strictly processing numerical Wi-Fi signal attributes. The framework is highly scalable for deployment across campuses to trace building utilization automatically.
