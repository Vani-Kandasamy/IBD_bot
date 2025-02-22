from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime
from google.api_core.exceptions import NotFound


def get_google_cloud_credentials(service_account_info):
    #service_account_info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    return credentials

def get_user_field(db, user_email, field_name='queries_log'):
    # Reference the user's document in Firestore by email
    doc_ref = db.collection('users').document(user_email)

    try:
        # Get the document
        user_doc = doc_ref.get()
        if user_doc.exists:
            # Convert the document to a dictionary
            user_details = user_doc.to_dict()

            # Check if the requested field exists in the document
            if field_name in user_details:
                # Retrieve and return the specific field value
                field_value = user_details[field_name]
                print(f"Field '{field_name}' for user {user_email}: {field_value}")
                return field_value
            else:
                # If the field does not exist, inform the user
                print(f"The field '{field_name}' does not exist for user {user_email}.")
                return None
        else:
            print(f"No such user with email: {user_email}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_user_details(db, user_email):
    # Reference the user's document in Firestore by email
    doc_ref = db.collection('users').document(user_email)

    try:
        # Get the document
        user_doc = doc_ref.get()
        if user_doc.exists:
            # Print or utilize the user's details
            user_details = user_doc.to_dict()
            print(f"User details for {user_email}:")
            for key, value in user_details.items():
                print(f"{key}: {value}")
            return user_details
        else:
            print(f"No such user with email: {user_email}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def update_user_document(db, user_email, user_name, user_query, bot_response):
    # Reference the user's document in Firestore by email
    doc_ref = db.collection('users').document(user_email)

    # Prepare interaction data with timestamp
    timestamp = datetime.utcnow()
    interaction_record = {
        'query': user_query,
        'response': bot_response,
        'timestamp': timestamp
    }

    try:
        # Update the document with the current interaction
        doc_ref.update({
            'name': user_name,
            'query': user_query,
            'response': bot_response,
            'queries_log': firestore.ArrayUnion([interaction_record])
        })
    except NotFound:
        # If the user document does not exist, create it
        doc_ref.set({
            'email': user_email,
            'name': user_name,
            'query': user_query,
            'response': bot_response,
            'queries_log': [interaction_record]
        })