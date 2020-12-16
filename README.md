# Invest in U Tool: Back-to-School Decision-Making Helper

A CAPP 30122 group project aimed at creating a webscraper that analyzes data related to deciding to enroll in higher education programs.

## Project Group
* Kelsey Anderson (kjanderson@uchicago.edu)
* Yimeng Qiu (qym@uchicago.edu)
* Yawei Li (yaweili@uchicago.edu)

## How to run

1. In terminal, run from project root folder
    $bash install.sh
    Then http://127.0.0.1:5000 should appear in a browser window.
       * If it does not, please verify the flask server is running and refresh the page.

2.  Make selections on the web form and press submit to see model predictions for wage and educational outcomes.
    Press Test buttons to run data collection process demos.
	* Troubleshooting: If the install shell script fails to start the UI in your default browser, after installing all required packages from requirements.txt, execute:
          $flask run.

## Required Libraries (Same info in requirements.txt)

beautifulsoup4==4.8.2
bs4==0.0.1
certifi==2019.11.28
chardet==3.0.4
click==7.1.1
Flask==1.1.1
Flask-WTF==0.14.3
idna==2.9
itsdangerous==1.1.0
Jinja2==2.11.1
joblib==0.14.1
MarkupSafe==1.1.1
numpy==1.18.1
pandas==0.24.2
patsy==0.5.1
pip==20.0.2
pkg-resources==0.0.0
python-dateutil==2.8.1
python-dotenv==0.12.0
pytz==2019.3
requests==2.23.0
scikit-learn==0.22.2.post1
scipy==1.4.1
six==1.14.0
sklearn==0.0
soupsieve==2.0
statsmodels==0.11.1
urllib3==1.25.8
Werkzeug==1.0.0
WTForms==2.2.1
