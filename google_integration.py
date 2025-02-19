from google.cloud import firestore
from google.oauth2 import service_account

import json

def get_google_cloud_credentials(jstring:str):
    credentials_dict=json.loads(jstring)
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)   
    return credentials

    
def fetch_prompts(credentials):
    db = firestore.Client(credentials=credentials)
    collection_ref = db.collection(u'test_prompts')
    #query = collection_ref.where('status', '==', 'transcripted')
    docs = collection_ref.stream()
    
    # Collect document IDs that match the query
    results = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    return results

def fetch_prompt_by_name(credentials,name):
    db = firestore.Client(credentials=credentials)
    collection_ref = db.collection(u'test_prompts')
    query = collection_ref.where('prompt_name', '==', name)
    docs = query.stream()
    
    # Collect document IDs that match the query
    results = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    return results

def add_prompt(credentials, prompt_name, new_value):
    db = firestore.Client(credentials=credentials)
    collection_ref = db.collection(u'test_prompts').document() 
    collection_ref.set({
        u'prompt_name': prompt_name,
        u'prompt_value': new_value
    })

def update_prompt_by_name(credentials, prompt_name, new_value):
    res=fetch_prompt_by_name(credentials,prompt_name)
    if(len(res)==0):
        add_prompt(credentials, prompt_name, new_value)
        return "Found no match. Adding."
    elif len(res)==1:
        document_id=res[0].get('id')
        db = firestore.Client(credentials=credentials)
        collection_ref = db.collection(u'test_prompts')
        document_ref = collection_ref.document(document_id)
        document_ref.update({'prompt_value': new_value})
        return f"Found one match {res}. Document {document_id} updated: prompt to {new_value}"
    else:
        return f"Found multiple matches {res}. Not updating"