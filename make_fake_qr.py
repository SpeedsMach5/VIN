import qrcode
import streamlit as st

def make_qr_quote(name, vin, status, make, model, year):
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4)
    qr.add_data(
        {"name":f"{name}", 
        "vin":f"{vin}",
        "status":f"{status}",
        "make":f"{make}",
        "model":f"{model}",
        "year":f"{year}"})
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"./fake_database/{name}.jpg")
    # return img.get_image()

def get_image_from_database(name):
        with open(f"./temp/{name}.jpg", "rb") as image:
                f = image.read()
                b = bytearray(f)
                return b

name = st.text_input("What is the person's name")
vin = st.text_input("What is the VIN of your car")
status = st.text_input("Select the Status")
make = st.text_input("What is the make of the vehicle?")
model = st.text_input("What is the model of the vehicle?")
year = st.text_input("What is the year of the vehicle?")

if st.button("Make QR Code"):
    make_qr_quote(name, vin, status, make, model, year)

    # st.image(get_image_from_database(name))