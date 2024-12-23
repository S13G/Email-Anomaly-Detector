# Use an official Python image
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV SECRET_KEY=${SECRET_KEY}
ENV ANYMAILFINDER_API_KEY=${ANYMAILFINDER_API_KEY}
ENV MAIL_EMAIL=${MAIL_EMAIL}
ENV MAIL_PASSWORD=${MAIL_PASSWORD}

# Set the working directory
WORKDIR /anomaly_detector

# Install system dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    python3-dev \
    libffi-dev


# Install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Copy project files
COPY . .

# Set the default command to run the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
