# SentinelAI Comprehensive UML & Data Flow Specifications

This document defines the Object-Oriented Class Hierarchy, Inter-Component Sequence Diagrams, and Multi-Level Data Flow Diagrams (DFDs) for SentinelAI.

---

## 1. Object-Oriented Class Diagram

```mermaid
classDiagram
    class BaseMLModel {
        <<abstract>>
        +model_name: str
        +is_trained: bool
        +fit(X, y)*
        +predict(X)* ndarray
        +predict_proba(X)* ndarray
        +save(filepath: str)
        +load(filepath: str)
    }

    class RandomForestDetector {
        +n_estimators: int
        +max_depth: int
        +fit(X, y)
        +predict(X) ndarray
        +predict_proba(X) ndarray
    }

    class XGBoostDetector {
        +learning_rate: float
        +n_estimators: int
        +fit(X, y)
        +predict(X) ndarray
        +predict_proba(X) ndarray
    }

    class LSTMDetector {
        +hidden_dim: int
        +num_layers: int
        +fit(X, y)
        +predict(X) ndarray
        +predict_proba(X) ndarray
    }

    class AutoencoderDetector {
        +threshold: float
        +fit(X, y)
        +predict(X) ndarray
        +detect_anomaly(X) ndarray
    }

    class DataPreprocessor {
        +scaler: StandardScaler
        +label_encoder: LabelEncoder
        +fit_transform(df: DataFrame) Tuple
        +transform(df: DataFrame) ndarray
        +handle_missing(df: DataFrame) DataFrame
        +balance_dataset(X, y) Tuple
    }

    class ExplainabilityEngine {
        +shap_explainer
        +lime_explainer
        +generate_shap_values(model, X_sample)
        +generate_lime_explanation(model, sample)
    }

    class IncidentService {
        +db_session
        +process_packet_batch(packets: List[PacketSchema]) List[Incident]
        +get_analytics_summary() AnalyticsSummarySchema
        +export_pdf_report(filter_params) bytes
    }

    BaseMLModel <|-- RandomForestDetector
    BaseMLModel <|-- XGBoostDetector
    BaseMLModel <|-- LSTMDetector
    BaseMLModel <|-- AutoencoderDetector
    IncidentService --> BaseMLModel : utilizes
    IncidentService --> DataPreprocessor : cleans input with
    IncidentService --> ExplainabilityEngine : computes explanations with
```

---

## 2. Real-Time Packet Prediction Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor SecurityAnalyst as Security Analyst (Client)
    participant ReactUI as React Frontend
    participant FastApiApi as FastAPI REST API
    participant JWTAuth as Auth Middleware
    participant PredictService as Predict Service
    participant Preprocessor as ML Data Preprocessor
    participant ModelEngine as Best Model (XGBoost/RF)
    participant PostgresDB as PostgreSQL Database
    participant WSManager as WebSocket Manager

    SecurityAnalyst->>ReactUI: Upload Packet CSV / Trigger Live Inspection
    ReactUI->>FastApiApi: POST /api/v1/predict/csv (With Bearer Token)
    FastApiApi->>JWTAuth: Validate JWT & Verify Roles (Analyst/Admin)
    JWTAuth-->>FastApiApi: Access Granted (User Context)
    FastApiApi->>PredictService: Inspect Packet Vector Payload
    PredictService->>Preprocessor: Scale & Clean 78 CICIDS Features
    Preprocessor-->>PredictService: Cleaned Scaled Array X
    PredictService->>ModelEngine: Execute Predict & Predict_Proba
    ModelEngine-->>PredictService: Attack Label, Confidence Score, Probability Distribution
    PredictService->>PostgresDB: Persist Incident Record & Audit Log
    PredictService->>WSManager: Broadcast Alert Event (If Malicious > 0.85)
    WSManager-->>ReactUI: WebSockets Push Live Threat Alert Toast
    PredictService-->>FastApiApi: Prediction Response JSON + Highlighted Malicious Packets
    FastApiApi-->>ReactUI: HTTP 200 OK (Predictions, Confidence, SHAP Feature Attribution)
    ReactUI-->>SecurityAnalyst: Render Interactive Dashboard & Threat Table
```

---

## 3. Data Flow Diagrams (DFD)

### Level 0 DFD (Context Diagram)

```mermaid
graph TD
    User((Security Analyst / Admin)) -->|Upload CSV Traffic / Query Dashboard| System[SentinelAI NIDS Platform]
    System -->|Real-Time Threats, Analytics, PDF/Excel Reports| User
    NetworkSensors((Network Sensors / PCAP Ingest)) -->|Raw Network Packets| System
```

### Level 1 DFD (Decomposed System Processes)

```mermaid
graph TD
    User((User / Analyst)) --> P1[1.0 User Auth & RBAC]
    P1 --> DB[(PostgreSQL Database)]
    
    Sensors((Traffic Ingestion / CSV)) --> P2[2.0 Data Preprocessing & Cleaning]
    P2 -->|Cleaned Feature Matrix| P3[3.0 ML/DL Attack Inference Engine]
    
    ModelRegistry[(Model Registry / Artifacts)] -->|Load Trained Model| P3
    P3 -->|Predictions & Confidence| P4[4.0 Incident Management & Persistence]
    P4 --> DB
    
    P3 -->|Live Alert Broadcast| P5[5.0 Real-Time WebSocket Streaming]
    P5 --> User
    
    P4 --> P6[6.0 Analytics & Explainability Generator]
    P6 -->|SHAP / LIME / Confusion Matrix| User
    
    P4 --> P7[7.0 Report Generation Engine]
    P7 -->|PDF / Excel / CSV Reports| User
```

### Level 2 DFD (Process 3.0: ML Inference Sub-processes)

```mermaid
graph TD
    In[Cleaned 78-Feature Vector] --> P3_1[3.1 Feature Scaling & Normalization]
    P3_1 --> P3_2[3.2 Classical & Boosting Model Pipeline]
    P3_1 --> P3_3[3.3 Deep Learning LSTM / Autoencoder Pipeline]
    
    P3_2 --> P3_4[3.4 Multi-Class Probability Aggregator]
    P3_3 --> P3_4
    
    P3_4 --> P3_5[3.5 Anomaly Score Thresholding]
    P3_5 --> Out[Final Attack Classification & Confidence Score]
```
