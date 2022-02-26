################################################################################
# IMPORTS
################################################################################
from web3 import Web3
import streamlit as st
import json
# from dotenv import load_dotenv
import os
from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json
from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json, get_CID
import qrcode
import cv2
import sqlalchemy as sql
import pandas as pd
import io
from pyzbar.pyzbar import decode
import config

import numpy as np




# load_dotenv()
# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(config.WEB3_PROVIDER_URI))
################################################################################
# Contract Helper function:
################################################################################
# @st.cache(allow_output_mutation=True)
def load_contract():
    # Load the contract ABI
    with open('abi.json') as f:
        artwork_abi = json.load(f)
    contract_address = config.SCA
    # Load the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=artwork_abi
    )
    return contract

def pin_artwork(artwork_name, artwork_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(artwork_file)
    # Build a token metadata file for the artwork
    token_json = {
        "name": artwork_name,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)
    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)
    return json_ipfs_hash

def pin_appraisal_report(report_content):
    json_report = convert_data_to_json(report_content)
    report_ipfs_hash = pin_json_to_ipfs(json_report)
    return report_ipfs_hash

    
# def qr_decoder(file):    
#     # read the QRCODE image
#     image = cv2.imread(file)
#     # initialize the cv2 QRCode detector
#     detector = cv2.QRCodeDetector()
#     # detect and decode
#     data, vertices_array, binary_qrcode = detector.detectAndDecode(image)
#     # if there is a QR code
#     # print the data
#     if vertices_array is not None:
#         return data
#     else:
#         return st.write("There was some error")


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
    img.save(f"./temp/{name}.jpg")
    # return img.get_image()

def get_image_from_database(name):
        with open(f"./temp/{name}.jpg", "rb") as image:
                f = image.read()
                b = bytearray(f)
                return b

#################################################################################
#Connect to DB
connection_string = "sqlite:///database_file.db"
engine = sql.create_engine(connection_string)
df = pd.read_sql("Texas License Plates",con=engine)
#################################################################################



#################################################################################
#Input information 
#################################################################################


contract = load_contract()
st.title("Register New Artwork")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)
name = st.text_input("What is the person's name")
vin = st.text_input("What is the VIN of your car")
status = st.selectbox("Select the Status",df["License Plate Status"].unique(),index=2)
make = st.selectbox("What is the make of the vehicle?",df.Make.sort_values().unique())
model = st.selectbox("What is the model of the vehicle?",df.Model.sort_values().unique())
year = st.selectbox("What is the year of the vehicle?",df.Year.sort_values().unique())
# color = st.selectbox("What is the color of the vehicle?",df.Color.sort_values().unique())

#################################################################################
# QR CODE STUFF
#################################################################################

if st.button("Register License Plates"):
    
    #CALL THE QR GENERATOR FUNCTION  WITH ALL INPUT INFORMATION 
    qr_file = make_qr_quote(name, vin, status, make, model, year)
    







    st.title("Mint License Plates")

    # if uploaded_file is not None:
    file = get_image_from_database(name)
    # pin artwork to pinata
    artwork_ipfs_hash = pin_artwork(name,file)

    # get the uri
    artwork_uri = f"ipfs://{artwork_ipfs_hash}"

    # get the CID
    cid = get_CID(artwork_ipfs_hash)

    # mint NFT through the smart contract function registerCar()
    tx_hash = contract.functions.registerCar(
        address,
        name,
        vin,
        status,
        artwork_uri
    ).transact({'from': address, 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    #getting the json recipet for hash
    st.write("Transaction receipt mined:")

    if st.button("View Reciept"):
        st.write(dict(receipt))


    st.download_button("Download your reciept",data=(str(receipt)))
    # st.download_button("elias",)
    #view the link to the artwork - thinking of deleting this and only kepeing the pinata link as a preview - thoughts? 
    st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
    ipfs_link = st.markdown(f"[Artwork IPFS Gateway Link](https://ipfs.io/ipfs/{artwork_ipfs_hash})")

    st.image(f"https://gateway.pinata.cloud/ipfs/{cid}")
        #open the Image that was generated as a file
    with open(f"./temp/{name}.jpg","rb") as file:
        #give the user the option to download their QR code
        btn = st.download_button(
                label="Download image",
                data=file,
                file_name=f"{name}.jpg",
                mime="image/jpg")


#################################################################################
# NEW SECTION - THIS IS THE VERIFYING PROCESS
#################################################################################


st.markdown("---")
st.title("Verify License Plates")
qr_verify = st.file_uploader("Please upload your QR Code?")


#################################################################################
# FUNCTIONS TO FULFILL THE VERIFYING PROCESS
#################################################################################

def total_token_supply():
    return contract.functions.totalSupply().call()


def vin_verification(number_of_tokens, vin_to_verify):
    for number in range(0,number_of_tokens):
        if contract.functions.vehicleCollection(number).call()[1] == vin_to_verify:
            return "IN SYSTEM"
        else:
            continue 
    return "not in system"

def qr_decoder(file):    

    file_bytes = file.getvalue()

    img_arr = np.frombuffer(file_bytes,np.uint8)
   
    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
   
    data = decode(img)[0].data

    decode_data = data.decode("utf-8")

    replace_string = decode_data.replace("'",'"')
    
    json_format_data = json.loads(replace_string)

    return json_format_data


if qr_verify:

    vin = qr_decoder(qr_verify)["vin"]


    
    


    total_supply = total_token_supply()

    st.write(vin_verification(total_supply, vin))




