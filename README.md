# 🔑 T-SQL ⟺ Snowflake SQL Converter (FastAPI + WebUI)

Convert **Microsoft T-SQL queries** into **Snowflake SQL** with a simple FastAPI backend and a lightweight HTML/JS frontend.  
This project demonstrates **backend API development**, **SQL parsing/transformation**, and **full-stack integration** for real-world data engineering workflows.  

---

## ✨ Features
- 🔄 **T-SQL to Snowflake SQL conversion**  
- ⚡ FastAPI backend with Uvicorn for high performance  
- 💻 Web UI for interactive query testing  
- 📥 Download converted SQL directly as `.sql` file  
- 🧪 Built-in examples for demonstrating SQL migration scenarios  

---

## 🚀 Tech Stack
- **Python 3.13+**  
- **FastAPI + Uvicorn**  
- **Jinja2 Templates** (for UI rendering)  
- **SQLGlot** (SQL parsing/translation)  
- **HTML / CSS / JavaScript** for the frontend  

---

## 📦 Installation

Clone the repo and set up a virtual environment:

```
# Clone the repository
git clone https://github.com/adamsalemsmu-svg/tsql-to-snowflake.git
cd tsql-to-snowflake

# Create and activate a virtual environment
py -3.13 -m venv .venv
.venv\Scripts\activate   # (Windows)

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ Usage

Start the app:
```bash
.venv\Scripts\activate
python -m uvicorn webui.main:app --reload --port 8000
```

Then open your browser at:
```
http://127.0.0.1:8000
```

Paste your T-SQL on the left panel, click **Convert**, and get Snowflake SQL instantly.  

---

## 📝 Example

**T-SQL Input**
```sql
SELECT TOP 10 *
FROM dbo.Transactions
WHERE CreatedAt >= DATEADD(MONTH, -3, GETDATE());
```

**Snowflake SQL Output**
```sql
SELECT *
FROM Transactions
WHERE CreatedAt >= DATEADD(MONTH, -3, CURRENT_TIMESTAMP)
LIMIT 10;
```

---

## ⚠️ Common Issues
- **`jinja2 must be installed`** → Run: `pip install jinja2`  
- **Execution policy errors on PowerShell** → Run:  
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
- **`No module named 'uvicorn'`** → Run: `pip install uvicorn fastapi`

---

## 📂 Repo Structure
```
.
├── webui/              # FastAPI app + UI templates
├── converter.py        # SQL translation logic
├── requirements.txt    # Dependencies
├── README.md           # Project documentation
└── *.csv / *.sql       # Example data + queries
```

---

## 🧑‍💻 Author
**Adam Salem**  
Senior BI Developer / Data Engineer  
[LinkedIn](https://www.linkedin.com/in/adamsalemsmu) | [GitHub](https://github.com/adamsalemsmu-svg)
