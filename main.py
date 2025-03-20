from flask import Flask, render_template, request
import requests
from consumer_details import CONSUMER_KEY, CONSUMER_SECRET, USERNAME, PASSWORD
from bs4 import BeautifulSoup

app = Flask(__name__)

URL = 'https://bbfunding.my.salesforce.com'
def generate_token():
    params = {
        "grant_type": "password",
        "client_id": CONSUMER_KEY,
        "client_secret": CONSUMER_SECRET,
        "username": USERNAME,
        "password": PASSWORD,
    }

    oauth_endpoint = '/services/oauth2/token'
    response = requests.post(URL + oauth_endpoint, params=params)

    if response.status_code != 200:
        return None, f"Error getting access token: {response.status_code} {response.text}"

    return response.json().get('access_token'), None

def calculate_monthly_payment(amount, interest_rate=9.25, term=60):
    """Calculate monthly payment based on simple interest formula"""
    monthly_rate = interest_rate / 100 / 12
    if monthly_rate == 0:
        return amount / term

    payment = amount * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)
    formatted_payment = f"${payment:.2f}"

    return formatted_payment

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/prospot", methods=["GET", "POST"])
def prospot_payment():
    amount = None
    monthly_payment = None
    equipment = None

    if request.method == "POST":
        try:
            equipment = request.form.get("equipment")
            amount = float(request.form["cost"])  # Fetch cost from form
            monthly_payment = calculate_monthly_payment(amount)  # Calculate payment
        except (ValueError, KeyError):  # Handle missing or invalid data
            amount = None
            monthly_payment = None
            equipment = None

    return render_template("prospot.html", amount='${:,.2f}'.format(amount), payment=monthly_payment, equipment=equipment)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        print(request.form)
        company = request.form.get("Company")
        first_name = request.form.get("FirstName")
        last_name = request.form.get("LastName")
        phone = request.form.get("Phone")
        email = request.form.get("Email")

        equipment = request.form.get("equipment")

        access_token, error = generate_token()
        print(f"{access_token}")

        if error:
            return error, 401

        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

        new_lead = {
            "OwnerId": '0055x00000BsZFz',
            "Company": company,
            "FirstName": first_name,
            "LastName": last_name,
            "Phone": phone,
            "Email": email,
            "LeadSource": "ProSpot Referral",
        }

        response = requests.post(URL + '/services/data/v62.0/sobjects/Lead/', json=new_lead, headers=headers)
        data = response.json()
        print(data)

        id = data.get("id")
        print(id)

        app_response = requests.get(URL + f'/services/data/v62.0/sobjects/Lead/{id}', headers=headers)
        app_data = app_response.json()

        print(app_data)

        app_url = app_data.get("Online_App_URL__c")

        soup = BeautifulSoup(app_url, 'html.parser')
        url = soup.a['href']

    return render_template("contact.html", first_name=first_name, apply=url, equipment=equipment)

if __name__ == "__main__":
    app.run(debug=True, port=5002)

