from flask import Flask, request, jsonify
import json
from supabase import create_client, Client
import re 
from datetime import datetime
import base64


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
            print(f"Insert response: {response}")
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
        
@app.route('/users.login', methods=['POST'])
def api_users_login():
    email = request.form.get('email')
    password = request.form.get('password')
    error = None

    if not email or len(email) < 5:
        error = 'Email needs to be valid'

    elif not password or len(password) < 5:
        error = 'Provide a password'

    else:
        response = supabase.table('users').select("*").eq('email', email).eq('pass', password).execute()
        if response.data:
            user_data = response.data[0]
            return jsonify({'status': 200, 'message': 'Login successful', 'data': user_data})
        else:
            error = 'Invalid Email or password'

    return jsonify({'status': 401, 'message': error, 'data': {}})
    
@app.route('/users/<string:user_id>', methods=['GET'])
def api_get_users(user_id):
    users = supabase.table('users').select("*").eq('user_id', user_id).limit(1).execute()
    return jsonify({'status': 200, 'message': '', 'data': users})




@app.route('/orders/<string:restaurant_id>/restaurant_id', methods=['GET'])
def api_get_orders(restaurant_id):
    # Assuming the orders have an 'order_date' field representing the order date
    today = datetime.now().date().isoformat()
    orders = supabase.table('orders').select("*").eq('restaurant_id', restaurant_id).eq('order_date', today).execute().data

    # Fetch user details (user_full_name and user_address) for each order
    orders_with_users = []
    for order in orders:
        user_id = order.get('user_id')
        if user_id:
            user_response = supabase.table('users').select("user_full_name, user_address").eq('user_id', user_id).limit(1).execute()
            user_data = user_response.data[0] if user_response.data else None
            order['user_details'] = user_data

        order_status = order.get('order_status')
        if order_status in ['waiting', 'Accepted']:
            orders_with_users.append(order)

    return jsonify({'status': 200, 'message': '', 'data': orders_with_users})
    
@app.route('/dishes/<string:restaurant_id>/restaurant_id', methods=['GET'])
def api_get_dishes(restaurant_id):
    dishes = supabase.table('dishes').select("*").eq('restaurant_id', restaurant_id).execute().data
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
        
@app.route('/dishes/<int:dish_id>', methods=['PUT'])
def api_edit_dish(dish_id):
    try:
        # Check if the dish with the given dish_id exists
        existing_dish = supabase.table('dishes').select("*").eq('dish_id', dish_id).limit(1).execute()
        if not existing_dish.data:
            return jsonify({'status': 404, 'message': 'Dish not found'})

        # Get the updated data from the request
        updated_data = {
            "dish_name": request.form.get('dish_name'),
            "dish_desc": request.form.get('dish_desc'),
            "dish_price": request.form.get('dish_price'),
            "dish_category": request.form.get('dish_category'),
        }

        # Update the dish
        response = supabase.table('dishes').update(updated_data).eq('dish_id', dish_id).execute()

        if not response.data:
            return jsonify({'status': 500, 'message': 'Error updating dish'})

        return jsonify({'status': 200, 'message': 'Dish updated successfully', 'data': response.data[0]})
    except Exception as e:
        print(f"Error updating dish: {e}")
        return jsonify({'status': 500, 'message': 'Error updating dish'})

