from flask import Flask, request, jsonify
import json
from supabase import create_client, Client
import re 

app = Flask(__name__)

url = "https://srzradycoulcpkuintfl.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNyenJhZHljb3VsY3BrdWludGZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDI2Njc1ODEsImV4cCI6MjAxODI0MzU4MX0.GHF3XHbwbhhGFu7T4Y_E-tN39ebNCbKW1srbLurp6D0"
supabase: Client = create_client(url, key)


@app.route('/users.signup', methods=['POST'])
def api_users_signup():
    try:
        user_full_name = request.form.get('user_full_name') 
        email = request.form.get('email')
        password = request.form.get('password')
        user_address = request.form.get('user_address')  
        phone_number = request.form.get('phone_number') 
        user_type = request.form.get('user_type', 'owner')  # Default user_type to 'owner'

        print(f"Checking user existence for email: {email}")

        error = False
        if (not email) or (not re.match(r"[^@]+@[^@]+\.[^@]+", email)):
            error = True
            print(f"Error: {error}")

        if (not error) and ((not password) or (len(password) < 5)):
            error = True
            print(f"Error: {error}")

        if (not error):
            # Check if the user already exists
            response = supabase.table('users').select("*").ilike('email', email).execute()
            if len(response.data) > 0:
                error = True
                print("Error: User already exists")

        if (not error):
            # Insert the new user with additional information
            response = supabase.table('users').insert({
                "user_full_name": user_full_name,
                "email": email,
                "pass": password,
                "user_address": user_address,
                "tlf_num": phone_number,
                "user_type": user_type
            }).execute()
            print(str(response.data))
            if len(response.data) == 0:
                error = True
                print("Error: Failed to create the user")

        if (error):
            return jsonify({'status': 500, 'message': 'Error creating the user'})

        return jsonify({'status': 200, 'message': '', 'data': response.data[0]})
    except Exception as e:
        print(f"Error during user signup: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})

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

@app.route('/restaurants.signup', methods=['POST'])
def api_restaurants_signup():
    try:
        store_name = request.form.get('store_name') 
        store_address = request.form.get('store_address')
        phone_num = request.form.get('phone_num')
        business = request.form.get('business')

        print(f"Checking restaurant existence for store name: {store_name}")

        error = False
        # Add validation logic for store_name, store_address, phone_num, and business if needed

        if not error:
            # Check if the restaurant already exists
            response = supabase.table('restaurant').select("*").ilike('store_name', store_name).execute()
            if len(response.data) > 0:
                error = True
                print("Error: Restaurant already exists")

        if not error:
            # Insert the new restaurant with additional information
            response = supabase.table('restaurant').insert({
                "store_name": store_name,
                "store_address": store_address,
                "phone_num": phone_num,
                "business": business,
            }).execute()
            print(str(response.data))
            if len(response.data) == 0:
                error = True
                print("Error: Failed to create the restaurant")

        if error:
            return jsonify({'status': 500, 'message': 'Error creating the restaurant'})

        return jsonify({'status': 200, 'message': '', 'data': response.data[0]})
   except Exception as e:
    print(f"Error during restaurant signup: {str(e)}")
    return jsonify({'status': 500, 'message': f'Internal Server Error: {str(e)}'})


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
    
@app.route('/dishes', methods=['GET'])
def api_get_dishes():
    dishes = supabase.table('dishes').select("*").execute().data
    return jsonify({'status': 200, 'message': '', 'data': dishes})
@app.route('/dishes/<int:dish_id>', methods=['DELETE'])
def api_delete_dish(dish_id):
    try:
        # Check if the dish with the given dish_id exists
        existing_dish = supabase.table('dishes').select("*").eq('dish_id', dish_id).limit(1).execute()
        if not existing_dish.data:
            return jsonify({'status': 404, 'message': 'Dish not found'})

        # Delete the dish
        response = supabase.table('dishes').delete().eq('dish_id', dish_id).execute()

        if not response.data:
            return jsonify({'status': 500, 'message': 'Error deleting dish'})

        return jsonify({'status': 200, 'message': 'Dish deleted successfully'})
    except Exception as e:
        print(f"Error deleting dish: {e}")
        return jsonify({'status': 500, 'message': 'Error deleting dish'})

@app.route('/about')
def about():
    return 'About'

if __name__ == "__main__":
    app.run(debug=True)
