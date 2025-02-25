import streamlit as st
from PIL import Image
from image_graph import graph_streamer

def image_bot():

    IMAGE_ADDRESS = "https://upload.wikimedia.org/wikipedia/commons/1/1a/Irritable_bowel_syndrome.jpg"
    IMAGE_NAME = "uploaded_image.png"

    # title
    st.title("IBSee Guide")
    # image
    st.image(IMAGE_ADDRESS, caption = "IBS Disease Helper")

    # Upload image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # open the image
        image = Image.open(uploaded_file)

        # display the image
        st.header("Uploaded Image")
        st.image(image, caption='Uploaded Image.', use_container_width=True)

        # save the image as a PNG file
        image.save(IMAGE_NAME)

        # analyse the image
        with st.spinner("Generating Information......"):
            get_chip_type = st.write_stream(graph_streamer(IMAGE_NAME))
            st.toast('Information Generation Successful!', icon='✅')

        if not get_chip_type:
            st.error("Cannot Interpret the Image", icon = "❌")
            st.stop()