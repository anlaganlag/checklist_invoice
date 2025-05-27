@echo off 
chcp 65001 >nul 
call "D:\project\invoice_checkList\.venv\Scripts\activate.bat" 
cd /d "D:\project\invoice_checkList" 
streamlit run "D:\project\invoice_checkList\streamlit_app.py" 
