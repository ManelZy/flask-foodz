from flask import Flask, request, jsonify
import json
from supabase import create_client, Client
import re 

app = Flask(__name__)

url = "https://srzradycoulcpkuintfl.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNyenJhZHljb3VsY3BrdWludGZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDI2Njc1ODEsImV4cCI6MjAxODI0MzU4MX0.GHF3XHbwbhhGFu7T4Y_E-tN39ebNCbKW1srbLurp6D0"
supabase: Client = create_client(url, key)

@app.route('/users.signup',methods=['GET','POST'])
def api_users_signup():
    email = request.form.get('email')
    password = request.form.get('password')
    
    print(f"Checking user existence for email: {email}")

    error = False
    if (not email) or (not re.match(r"[^@]+@[^@]+\.[^@]+", email)):
        error = False
        print(f"Error: {error}")
    
    if (not error) and ((not password) or (len(password) < 5)):
        error = 'Provide a password'

    if (not error):
        response = supabase.table('users').select("*").ilike('email', email).execute()
        if len(response.data) > 0:
            error = 'User already exists'

    if (not error):
       response = supabase.table('users').insert({"email": email, "pass": password}).execute()
       print(str(response.data))
       if len(response.data) == 0:
            error = 'Error creating the user'

    if (error):
        return jsonify({'status': 500, 'message': error})

    return jsonify({'status': 200, 'message': '', 'data': response.data[0]})

@app.route('/users.login',methods=['GET','POST'])
def api_users_login():
    email = request.form.get('email')
    password = request.form.get('password')
    error = False

    if (not email) or (len(email) < 5):
        error = 'Email needs to be valid'

    if (not error) and ((not password) or (len(password) < 5)):
        error = 'Provide a password'

    if not error:
        response = supabase.table('users').select("*").ilike('email', email).eq('pass', password).execute()
        if len(response.data) > 0:
            return jsonify({'status': 200, 'message': '', 'data': response.data[0]})

    if not error:
        error = 'Invalid Email or password'

    return jsonify({'status': 500, 'message': error})
    
@app.route('/orders', methods=['GET'])
def api_get_orders():
    orders = supabase.table('orders').select("*").execute().data

    # Fetch user details (user_full_name and user_address) for each order
    orders_with_users = []
    for order in orders:
        user_id = order.get('user_id')
        if user_id:
            user_response = supabase.table('users').select("user_full_name, user_address").eq('user_id', user_id).limit(1).execute()
            user_data = user_response.data[0] if user_response.data else None
            order['user_details'] = user_data

        orders_with_users.append(order)

    return jsonify({'status': 200, 'message': '', 'data': orders_with_users})

@app.route('/about')
def about():
    return 'About'

if __name__ == "__main__":
    app.run(debug=True)
