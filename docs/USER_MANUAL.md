# SentinelAI User Manual & Operational Guide

Welcome to the SentinelAI User Manual. This document provides step-by-step instructions for Security Analysts and System Administrators operating the platform.

---

## 1. Authentication & Role-Based Access Control (RBAC)

### User Roles:
- 👑 **Admin**: Full administrative privileges, user management, system configuration, and model retraining triggers.
- 🔬 **Analyst**: Threat prediction, packet inspection, analytics viewing, and report export.
- 👁️ **Viewer**: Read-only access to dashboard charts and incident summaries.

### Logging In:
1. Navigate to `http://localhost:5173/login`.
2. Enter your credentials or click a preset demo role button (`ADMIN`, `ANALYST`, `VIEWER`).
3. Upon authentication, you will be redirected to the **Master Dashboard**.

---

## 2. Operating the Master Dashboard

The Dashboard provides high-level situational awareness:
- **Network Status Banner**: Displays `SECURE` (green), `WARNING` (amber), or `CRITICAL` (crimson).
- **Stat Cards**: Monitors Total Packets Inspected, Threats Isolated, Model Accuracy, and Active Classifier count.
- **Live Network Throughput Stream**: Real-time line chart rendering packets per second.
- **Attack Category Breakdown**: Interactive doughnut chart breaking down attacks by percentage.
- **WebSocket Alert Ticker**: Live side panel flashing incoming threats pushed via WebSockets.

---

## 3. Real-Time Packet Inspection & CSV Upload

1. Navigate to **Real-Time Inspection** in the sidebar.
2. Select your preferred ML Classifier from the dropdown menu (e.g., *XGBoost*, *Random Forest*, *1D-CNN*).
3. **CSV Upload Mode**:
   - Drag & drop a network capture CSV file (such as `backend/app/sample_traffic.csv`).
   - Click **EXECUTE THREAT INFERENCE**.
   - Review summary metrics and the packet table highlighting malicious flows in neon red.
4. **Manual Flow Inspection Mode**:
   - Fill in individual flow features (Source IP, Flow Packets/s, Packet Length Mean, SYN Flags).
   - Click **INSPECT FLOW VECTOR** to view instantaneous prediction and SHAP feature attribution scores.

---

## 4. Generating & Downloading Executive Reports

1. Navigate to **Threat Reports**.
2. Select your desired report format: **EXECUTIVE PDF**, **EXCEL SPREADSHEET**, or **RAW CSV DUMP**.
3. Click **GENERATE REPORT NOW**.
4. Once completed, click **DOWNLOAD FILE** to save the generated document locally.
