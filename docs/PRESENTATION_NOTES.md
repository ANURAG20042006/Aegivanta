# SentinelAI Presentation Script & Viva Defense Guide

This document provides a slide-by-slide presentation script and defense Q&A preparation guide for presenting SentinelAI to project evaluators, professors, and technical reviewers.

---

## 🎤 Slide-by-Slide Presentation Script

### Slide 1: Title & Introduction
> "Good morning evaluators. Today I am presenting **SentinelAI**, an enterprise-level Intelligent Network Intrusion Detection and Threat Analytics Platform powered by Machine Learning and Deep Learning."

### Slide 2: Problem Statement & Motivation
> "Traditional Network Intrusion Detection Systems rely on signature matching. When an attacker modifies payload signatures or launches a Zero-Day exploit, traditional firewalls fail. SentinelAI solves this problem by using anomaly detection trained on 78 statistical network flow features."

### Slide 3: Dataset Benchmark (CICIDS2017)
> "We benchmarked our system on the CICIDS2017 dataset, covering 15 attack types including DDoS, DoS Hulk, Port Scans, Botnets, SQL Injection, and Zero-Day anomalies."

### Slide 4: 12-Model Machine Learning Architecture
> "We implemented and benchmarked 12 distinct machine learning and deep learning algorithms—ranging from Random Forest and XGBoost to PyTorch 1D-CNNs, LSTMs, and Deep Autoencoders. XGBoost achieved our top macro F1-score of 0.9901."

### Slide 5: Explainable AI (SHAP & LIME)
> "To prevent black-box decision making in security operations, SentinelAI integrates SHAP and LIME to show security analysts exactly which packet features contributed to an intrusion flag."

### Slide 6: Live Product Demonstration
> "Let us now demonstrate the live platform: logging in with role-based access, inspecting packet capture CSVs, viewing real-time WebSocket alert tickers, and downloading executive PDF reports."

---

## ❓ Viva Defense Q&A Preparation

### Q1: Why use CICIDS2017 instead of KDD Cup 99?
> **Answer**: KDD Cup 99 is over 25 years old and contains redundant, outdated traffic patterns. CICIDS2017 reflects modern network protocols, background traffic, and modern attack dynamics like Slowloris and DDoS.

### Q2: How does SentinelAI handle class imbalance?
> **Answer**: We implement synthetic oversampling (SMOTE) during preprocessing to balance minority attack classes like SQL Injection and Botnets relative to benign traffic.

### Q3: How is real-time performance achieved?
> **Answer**: We use asynchronous FastAPI with Uvicorn ASGI workers, Redis caching, and WebSockets pushing event stream payloads to a React frontend without full-page reloads.

### Q4: How does the Autoencoder detect Zero-Day attacks?
> **Answer**: The Deep Autoencoder is trained to minimize reconstruction loss on normal traffic. When an un-seen Zero-Day flow vector passes through, the reconstruction error spikes above our threshold, triggering an anomaly alert.
