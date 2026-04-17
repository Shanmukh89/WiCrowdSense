# Product Requirements Document (PRD)

## Product Name

WiCrowdSense — Wi-Fi Based Crowd Density Estimation System Using ESP32

---

# 1. Problem Statement

In many environments such as classrooms, offices, libraries, conference halls, public transportation hubs, and event venues, it is valuable to know how many people are present in a room or area. Current crowd monitoring systems typically rely on:

* Cameras and computer vision systems
* Infrared people counters
* RFID badges or access systems
* Manual head counts

However, these approaches have several limitations:

1. **Privacy Concerns**
   Camera-based systems collect visual data and raise privacy concerns.

2. **High Cost**
   Professional crowd monitoring systems require expensive cameras, sensors, and computing hardware.

3. **Deployment Complexity**
   Camera systems require mounting, calibration, lighting control, and constant maintenance.

4. **Limited Scalability**
   Many solutions are not easy to scale across multiple rooms or buildings.

5. **Occlusion Issues**
   Cameras fail when people block each other.

A low-cost, privacy-preserving alternative is needed to estimate **crowd density and approximate number of people in a room** without using cameras.

---

# 2. Proposed Solution

WiCrowdSense uses **Wi-Fi signal sensing** to estimate the number of people inside a room.

Human bodies absorb, reflect, and scatter Wi-Fi signals. When multiple people move or stand inside a room, the Wi-Fi signal propagation changes. These disturbances can be measured and analyzed using signal metrics.

The system uses **four ESP32 modules placed at the four corners of the room** to continuously transmit and measure Wi-Fi signals between them. Currently, we have collected a real-world dataset establishing a baseline with 0 to 4 people. By analyzing these recorded patterns—particularly the drop in RSSI and CSI amplitude, and the increase in variance and entropy—we train a machine learning model that extrapolates and normalizes these relationships to estimate crowd densities of up to 150 people.

From these signals we collect:

* RSSI (Received Signal Strength Indicator)
* CSI Amplitude
* CSI Phase
* Packet timestamps
* Channel information

These metrics are then fed into the model to predict the crowd density in real-time.

---

# 3. System Overview

## Hardware Setup

Four ESP32 modules are placed at the corners of the room.

Room Layout Example

ESP1 -------- ESP2
|              |
|              |
ESP3 -------- ESP4

Each ESP32 node performs two functions:

1. Transmit Wi-Fi packets
2. Capture signal metrics from other ESP32 nodes

This produces signal measurements across multiple wireless links.

Possible communication links:

ESP1 → ESP2
ESP1 → ESP3
ESP1 → ESP4
ESP2 → ESP3
ESP2 → ESP4
ESP3 → ESP4

Each link produces continuous Wi-Fi signal measurements.

---

# 4. Key Signal Metrics Collected

## 4.1 RSSI (Received Signal Strength Indicator)

RSSI measures signal power received from another ESP32.

Typical RSSI range:

-30 dBm → Very strong signal
-60 dBm → Moderate signal
-90 dBm → Weak signal

Human bodies absorb Wi-Fi signals, so RSSI often decreases as the number of people increases.

---

## 4.2 CSI (Channel State Information)

CSI provides fine-grained signal information for each OFDM subcarrier in Wi-Fi communication.

For each packet we obtain:

* CSI amplitude per subcarrier
* CSI phase per subcarrier

CSI captures multipath effects caused by reflections and obstructions in the room.

People moving or standing in the room create measurable disturbances in CSI patterns.

---

# 5. Data Pipeline

Data collection process:

1. ESP32 nodes transmit Wi-Fi packets
2. Other nodes record signal metrics
3. Data is streamed to a central server
4. Data is stored in a dataset
5. Feature extraction is performed
6. Machine learning model predicts crowd size

Pipeline:

ESP32 Nodes
↓
Signal Metric Collection
↓
Dataset Storage
↓
Feature Extraction
↓
Machine Learning Model
↓
Predicted Crowd Count

