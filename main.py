from flask import Flask, render_template, request, redirect, url_for
import requests
from consumer_details import CONSUMER_KEY, CONSUMER_SECRET, USERNAME, PASSWORD
from bs4 import BeautifulSoup
import csv

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
    formatted_payment = f"${payment:,.0f}"

    return formatted_payment

def deferred_payment(amount, rate=.1025):
    principal = amount * 1.10
    promo = 99

    i = rate / 12
    v = 1 / (1 + i)
    v3 = v ** 3
    a3 = (1 - v3) / i
    a59 = (1 - v ** 59) / i

    X = (principal - promo * a3) / (1 + v3 * a59)
    formatted_payment = f"${X:,.2f}"

    return formatted_payment


@app.route("/", methods=["GET", "POST"])
def index():

    amount = None
    error = False
    message = None

    if request.method == "POST":
        cost = request.form.get("cost")

        try:
            amount = int(cost)
        except (ValueError, TypeError):
            error = True
            message = "Please enter a valid equipment cost."
            return render_template("index.html", step=1, error=error, message=message, equip_cost=None)

        if amount < 5000:
            error = True
            message = "Equipment cost must be greater than $5,000"
            return render_template("index.html", error=error, message=message, equip_cost=None, step=1)

        return redirect (url_for('payment', amount=amount, step=2))

    return render_template("index.html", error=error, message=message, equip_cost=amount,  step=1)



@app.route("/payment", methods=["GET", "POST"])
def payment():
    amount = int(request.args.get("amount"))

    formatted_amount = f"${amount:,.2f}"
    monthly_payment = deferred_payment(amount)

    return render_template("prospot.html", step=2, amount=amount, payment=monthly_payment, cost=formatted_amount)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        company = request.form.get("company")
        first_name = request.form.get("first")
        last_name = request.form.get("last")
        phone = request.form.get("phone")
        email = request.form.get("email")

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

        response = requests.post(URL + '/services/data/v64.0/sobjects/Lead/', json=new_lead, headers=headers)
        data = response.json()
        print(data)

        id = data.get("id")
        print(id)

        app_response = requests.get(URL + f'/services/data/v62.0/sobjects/Lead/{id}', headers=headers)
        app_data = app_response.json()

        print(app_data)

        app_url = app_data.get("AhiSign_App_URL__c")

        soup = BeautifulSoup(app_url, 'html.parser')
        url = soup.a['href']

    return render_template("contact.html", step=3, first_name=first_name, apply=url)

if __name__ == "__main__":
    app.run(debug=True, port=5002)