@app.route('/restaurants.signup', methods=['POST'])
def api_restaurant_signup():
    try:
        store_name = request.form.get('store_name')
        store_address = request.form.get('store_address')
        phone_num = request.form.get('phone_num')  
        business = request.form.get('business') 
        user_id = request.form.get('user_id')
        rest_img = request.form.get('rest_img')
        # Insert the new store
        response = supabase.table('restaurant').insert({
            "store_name": store_name,
            "store_address": store_address,
            "phone_num": phone_num,
            "business": business,
            "user_id": user_id,
            "rest_img": rest_img,
        }).execute()

        print(f"Insert response: {response}")

        if len(response.data) == 0:
            print("Error: Failed to create the store")
            return jsonify({'status': 500, 'message': 'Failed to create the store'})

        return jsonify({'status': 200, 'message': 'Store created successfully', 'data': response.data[0]})
    
    except Exception as e:
        print(f"Error during store signup: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})
        
       
@app.route('/dishes.add', methods=['POST'])
def api_dishes_add():
    try:
        dish_name = request.form.get('dish_name')
        dish_desc = request.form.get('dish_desc')
        dish_price = request.form.get('dish_price')  
        dish_category = request.form.get('dish_category') 
        restaurant_id = request.form.get('restaurant_id') 
        dish_img = request.form.get('dish_img')  
        # Insert the new store
        response = supabase.table('dishes').insert({
            "dish_name": dish_name,
            "dish_desc": dish_desc,
            "dish_price": dish_price,
           "dish_category": dish_category,
            "restaurant_id": restaurant_id,
            "dish_img": dish_img,
        }).execute()

        print(f"Insert response: {response}")

        if len(response.data) == 0:
            print("Error: Failed to add the dish")
            return jsonify({'status': 500, 'message': 'Failed to add the dish'})

        return jsonify({'status': 200, 'message': 'dish added successfully', 'data': response.data[0]})
    
    except Exception as e:
        print(f"Error during dish adding: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})
        
@app.route('/dishes/<int:dish_id>/dish_id', methods=['GET'])
def api_get_dishes_byid(dish_id):
    try:
        dish_response = supabase.table('dishes').select("*").eq('dish_id', dish_id).limit(1).execute()
        dish_data = dish_response.data[0] if dish_response.data else None

        if dish_data:
            # Extract relevant information from dish_data
            dish = {
                "dishId": dish_data.get('dish_id'),
                "name": dish_data.get('dish_name'),
                "description": dish_data.get('dish_desc'),
                "price": dish_data.get('dish_price'),
                "imagePath": dish_data.get('dish_img'),
                "category": dish_data.get('dish_category'),
            }

            return jsonify({'status': 200, 'message': '', 'data': dish})
        else:
            return jsonify({'status': 404, 'message': 'Dish not found'})

    except Exception as e:
        print(f"Error fetching dish: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})
        
@app.route('/orderitems/<int:order_id>/order_id', methods=['GET'])
def api_get_orderitems_byid(order_id):
    try:
        items_response = supabase.table('order_items').select("*").eq('order_id', order_id).execute().data

        if items_response:
            # Extract relevant information from item_data for each item
            items = []
            for item_data in items_response:
                item = {
                    "orderItemId": item_data.get('order_item'),
                    "itemQuantity": item_data.get('item_quantity'),
                    "dishId": item_data.get('dish_id'),
                }
                items.append(item)

            return jsonify({'status': 200, 'message': '', 'data': items})
        else:
            return jsonify({'status': 404, 'message': 'Order not found'})

    except Exception as e:
        print(f"Error fetching items: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})

    
@app.route('/categories/<string:restaurant_id>/restaurant_id', methods=['GET'])
def api_get_categories(restaurant_id):
    categories = supabase.table('categories').select("*").eq('restaurant_id', restaurant_id).execute().data
    return jsonify({'status': 200, 'message': '', 'data': categories})

@app.route('/categories.add', methods=['POST'])
def api_categories_add():
    try:
        category_name = request.form.get('category_name')
        restaurant_id = request.form.get('restaurant_id')
    

        # Insert the new store
        response = supabase.table('categories').insert({
            "category_name": category_name,
            "restaurant_id": restaurant_id,
            
        }).execute()

        print(f"Insert response: {response}")

        if len(response.data) == 0:
            print("Error: Failed to add the category")
            return jsonify({'status': 500, 'message': 'Failed to add the category'})

        return jsonify({'status': 200, 'message': 'category added successfully', 'data': response.data[0]})
    
    except Exception as e:
        print(f"Error during category adding: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})

@app.route('/users/<string:user_id>/restaurant_id', methods=['GET'])
def get_restaurant_id(user_id):
    try:
        # Query the restaurant table to get the corresponding restaurant_id based on user_id
        response = supabase.table('restaurant').select("*").eq('user_id', user_id).limit(1).execute()
        rest_data = response.data[0] if response.data else None

        if rest_data:
            # Extract relevant information from dish_data
            rest = {
            "restaurant_id": rest_data.get('restaurant_id'),
            "store_name": rest_data.get('store_name'),
            "store_address": rest_data.get('store_address'),
            "phone_num": rest_data.get('phone_num'),
            "business": rest_data.get('business'),
            }
            
            return jsonify({'status': 200, 'message': '', 'data': rest })
        else:
            return jsonify({'status': 404, 'message': 'Restaurant not found for the user'})

    except Exception as e:
        print(f"Error getting restaurant_id: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})
        
     

@app.route('/users/<string:user_id>', methods=['PUT'])
def api_edit_user(user_id):
    try:
        # Check if the user with the given user_id exists
        existing_user = supabase.table('users').select("*").eq('user_id', user_id).limit(1).execute()

        if not existing_user.data:
            return jsonify({'status': 404, 'message': 'User not found'})

        # Get the updated data from the request
        updated_data = {
            "email": request.form.get('email'),
            "pass": request.form.get('pass'),
            "user_address": request.form.get('user_address'),
            "user_full_name": request.form.get('user_full_name'),
            "tlf_num": request.form.get('tlf_num'),
        }

       
        # Update the user
        response = supabase.table('users').update(updated_data).eq('user_id', user_id).execute()

        if not response.data:
            return jsonify({'status': 500, 'message': 'Error updating user'})

        return jsonify({'status': 200, 'message': 'User updated successfully', 'data': response.data[0]})

    except Exception as e:
        print(f"Error updating user: {e}")
     
        return jsonify({'status': 500, 'message': 'Internal Server Error'})
        
@app.route('/orderstatus/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    try:
        # Check if the order with the given order_id exists
        existing_order = supabase.table('orders').select("*").eq('order_id', order_id).limit(1).execute()

        if not existing_order.data:
            return jsonify({'status': 404, 'message': 'Order not found'})

        # Get the updated data from the request
        new_status = request.json.get('order_status')

        if new_status is None:
            return jsonify({'status': 400, 'message': 'Bad Request - Missing order_status'})

        # Update the order status
        response = supabase.table('orders').update({'order_status': new_status}).eq('order_id', order_id).execute()

        if not response.data:
            return jsonify({'status': 500, 'message': 'Error updating order'})

        return jsonify({'status': 200, 'message': f'Order {order_id} status updated to {new_status}', 'data': response.data[0]})

    except Exception as e:
        # Log the error details to a secure location
        app.logger.error(f"Error updating order status: {e}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})
        
@app.route('/rest/<string:restaurant_id>', methods=['PUT'])
def api_edit_rest(restaurant_id):
    try:
        # Check if the user with the given user_id exists
        existing_rest = supabase.table('restaurant').select("*").eq('restaurant_id', restaurant_id).limit(1).execute()

        if not existing_rest.data:
            return jsonify({'status': 404, 'message': 'User not found'})

        # Get the updated data from the request
        updated_data = {
            "store_name": request.form.get('store_name'),
            "store_address": request.form.get('store_address'),
            "phone_num": request.form.get('phone_num'),
            "business": request.form.get('business'),
            "rest_img": request.form.get('rest_img'),
        }

       
        # Update the user
        response = supabase.table('restaurant').update(updated_data).eq('restaurant_id', restaurant_id).execute()

        if not response.data:
            return jsonify({'status': 500, 'message': 'Error updating user'})

        return jsonify({'status': 200, 'message': 'User updated successfully', 'data': response.data[0]})

    except Exception as e:
        print(f"Error updating user: {e}")
     
        return jsonify({'status': 500, 'message': 'Internal Server Error'})

@app.route('/rest.info/<string:restaurant_id>', methods=['GET'])
def api_get_restaurant_info(restaurant_id):
    try:
        # Query the restaurant table to get the corresponding restaurant information based on restaurant_id
        response = supabase.table('restaurant').select("*").eq('restaurant_id', restaurant_id).limit(1).execute()
        rest_data = response.data[0] if response.data else None

        if rest_data:
            # Extract relevant information from restaurant_data
            restaurant_info = {
                "restaurant_id": rest_data.get('restaurant_id'),
                "store_name": rest_data.get('store_name'),
                "store_address": rest_data.get('store_address'),
                "phone_num": rest_data.get('phone_num'),
                "business": rest_data.get('business'),
                "rest_img": rest_data.get('rest_img'),
                
            }

            return jsonify({'status': 200, 'message': '', 'data': restaurant_info})
        else:
            return jsonify({'status': 404, 'message': 'Restaurant not found'})

    except Exception as e:
        print(f"Error getting restaurant info: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})
        
@app.route('/user.info/<string:user_id>', methods=['GET'])
def api_get_user_info(user_id):
    try:
        # Query the restaurant table to get the corresponding restaurant information based on restaurant_id
        response = supabase.table('users').select("*").eq('user_id', user_id).limit(1).execute()
        res_data = response.data[0] if response.data else None

        if res_data:
            # Extract relevant information from restaurant_data
            user_info = {
                "user_id": res_data.get('user_id'),
                "user_full_name": res_data.get('user_full_name'),
                "user_address": res_data.get('user_address'),
                "tlf_num": res_data.get('tlf_num'),
                "email": res_data.get('email'),
                "pass": res_data.get('pass'),
            }

            return jsonify({'status': 200, 'message': '', 'data':user_info})
        else:
            return jsonify({'status': 404, 'message': 'Restaurant not found'})

    except Exception as e:
        print(f"Error getting restaurant info: {str(e)}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})


@app.route('/getPopularDishes/<string:restaurant_id>', methods=['GET'])
def get_popular_dishes(restaurant_id):
    try:
        # Retrieve order_items data for the specified restaurant_id
        order_items_response = supabase.table('order_items').select('dish_id').eq('restaurant_id', restaurant_id).execute()

        if order_items_response.data:
            # Assuming the result is a list of dictionaries
            order_items_data = order_items_response.data

            # Count occurrences of each dish_id in order_items
            dish_counts = {}
            for order_item_data in order_items_data:
                dish_id = order_item_data['dish_id']
                if dish_id not in dish_counts:
                    dish_counts[dish_id] = 1
                else:
                    dish_counts[dish_id] += 1

            # Filter dishes with count > 10
            popular_dishes = []
            for dish_id, count in dish_counts.items():
                if count > 0:
                    # Retrieve dish details based on dish_id
                    dish_response = supabase.table('dishes').select('*').eq('dish_id', dish_id).limit(1).execute()

                    if dish_response.data:
                        dish_details = dish_response.data[0]
                        popular_dishes.append({
                            "dish_id": dish_details['dish_id'],
                            "dish_name": dish_details['dish_name'],
                            "dish_img": dish_details['dish_img'],
                            "count": count,
                        })

            # Return popular dishes data as JSON
            return jsonify(popular_dishes)
        else:
            # Return an empty list if no data found
            return jsonify([])

    except Exception as e:
        # Handle database query errors
        return jsonify({'error': f'Database error: {str(e)}'}), 500
        
@app.route('/getOrdersStats/<string:restaurant_id>', methods=['GET'])
def get_order_statistics(restaurant_id):
    try:
        # Retrieve the number of orders for the specified restaurant_id
        order_count_response = supabase.table('orders').select('restaurant_id').eq('restaurant_id', restaurant_id).execute()

        # Retrieve the total price for the specified restaurant_id
        total_price_response = supabase.table('orders').select('total_price').eq('restaurant_id', restaurant_id).in_('order_status', ['Accepted', 'Completed']).execute()

        if order_count_response.data and total_price_response.data:
            order_count = len(order_count_response.data)
            total_price = sum(order['total_price'] for order in total_price_response.data)

            return {'order_count': order_count, 'total_price': total_price}
        else:
            return {'error': 'No data found'}

    except Exception as e:
        # Handle database query errors
        return {'error': f'Database error: {str(e)}'}

        
@app.route('/about')
def about():
    return 'About'

if __name__ == "__main__":
    app.run(debug=True)
