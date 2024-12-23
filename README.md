# Email Anomaly Detector

An Email Anomaly Detector is a simple web application built with Flask that helps identify suspicious or potentially harmful emails based on their domain. The app allows users to send emails and flag suspicious emails based on their domain names. It supports adding new domains for more dynamic anomaly detection.

## Features

- **Inbox View**: Displays incoming emails with sender details and content preview.
- **Flag Suspicious Emails**: Emails with domains not in the allowed list are flagged as potentially suspicious.
- **Send Email**: Allows users to send emails to a specific address with a subject and message.
- **Add New Domains**: Users can add new domains to the allowed domains list, updating the anomaly detection mechanism.

## Technologies

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS (Bootstrap)
- **Libraries**:
  - Flask-SQLAlchemy for database management
  - Flask for web routing
  - Bootstrap for responsive design
  - Bootstrap Icons for UI components********

## Requirements

To run the project locally, you need to have the following installed:

- Python 3.10+
- Flask
- Flask-SQLAlchemy

You can install the required dependencies using the following:

```bash
pip install -r requirements.txt
```

## Normal Setup

To set up the project, follow these steps:

1. Clone the repository to your local machine.
        
    `git clone https://github.com/yourusername/email-anomaly-detector.git`


2. Create a virtual environment and activate it.


3. Install the required dependencies using 

    `pip install -r requirements.txt`.


4. Run the application using 

    `python app.py`


5. Access the application at http://127.0.0.1:5000


## Docker Setup

To set up the project using Docker, follow these steps:

1. Clone the repository to your local machine.
        
    `git clone https://github.com/<username>/Email-Anomaly-Detector.git`

2. Build the Docker image using the following command:

    `docker build -t email-anomaly-detector .`

3. Run the Docker container using the following command:

    `docker run -p 5000:5000 --name email-anomaly-detector email-anomaly-detector`

4. Access the application at http://127.0.0.1:5000
