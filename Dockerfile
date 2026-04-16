# Step 1: Python ki stable version use karein
FROM python:3.9

# Step 2: Container mein folder set karein
WORKDIR /app

# Step 3: Pehle requirements copy aur install karein (Fast building ke liye)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Baqi saara code (app.py) copy karein
COPY . .

# Step 5: Cloud Run ke liye port expose karein
EXPOSE 8080

# Step 6: Streamlit chalane ki command
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
