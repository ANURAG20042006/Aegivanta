# SentinelAI Database Design Specification

## Overview
SentinelAI uses a fully normalized PostgreSQL relational schema designed for high-concurrency packet ingestion, audit logging, model versioning, and user management.

---

## 1. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : generates
    USERS ||--o{ INCIDENTS : assigned_to
    MODEL_REGISTRY ||--o{ INCIDENTS : predicted_by
    MODEL_REGISTRY ||--o{ TRAINING_RUNS : evaluates

    USERS {
        uuid id PK
        string username UK
        string email UK
        string password_hash
        string full_name
        string role
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    INCIDENTS {
        uuid id PK
        string source_ip
        string destination_ip
        integer source_port
        integer destination_port
        string protocol
        integer packet_length
        float flow_duration
        string attack_type
        float confidence_score
        boolean is_malicious
        string severity
        uuid predicted_by_model FK
        timestamp timestamp
        jsonb feature_payload
    }

    MODEL_REGISTRY {
        uuid id PK
        string model_name UK
        string model_type
        float accuracy
        float f1_score
        float precision_score
        float recall_score
        float roc_auc
        boolean is_active
        string artifact_path
        timestamp trained_at
    }

    TRAINING_RUNS {
        uuid id PK
        uuid model_id FK
        integer total_samples
        integer train_samples
        integer test_samples
        float training_duration_sec
        jsonb hyperparameters
        jsonb confusion_matrix
        timestamp created_at
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        string action
        string resource
        string ip_address
        string status
        timestamp timestamp
        jsonb metadata
    }
```

---

## 2. Table Specifications & Schema Definitions

### A. `users` Table
Stores system users with Role-Based Access Control (RBAC).

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Unique User ID |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | User login handle |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt / Argon2 hashed password |
| `full_name` | VARCHAR(100) | NOT NULL | Display name |
| `role` | VARCHAR(20) | NOT NULL, DEFAULT `'analyst'` | Role (`admin`, `analyst`, `viewer`) |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT `true` | Account status flag |
| `created_at` | TIMESTAMP WITH TIME ZONE | DEFAULT `NOW()` | Registration timestamp |

### B. `incidents` Table
Stores predicted network packet inspection results.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY, DEFAULT `gen_random_uuid()` | Incident ID |
| `source_ip` | VARCHAR(45) | NOT NULL, INDEXED | IPv4 / IPv6 source address |
| `destination_ip` | VARCHAR(45) | NOT NULL, INDEXED | IPv4 / IPv6 destination address |
| `source_port` | INTEGER | NOT NULL | Source port number |
| `destination_port` | INTEGER | NOT NULL | Destination port number |
| `protocol` | VARCHAR(10) | NOT NULL | TCP, UDP, ICMP |
| `packet_length` | INTEGER | NOT NULL | Packet size in bytes |
| `flow_duration` | DOUBLE PRECISION | NOT NULL | Flow duration in microseconds |
| `attack_type` | VARCHAR(50) | NOT NULL, INDEXED | Multi-class label (e.g., DDoS, BENIGN) |
| `confidence_score` | DOUBLE PRECISION | NOT NULL | Prediction confidence [0.0 - 1.0] |
| `is_malicious` | BOOLEAN | NOT NULL, INDEXED | High-level binary threat flag |
| `severity` | VARCHAR(15) | NOT NULL | Low, Medium, High, Critical |
| `predicted_by_model` | UUID | REFERENCES `model_registry(id)` | Model used for prediction |
| `timestamp` | TIMESTAMP WITH TIME ZONE | NOT NULL, INDEXED | Packet capture timestamp |
| `feature_payload` | JSONB | NULLABLE | 78+ CICIDS2017 feature vector |

---

## 3. Indexing Strategy & Performance Optimization
- `idx_incidents_timestamp_attack`: Composite index on `(timestamp DESC, attack_type)` for ultra-fast time-series chart querying.
- `idx_incidents_ip_malicious`: Index on `(source_ip, is_malicious)` for rapid threat intelligence lookup.
- Redis Caching Strategy: Active model metadata, live dashboard counters, and revoked JWT tokens are cached in Redis with strict TTLs.
