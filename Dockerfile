# Use the official Python base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install builder tools (e.g. gcc)
RUN apt-get update && apt-get install -y build-essential

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application files
COPY chatbot.py .

# Expose the Streamlit port
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "chatbot.py"]