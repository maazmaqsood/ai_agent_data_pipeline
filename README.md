# 🚀 AI-Powered Data Pipeline with DeepSeek  

This repository contains a fully **dockerized AI-powered data pipeline**, where an **AI Agent (DeepSeek-R1 7B)** assists in handling ETL failures.  

## 📌 Features  

- **Automated Failure Handling**: AI decides whether to **restart, ignore, or escalate** failures.  
- **Fully Dockerized**: Runs with **Airflow + Ollama** in containers.  
- **Easy to Extend**: Blueprint for integrating AI with data engineering pipelines.  

## 🛠️ Setup & Run  

### 1️⃣ Clone the Repository  

### 2️⃣ Start Docker Containers

```bash
docker-compose up --build -d  
```

### 3️⃣ Access Airflow UI

- Open http://localhost:8080
- Login with Username: admin | Password: admin

### 4️⃣ Trigger the ETL Pipeline

Trigger the DAG manually from the Airflow Web UI or use:
```bash
docker exec -it airflow-scheduler airflow dags trigger etl_pipeline  
```

### 5️⃣ Check AI Agent Decisions

- View logs in Airflow UI → Task Logs

## 📢 Contribute

This is a blueprint—feel free to extend, improve, and customize it for your own AI-powered workflows! 🚀