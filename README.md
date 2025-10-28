# NexGen Logistics - Cost Intelligence Platform

This project is an interactive web application built with Streamlit for the **Logistics Innovation Challenge (Option 5)**.

The dashboard analyzes 7 interconnected datasets to identify key drivers of operational costs for NexGen Logistics. It provides actionable insights into cost breakdowns, customer segment profitability, and route efficiency, with the goal of helping leadership achieve a 15-20% reduction in costs.

## 🚀 How to Run This Application

Follow these steps to run the dashboard on your local machine.

### 1. Prerequisites

* Python 3.8+
* `pip` (Python package installer)

### 2. Setup

**Clone the repository:**

```bash
git clone [https://github.com/pragy19/case_study_ofi]
cd [case_study_ofi]
```

**Create and activate a virtual environment (Recommended):**

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

Install all the required Python libraries using the requirements.txt file:

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit App

Make sure all 7 CSV files are in the same folder as app.py.

```bash
streamlit run app.py
```

A new tab will automatically open in your default web browser, displaying the interactive dashboard.

## 📁 Project Structure

```
.
├── 📄 app.py                     # The main Streamlit application code
├── 📄 requirements.txt           # List of all Python dependencies
├── 📄 README.md                  # You are here!
│
├── 📊 orders.csv                 # Dataset: Order-level information
├── 📊 delivery_performance.csv   # Dataset: Delivery execution data
├── 📊 routes_distance.csv        # Dataset: Route-specific metrics
├── 📊 cost_breakdown.csv         # Dataset: Detailed cost components
├── 📊 customer_feedback.csv      # Dataset: Customer voice data
├── 📊 vehicle_fleet.csv          # Dataset: Fleet information
└── 📊 warehouse_inventory.csv    # Dataset: Warehouse stock levels
```