---

# 6. Dataset Structure

Each sample in the dataset represents a time window of Wi-Fi measurements. 

**Real-world Baseline Data:** We have collected raw capture CSV files containing data for scenarios involving 1, 2, 3, and 4 people respectively. This data forms the ground truth for human-induced signal disturbances.

**Extrapolation:** Using the patterns discovered in the 1-4 person data, synthetic representations are generated to normalize the data and train the model for populations scaling up to 150 people.

Dataset fields include:

timestamp
transmitter_id
receiver_id
rssi
csi_subcarrier_1
csi_subcarrier_2
csi_subcarrier_3
...
csi_subcarrier_30
people_count_label

---

# 7. Example Dataset

Below is a simplified example dataset.

timestamp,tx,rx,rssi,sc1,sc2,sc3,sc4,sc5,sc6,sc7,sc8,people_count

0.001,ESP1,ESP2,-48,0.62,0.60,0.61,0.63,0.58,0.57,0.59,0.61,0
0.002,ESP1,ESP2,-49,0.63,0.59,0.60,0.64,0.57,0.56,0.58,0.60,0
0.003,ESP1,ESP2,-51,0.60,0.57,0.58,0.61,0.55,0.54,0.56,0.57,1
0.004,ESP1,ESP2,-52,0.58,0.56,0.55,0.60,0.54,0.52,0.53,0.55,1
0.005,ESP1,ESP2,-55,0.55,0.53,0.52,0.56,0.50,0.49,0.51,0.52,2
0.006,ESP1,ESP2,-57,0.52,0.50,0.49,0.54,0.48,0.47,0.48,0.49,2
0.007,ESP1,ESP2,-60,0.49,0.47,0.46,0.50,0.44,0.43,0.45,0.46,3
0.008,ESP1,ESP2,-61,0.47,0.45,0.44,0.48,0.42,0.41,0.43,0.44,3
0.009,ESP1,ESP2,-64,0.44,0.42,0.41,0.46,0.40,0.39,0.40,0.42,4
0.010,ESP1,ESP2,-66,0.41,0.40,0.39,0.44,0.37,0.36,0.38,0.39,4

Example interpretation:

Lower CSI amplitudes and lower RSSI values often correlate with increased human presence.

---

# 8. Feature Engineering

Raw signal data must be transformed into features.

Example features:

mean_csi_amplitude
variance_csi_amplitude
spectral_entropy
rssi_mean
rssi_variance
doppler_shift

Example feature vector:

[0.58, 0.09, 1.12, -52, 3.4]

Label:

people_count = 3

---

# 9. Machine Learning Model

Possible models:

Random Forest
Support Vector Machine
Gradient Boosting
Neural Networks
CNN + LSTM

Recommended approach:

CNN processes spatial relationships between subcarriers.
LSTM captures temporal patterns in signal changes.

Input:

CSI window of 100 packets

Output:

Predicted number of people

---

# 10. Expected Output

The system outputs estimated crowd density.

Example outputs:

0 people
1–2 people
3–5 people
6–10 people

Or exact count prediction.

Example prediction:

timestamp: 12:05:33
predicted_people: 4

---

# 11. Applications

Smart buildings
Energy optimization
Classroom occupancy monitoring
Conference room usage tracking
Public safety monitoring
Retail analytics
Crowd management at events

---

# 12. Key Advantages

Low cost hardware (ESP32 modules)

Privacy preserving (no cameras)

Works in low light or darkness

Scalable across multiple rooms

Continuous real-time monitoring

---

# 13. Future Improvements

Multi-room sensing networks
Edge ML inference on ESP32
Integration with building management systems
Anomaly detection for unusual crowd behavior
Real-time dashboard for occupancy visualization

---

# 14. Success Metrics

Accuracy of people count prediction

Mean Absolute Error (MAE)

Prediction latency

System reliability

---

# End of PRD