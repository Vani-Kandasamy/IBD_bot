import streamlit as st
import authlib


IMAGE_ADDRESS = "https://aboutibs.org/wp-content/uploads/sites/13/Diet-and-IBS-768x512.jpg"

# web app
st.title("IBD Control Helper")

st.image(IMAGE_ADDRESS, caption = "IBD Nutrition Importance")

if not st.experimental_user.is_logged_in:
    if st.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()
else:
    # Display user name
    st.html(f"Hello, <span style='color: orange; font-weight: bold;'>{st.experimental_user.name}</span>!")

    # Documentation for each key
    key_descriptions = {
        "is_logged_in": "Indicates if the user is currently logged in.",
        "iss": "Issuer Identifier for the issuer of the response.",
        "azp": "Authorized party - the party to which the ID Token was issued.",
        "aud": "Audience - the party for which the ID Token is intended.",
        "sub": "Subject - an identifier for the user, unique among all Google accounts.",
        "email": "The user's email address.",
        "email_verified": "Indicates if the user's email address has been verified.",
        "at_hash": "Access token hash for validating the token.",
        "nonce": "A unique value to associate a client session with an ID Token.",
        "name": "The user's full name.",
        "picture": "URL of the user's profile picture.",
        "given_name": "The user's given name.",
        "family_name": "The user's family name.",
        "iat": "Issued At Time - the time the ID Token was issued.",
        "exp": "Expiration Time - the time the ID Token expires."
    }

    # Function to convert timestamp to human-readable format
    def format_timestamp(timestamp):
        try:
            return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            return timestamp  # Return original if conversion fails

    # Create a list of dictionaries for the DataFrame
    data = []
    for key, value in st.experimental_user.items():
        if key in ["iat", "exp"]:
            value = format_timestamp(value)  # Convert timestamps to human-readable format
        description = key_descriptions.get(key, "No description available.")
        data.append({"Key": key, "Value": value, "Description": description})

    st.subheader("User Information", divider=True)
    # Create the DataFrame
    df = pd.DataFrame(data)

    # Display the DataFrame in Streamlit
    st.dataframe(df, height=600, hide_index=True)

    if st.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()