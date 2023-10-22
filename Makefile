install:
	pip install -r requirements.txt

run:
	streamlit run app.py

all:
	install run