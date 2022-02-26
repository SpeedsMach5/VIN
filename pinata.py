import os
import json
# from gevent import config
import requests
import config
# from dotenv import load_dotenv
# load_dotenv()

json_headers = {
    "Content-Type": "application/json",
    "pinata_api_key": config.PKEY,
    "pinata_secret_api_key": config.SKEY,
}

file_headers = {
    "pinata_api_key": config.PKEY,
    "pinata_secret_api_key": config.SKEY,
}

def convert_data_to_json(content):
    data = {"pinataOptions": {"cidVersion": 1}, "pinataContent": content}
    return json.dumps(data)

def pin_file_to_ipfs(data):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinFileToIPFS",
        files={'file': data},
        headers=file_headers
    )
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash

def pin_json_to_ipfs(json):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        data=json,
        headers=json_headers
    )
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash

def get_CID(file_ipfs_hash):
    return requests.get(f"https://gateway.pinata.cloud/ipfs/{file_ipfs_hash}").json()["image"]