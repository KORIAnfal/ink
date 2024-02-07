from flask import Flask , request
from supabase import create_client, Client
import json
import re  # Import the regular expression module
import hashlib
from flask import jsonify
from collections import defaultdict
from urllib.parse import unquote



app = Flask(__name__)

url="https://mqlvalzpuinscoobhwmc.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xbHZhbHpwdWluc2Nvb2Jod21jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcwMjU1ODk4OCwiZXhwIjoyMDE4MTM0OTg4fQ.d3O0kWzLScmUEtiwSPGAnkWFElq7ApGKruTlmv1gbDc"
supabase: Client = create_client(url, key)

def is_valid_email(email):
    # Use a regular expression to check if the email format is valid
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@app.route('/getBookImagesBySeller1')
def get_book_images_by_seller1():
    try:
        # Fetch all book IDs with their seller IDs
        all_books_query = supabase.from_('sellerbook').select('bookid', 'sellerid')
        all_books_result = all_books_query.execute()

        # Create a dictionary to store book images grouped by seller ID
        book_images_by_seller = defaultdict(list)
        for book_row in all_books_result.data:
            book_id = book_row['bookid']
            book_image_query = supabase.from_('book').select('imagepath').eq('id', book_id)
            book_image_result = book_image_query.execute()
            book_image = book_image_result.data[0]['imagepath']
            book_images_by_seller[book_row['sellerid']].append(book_image)

        # Combine the results for all sellers
        result = {'book_images_by_seller': book_images_by_seller}

        # Print the data
        print("Result:", book_images_by_seller)

        # Return the data
        return jsonify(result)

    except Exception as e:
        print(f"Error fetching book images by seller: {e}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})



@app.route('/users.signup', methods=['POST'])
def api_users_signup():
    data_source = request.form
    accountname = data_source.get('accountname')
    email = data_source.get('email')
    password = data_source.get('password')
    hashed_password = hash_password(password)
    imagepath = data_source.get('imagepath')
    insta = data_source.get('insta')
    face = data_source.get('face')
    phonenumber = data_source.get('phonenumber')
    wilaya = data_source.get('wilaya')
    region = data_source.get('region')
    
    # Check if the email is a valid format
    if not is_valid_email(email):
        return json.dumps({'status': 400, 'message': 'Invalid email format'})

    # Check if the email already exists in the table
    existing_user_query = supabase.table('seller').select('id').eq('email', email)
    existing_user_response = existing_user_query.execute()

    if len(existing_user_response.data) > 0:
        return json.dumps({'status': 400, 'message': 'Email already exists'})

    # Insert the new user into the table
    response = supabase.table('seller').insert({
        "accountname": accountname,
        "email": email,
        "password": hashed_password,
        "imagepath": imagepath,
        "insta": insta,
        "face": face,
        "phonenumber": phonenumber,
        "wilaya": wilaya,
        "region": region
    }).execute()

    print(str(response.data))
    
    if len(response.data) == 0:
        return json.dumps({'status': 500, 'message': 'Error creating the user'})

    return json.dumps({'status': 200, 'message': '', 'data': response.data[0]})

def hash_password(password):
    # Use hashlib to hash the password
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return hashed

@app.route('/update_seller',methods=['GET','POST'])
def api_users_edit():
    data_source=request.form
    id=data_source.get('id')
    accountname= data_source.get('accountname')
    email= data_source.get('email')
    password= data_source.get('password')
    hashed_password = hash_password(password)
    imagepath= data_source.get('imagepath')
    insta= data_source.get('insta')
    face= data_source.get('face')
    phonenumber= data_source.get('phonenumber')
    wilaya= data_source.get('wilaya')
    region= data_source.get('region')
    error =False       
    if (not error):   
        if (imagepath == ''):
          response = supabase.table('seller').update({ "accountname": accountname, "email": email, "password": hashed_password, "insta":insta, "face":face, "phonenumber":phonenumber, "wilaya":wilaya, "region":region}).eq('id', int(id)).execute()

        else:   
          response = supabase.table('seller').update({ "accountname": accountname, "email": email, "password": hashed_password,"imagepath": imagepath, "insta":insta, "face":face, "phonenumber":phonenumber, "wilaya":wilaya, "region":region}).eq('id', int(id)).execute()
        
        print(str(response.data))
        if len(response.data)==0:
            error='Error editing the user'        
    if error:
        return json.dumps({'status':500,'message':error})     
    
   
    
    return json.dumps({'status':200,'message':'','data':response.data[0]})

@app.route('/getSellerById/<user_id>')
def api_getSellerById(user_id):

    try:
        # Fetch seller details from Supabase based on seller ID
        seller_info_query = supabase.from_('seller').select('*').eq('id', int(user_id))
        seller_info_response = seller_info_query.execute()
        if len(seller_info_response.data) > 0:
            return jsonify({'status': 200, 'message': '', 'data': seller_info_response.data[0]})
        else:
            return jsonify({'status': 404, 'message': 'Seller not found', 'data': None})
    except Exception as e:
        return jsonify({'status': 500, 'message': str(e), 'data': None})
        print(f"Error fetching book images by seller: {e}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})

    
@app.route('/users.login',methods=['GET','POST'])
def api_users_login():
    email= request.form.get('email')
    password= request.form.get('password')
    error =False
    if (not email) or (len(email)<5): #You can even check with regx
        error='Email needs to be valid'
    if (not error) and ( (not password) or (len(password)<6) ):
        error='Provide a password'        
    if (not error):
        hashed_password = hash_password(password)
        response = supabase.table('seller').select("*").ilike('email', email).eq('password',hashed_password).execute()
        if len(response.data)>0:
            return json.dumps({'status':200,'message':'','data':response.data[0]})
               
    if not error:
         error='Invalid Email or password'        
    
    return json.dumps({'status':500,'message':error}) 

@app.route('/book.ImagePath', methods=['GET','POST'])    
def api_book_getImagePath_by_id():
    id = request.args.get('id')

    error = False
    if not id:
        error = 'id needs to be valid'

    if not error:
        response = supabase.table('book').select("*").eq('id', int(id)).execute()
      
        if len(response.data)>0:
            return json.dumps({'status': 200, 'message': '', 'data': response['data']})

    if not error:
        error = 'Invalid id'

    return json.dumps({'status': 500, 'message': error, 'data': None})
    
@app.route('/book.searchByTitle', methods=['GET'])    
def api_search_book_by_title():
    name= request.form.get('name')
   
    error =False
    if (not name) : 
        error='name needs to be valid'
            
    if (not error):
        response = supabase.table('book').select("id").ilike('title', f'%{name}%').execute()
        
        if len(response.data)>0:
            return json.dumps({'status':200,'message':'','data':response.data})
              
    if not error:
         error='Invalid name'        
          
    return json.dumps({'status':500,'message':error})
@app.route('/book.searchByAuthors', methods=['GET'])    
def api_search_book_by_author():
    name= request.form.get('name')
   
    error =False
    if (not name) : 
        error='name needs to be valid'
            
    if (not error):
        response = supabase.table('book').select("id").ilike('authors', f'%{name}%').execute()
        
        if len(response.data)>0:
            return json.dumps({'status':200,'message':'','data':response.data})
              
    if not error:
         error='Invalid name'        
          
    return json.dumps({'status':500,'message':error})
    
@app.route('/book.filtercategory', methods=['GET'])    
def api_filter_book_by_category():
    categoryid= request.form.get('categoryid')
   
    error =False
    if (not categoryid) : 
        error='categoryid needs to be valid'

    if (not error):
        response = supabase.table('bookcategory').select("bookid").eq('categoryid', categoryid).execute()
        
        if len(response.data)>0:
            return json.dumps({'status':200,'message':'','data':response.data})
              
    if not error:
         error='Invalid  categoryid'        
          
    return json.dumps({'status':500,'message':error})
    
@app.route('/seller.addbook',methods=['GET','POST'])
def api_seller_addbook():
    data_source=request.form
    isbn= data_source.get('isbn')
    title= data_source.get('title')
    authors= data_source.get('authors')
    summary= data_source.get('summary')
    imagepath= data_source.get('imagepath')
    
    error =False       
    if (not error):    
        response = supabase.table('book').insert({ "isbn": isbn, "title": title, "authors": authors, "summary":summary,"imagepath": imagepath}).execute()
        
        print(str(response.data))
        if len(response.data)==0:
            error='Error adding the book'        
    if error:
        return json.dumps({'status':500,'message':error})     
    
   
    
    return json.dumps({'status':200,'message':'','data':response.data[0]})


@app.route('/seller.addBookToSeller',methods=['GET','POST'])
def api_seller_addbook_to_seller():
    data_source=request.form
    sellerid= data_source.get('sellerid')
    bookid= data_source.get('bookid')
    delivery= data_source.get('delivery')
    price= data_source.get('price')
    sell= data_source.get('sell')
    exchange= data_source.get('exchange')
    available= data_source.get('available')
    
    error =False       
    if (not error):    
        response = supabase.table('sellerbook').insert({ "sellerid": sellerid, "bookid": bookid, "delivery": delivery, "price":price,"sell": sell,"exchange": exchange,"available": available}).execute()
        
        print(str(response.data))
        if len(response.data)==0:
            error='Error adding the book'        
    if error:
        return json.dumps({'status':500,'message':error})     
    
   
    
    return json.dumps({'status':200,'message':'','data':response.data[0]})

@app.route('/Book.addBookCategory',methods=['GET','POST'])
def api_seller_addbook_category():
    data_source=request.form
    bookid= data_source.get('bookid') 
    categoryid = data_source.getlist('categoryid')
    
    error =False 
    for category_id in categoryid:
        response = supabase.table('bookcategory').insert({"bookid": bookid, "categoryid": category_id}).execute()
        
        print(str(response.data))
        if len(response.data) == 0:
            error = 'Error adding the book'
       
    if error:
        return json.dumps({'status':500,'message':error})     

    return json.dumps({'status':200,'message':'','data':response.data})

@app.route('/check_isbn',methods=['GET','POST'])
def api_check_isbn():
    data_source=request.get
    isbn= data_source.get('isbn')
    
    if not isbn:
        return jsonify({'error': 'ISBN parameter is required'}), 400

    response = supabase.table('book').select("id").ilike('isbn', isbn).execute()
    if len(response.data)>0:
            return json.dumps({'status':200,'message':'book exist','data':response.data[0]})

    return json.dumps({'status':500,'message':'no book'}) 

@app.route('/getBookById/<bookId>')
def api_getBookById(bookId):
  
      # Fetch book details from Supabase based on bookId
        book_query = supabase.from_('book').select('*').eq('id', int(bookId))
        book_response = book_query.execute()
    
        
        print("Supabase Response:", book_response)
        
        return json.dumps({'status': 200, 'message': '', 'data':book_response.data[0]})

@app.route('/getBookDetails/<bookId>')
def get_book_details(bookId):
    # Fetch book details
    book_query = supabase.from_('book').select('id', 'isbn', 'title', 'authors', 'summary', 'imagepath').eq('id', int(bookId))
    book_result = book_query.execute()

    # Fetch seller_book details
    seller_book_query = supabase.from_('sellerbook').select('sellerid', 'delivery', 'price', 'sell', 'exchange', 'available').eq('bookid', int(bookId))
    seller_book_result = seller_book_query.execute()

    # Initialize an empty list to store seller details
    sellers = []

    # Iterate through each row in seller_book_result
    for seller_book_row in seller_book_result.data:
        # Fetch seller details
        seller_query = supabase.from_('seller').select('id', 'accountname', 'email', 'phonenumber', 'imagepath','insta','face','wilaya','region').eq('id', seller_book_row['sellerid'])
        seller_result = seller_query.execute()

        # Combine the results for each seller
        seller_info = {
            'seller_book': seller_book_row,
            'seller': seller_result.data[0],
        }

        # Add the seller info to the list
        sellers.append(seller_info)
        



    # Combine the results for all sellers
    combined_result = {
        'book': book_result.data[0],
        'sellers': sellers,
    }

    # Print the data
    print("Combined Result:", combined_result)

    # Return the data
    return jsonify(combined_result)

@app.route('/getBookDetails2/<bookId>/<sellerId>')
def get_book_details2(bookId,sellerId):
    # Fetch book details
    book_query = supabase.from_('book').select('id', 'isbn', 'title', 'authors', 'summary', 'imagepath').eq('id', int(bookId))
    book_result = book_query.execute()

    # Fetch seller_book details
    seller_book_query = supabase.from_('sellerbook').select('sellerid', 'delivery', 'price', 'sell', 'exchange', 'available').eq('bookid', int(bookId)).eq('sellerid', sellerId)
    seller_book_result = seller_book_query.execute()
    
    combined_result = {
        'book': book_result.data[0],
        'seller': seller_book_result.data[0]
    }
    print("Combined Result:", combined_result)

    # Return the data
    return jsonify(combined_result)

@app.route('/MarkAsNotAvailable/<bookId>/<sellerId>')
def mark_as_not_avalaible(bookId,sellerId):
 
    supabase.from_('sellerbook').update({'available': 0}).eq('bookid', int(bookId)).eq('sellerid', sellerId).execute()
        

    return jsonify({'success': True, 'message': 'Book marked as not available successfully'})


@app.route('/MarkAsAvailable/<bookId>/<sellerId>')
def mark_as_avalaible(bookId,sellerId):
 
    supabase.from_('sellerbook').update({'available': 1}).eq('bookid', int(bookId)).eq('sellerid', sellerId).execute()
        

    return jsonify({'success': True, 'message': 'Book marked as not available successfully'})



@app.route('/getBookDetails3/<bookId>/<sellerId>')
def get_book_details3(bookId,sellerId):
    # Fetch book details
    book_query = supabase.from_('book').select('id', 'isbn', 'title', 'authors', 'summary', 'imagepath').eq('id', int(bookId))
    book_result = book_query.execute()

    # Fetch seller_book details
    seller_book_query = supabase.from_('sellerbook').select('sellerid', 'delivery', 'price', 'sell', 'exchange', 'available').eq('bookid', int(bookId)).eq('sellerid', sellerId)
    seller_book_result = seller_book_query.execute()
    
     # Fetch seller_book details
    seller_query = supabase.from_('seller').select('*').eq('id', sellerId)
    seller_result = seller_query.execute()
    
    combined_result = {
        'book': book_result.data[0],
        'seller': seller_result.data[0],
        'seller_book': seller_book_result.data[0]
    }
    print("Combined Result:", combined_result)

    # Return the data
    return jsonify(combined_result)
    
@app.route('/getBookImagesBySeller')
def get_book_images_by_seller():
    try:
        # Fetch all book IDs with their seller IDs
        all_books_query = supabase.from_('sellerbook').select('bookid', 'sellerid')
        all_books_result = all_books_query.execute()

        # Create a dictionary to store book information grouped by seller ID
        book_info_by_seller = defaultdict(list)
        for book_row in all_books_result.data:
            book_id = book_row['bookid']

            # Fetch book information, including imagepath, based on book ID
            book_info_query = supabase.from_('book').select('id', 'imagepath').eq('id', book_id)
            book_info_result = book_info_query.execute()

            if book_info_result.data:
                book_info = {
                    'id': book_info_result.data[0]['id'],
                    'imagepath': book_info_result.data[0]['imagepath']
                }
                book_info_by_seller[book_row['sellerid']].append(book_info)

        # Combine the results for all sellers
        result = {'book_info_by_seller': book_info_by_seller}

        # Print the data
        print("Result:", book_info_by_seller)

        # Return the data
        return jsonify(result)

    except Exception as e:
        print(f"Error fetching book information by seller: {e}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})


@app.route('/changePassword', methods=['POST'])
def change_password():
    try:
        data = request.get_json()

        userId = data.get('userId')
        oldPassword = data.get('oldPassword')
        newPassword = data.get('newPassword')

        # Retrieve the stored password for the user
        user_data = supabase.from_('seller').select('password').eq('id', userId).execute()
        stored_password_hash = user_data.data[0]['password']

        # Hash the old password for comparison
        old_password_hash = hash_password(oldPassword)

        # Check if the old password matches the stored password
        if old_password_hash == stored_password_hash:
            # Hash the new password before updating
            new_password_hash = hash_password(newPassword)
            # Update the password in the Supabase table
            supabase.from_('seller').update({'password': new_password_hash}).eq('id', userId).execute()

            return jsonify({'success': True, 'message': 'Password changed successfully'+newPassword})
        else:
            return jsonify({'success': False, 'message': 'Old password does not match'})

    except Exception as e:
        print(f"Error during password change: {e}")
        return jsonify({'success': False, 'message': 'Failed to change password'})

    




@app.route('/getCategories')
def api_get_categories():
    categories_query = supabase.from_('category').select('id', 'name').order('id')
    categories_result = categories_query.execute()

    return json.dumps({'status': 200, 'message': '', 'data': categories_result.data})


        
@app.route('/getBookByCategory/<categoryname>')
def get_book_category_details(categoryname):
    decoded_category_name = unquote(categoryname)
    category_query=supabase.from_('category').select('id').eq('name', decoded_category_name)
    category_result=category_query.execute()
    
    category_id = category_result.data[0]['id']

    books_query = supabase.from_('bookcategory').select('categoryid', 'bookid').eq('categoryid', category_id)
    books_result = books_query.execute()

    books = []

    for book_row in books_result.data:
        book_query = supabase.from_('book').select('id','imagepath').eq('id', book_row['bookid'])
        book_result = book_query.execute()

        books.append(book_result.data[0])  
        for book in books:
                sellerbook_query = supabase.from_('sellerbook').select('sell', 'exchange').eq('bookid', book['id'])
                sellerbook_result = sellerbook_query.execute()
                sellerbook_data = sellerbook_result.data

                # Initialize counters for 'sell' and 'exchange'
                sell_count = 0
                exchange_count = 0

                # Count the occurrences of 'sell' and 'exchange'
                for sellerbook_info in sellerbook_data:
                    if sellerbook_info['sell']:
                        sell_count += 1
                    if sellerbook_info['exchange']:
                        exchange_count += 1

                # Set 'sell' and 'exchange' based on the counts
                if sell_count == len(sellerbook_data):
                    book['sell'] = 1
                    book['exchange'] = 0
                elif exchange_count == len(sellerbook_data):
                    book['sell'] = 0
                    book['exchange'] = 1
                elif exchange_count == 0 and sell_count == 0:
                    book['sell'] = 0
                    book['exchange'] = 0    
                else:
                    book['sell'] = 1
                    book['exchange'] = 1
        
        
    # Print the data
    print("Result:", books)

    # Return the data
    return jsonify(books)  






from collections import defaultdict

@app.route('/getAllBooks')
def get_all_books():
    try:
        # Fetch all book IDs with their category IDs
        all_books_query = supabase.from_('bookcategory').select('bookid', 'categoryid')
        all_books_result = all_books_query.execute()

        # Create a dictionary to store book IDs grouped by category ID
        books_by_category = defaultdict(list)
        for book_row in all_books_result.data:
            books_by_category[book_row['categoryid']].append(book_row['bookid'])

        # Fetch details for all books in a single query
        all_books = defaultdict(list)
        for category_id, book_ids in books_by_category.items():
            category_name_query = supabase.from_('category').select('name').eq('id', category_id)
            category_name_result = category_name_query.execute()
            category_name = category_name_result.data[0]['name']

            books_query = supabase.from_('book').select('id', 'imagepath').in_('id', book_ids)
            books_result = books_query.execute()
            books = books_result.data

            # Fetch additional information from the sellerbook table
            for book in books:
                sellerbook_query = supabase.from_('sellerbook').select('sell', 'exchange').eq('bookid', book['id'])
                sellerbook_result = sellerbook_query.execute()
                sellerbook_data = sellerbook_result.data

                # Initialize counters for 'sell' and 'exchange'
                sell_count = 0
                exchange_count = 0

                # Count the occurrences of 'sell' and 'exchange'
                for sellerbook_info in sellerbook_data:
                    if sellerbook_info['sell']:
                        sell_count += 1
                    if sellerbook_info['exchange']:
                        exchange_count += 1

                # Set 'sell' and 'exchange' based on the counts
                if sell_count == len(sellerbook_data):
                    book['sell'] = 1
                    book['exchange'] = 0
                elif exchange_count == len(sellerbook_data):
                    book['sell'] = 0
                    book['exchange'] = 1
                elif exchange_count == 0 and sell_count == 0:
                    book['sell'] = 0
                    book['exchange'] = 0    
                else:
                    book['sell'] = 1
                    book['exchange'] = 1
            all_books[category_name] = books

        # Combine the results for all books
        result = {'books_by_category': all_books}

        # Print the data
        print("Result:", all_books)

        # Return the data
        return jsonify(result)

    except Exception as e:
        print(f"Error fetching all books: {e}")
        return jsonify({'status': 500, 'message': 'Internal Server Error'})


@app.route('/getTopSellers')
def get_top_sellers():
    # Fetch the seller IDs
    top_sellers = supabase.from_('sellerbook').select('sellerid').execute()

    # Extract seller IDs from the result
    seller_ids = [seller['sellerid'] for seller in top_sellers.data]

    # Count the occurrences of each seller ID
    seller_counts = {seller_id: seller_ids.count(seller_id) for seller_id in set(seller_ids)}

    # Sort the seller counts in descending order
    sorted_sellers = sorted(seller_counts.items(), key=lambda x: x[1], reverse=True)

    # Get the top 3 most frequent sellers
    top_frequent_sellers = sorted_sellers[:3]

    # Fetch additional data for each top seller from 'sellers_data' table
    sellers_data = []
    for seller_id, _ in top_frequent_sellers:
        # Assuming 'sellers_data' has columns like 'sellerid', 'name', 'location', etc.
        seller_data = supabase.from_('seller').select('id','accountname','imagepath').eq('id', seller_id).execute()
        sellers_data.append(seller_data.data[0])  # Assuming there's only one row per seller_id

    return jsonify({"top_frequent_sellers_data": sellers_data})

@app.route('/Deleteaccount/<id>', methods=['DELETE'])
def api_delete_account(id):
    # Step 1: Retrieve seller's information from 'seller' table
    seller_data = supabase.from_('seller').select('*').eq('id', id).execute()
    
    
    seller_info = seller_data.data[0]
    print('hello',seller_info)

    # Step 2: Insert seller's information into 'deleted_accounts' table
    supabase.table('deletedaccount').insert(seller_info).execute()

    # Step 3: Delete seller's information from 'seller' table
    supabase.from_('sellerbook').delete().eq('sellerid', id).execute()

    # Step 2: Delete the record from 'seller'
    supabase.from_('seller').delete().eq('id', id).execute()

    return {"success": "Account deleted successfully"}

@app.route('/deleteBook/<bookId>/<sellerId>')
def api_delete_book(bookId,sellerId):
    
        
    book_data = supabase.from_('sellerbook').select('*').eq('bookid', bookId).execute()
    book_result = book_data.data
    
    # Check the number of elements in the list
    num_elements = len(book_result)
    
    supabase.from_('sellerbook').delete().eq('bookid', bookId).eq('sellerid', sellerId).execute()
    if num_elements == 1:
        supabase.from_('bookcategory').delete().eq('bookid', bookId).execute()
        supabase.from_('book').delete().eq('id', bookId).execute()
        
    return {"success": "Book deleted successfully"}

    
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

if __name__ == "__main__":
   app.run(port=8080)

