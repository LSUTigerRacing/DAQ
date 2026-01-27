# DAQ Environment Setup

This guide walks you through setting up your local development environment and verifying that you can connect to the TimescaleDB instance used by the DAQ team.

---

## 1. Prerequisites 

Install Before Proceeding: 

1. Python 3.XX
2. Docker Desktop
3. IDE of choice (e.g. VS Code)
4. Clone DAQ Repo

---

## 2. Start TimescaleDB Instance 
Command: docker compose up -d

---

## 3. Verify Database Connection 

Command: docker exec -it lsu-fsae-timescaledb psql -U fsae -d daq_data -c "SELECT 1;"

You should see a table with '1' in it.

---

## 4. Setup is Complete

You are now ready to:


1. Parse DAQ JSON payloads
2. Write ingestion scripts
3. Build dashboards on top of real data
4. Query time-series sensor data
 
---

## Questions? 
Ask in the DAQ channel! Please don't get stuck debugging for hours by yourself!