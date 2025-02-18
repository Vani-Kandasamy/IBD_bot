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
    st.html(f"Hello, <span style='color: orange; font-weight: bold;'>{st.experimental_user.name}</span>!")
    if st.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()

st.caption(f"Streamlit version {st.__version__}")
st.caption(f"Authlib version {authlib.__version__}")