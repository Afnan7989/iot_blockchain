from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
import json
import os
import time
import random
import requests
from dotenv import load_dotenv

from .models import SensorRecord
from .blockchain import store_on_chain, verify_on_chain
from .crypto import encrypt_json, decrypt_json

# ------------------------------------------------------------------
# ENVIRONMENT
# ------------------------------------------------------------------

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")
PINATA_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

PINATA_HEADERS = {
    "Content-Type": "application/json",
    "pinata_api_key": PINATA_API_KEY,
    "pinata_secret_api_key": PINATA_API_SECRET,
}

# ------------------------------------------------------------------
# BASIC PAGES
# ------------------------------------------------------------------

def dashboard(request):
    return render(request, "dashboard.html")


def data_storage(request):
    return render(request, "data_storage.html")


 
def data_access(request):
    # Fetch all records, newest first
    records = SensorRecord.objects.all().order_by("-created_at")
    return render(request, "data_access.html", {"records": records})
# ------------------------------------------------------------------
# CUSTOM DATA STORAGE (HTML FORM → IPFS → BLOCKCHAIN)
# ------------------------------------------------------------------

@csrf_exempt
 
def custom_data_storage(request):
    start_time = time.perf_counter()
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        # 1. Read data from HTML form
        sensor_data = {
            "title": request.POST.get("custom_title"),
            "temperature": float(request.POST.get("custom_temperature")),
            "humidity": float(request.POST.get("custom_humidity")),
            "air_pressure": float(request.POST.get("custom_pressure")),
            "datetime": datetime.utcnow().isoformat(),
        }

        # 2. Encrypt data
        encrypted_payload = encrypt_json(sensor_data)

        # 3. Upload encrypted JSON to IPFS (Pinata)
        ipfs_response = requests.post(
            PINATA_URL,
            headers=PINATA_HEADERS,
            data=json.dumps(encrypted_payload),
        )

        if ipfs_response.status_code != 200:
            return JsonResponse({"error": "IPFS upload failed"}, status=500)

        cid = ipfs_response.json()["IpfsHash"]
        print("CID:", cid)

        # 4. Store CID on blockchain
        bc_result = store_on_chain(cid)
        print("Blockchain Result:", bc_result)

        end_time = time.perf_counter()
        storage_time_taken = end_time - start_time
        transaction_per_second = 1 / storage_time_taken if storage_time_taken > 0 else 0

        # 5. Store ONLY references in DB
        record = SensorRecord.objects.create(
            ipfs_cid=cid,
            blockchain_tx=bc_result["tx_hash"],
            blockchain_account=bc_result["account_address"],
            storage_time_taken=storage_time_taken,
            transaction_per_second=transaction_per_second,
        )

        return JsonResponse({
            "success": True,
            "message": "Data stored successfully!",
            "data": {
                "sensor_data": sensor_data,
                "ipfs_cid": cid,
                "blockchain_tx": bc_result["tx_hash"],
                "blockchain_account": bc_result["account_address"],
                "storage_time_taken": round(storage_time_taken, 4),
                "transaction_per_second": round(transaction_per_second, 2),
            }
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Failed to store data: {str(e)}"
        }, status=500)

# ------------------------------------------------------------------
# RANDOM DATA GENERATOR (SIMULATED IOT)
# ------------------------------------------------------------------

 
def generate_random_data(request):
    sensor_data = {
        "title": f"IoT Sensor {random.randint(1, 100)}",
        "temperature": round(random.uniform(20.0, 35.0), 2),
        "humidity": round(random.uniform(40.0, 70.0), 2),
        "air_pressure": round(random.uniform(980.0, 1050.0), 2),
        "datetime": datetime.utcnow().isoformat(),
    }

    return JsonResponse(sensor_data)

@csrf_exempt
def store_random_data(request):
    start_time = time.perf_counter()
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        # 1. Generate random data (backend authoritative)
        sensor_data = {
            "title": f"IoT Sensor {random.randint(1, 100)}",
            "temperature": round(random.uniform(20.0, 35.0), 2),
            "humidity": round(random.uniform(40.0, 70.0), 2),
            "air_pressure": round(random.uniform(980.0, 1050.0), 2),
            "datetime": datetime.utcnow().isoformat(),
        }

        # 2. Encrypt data
        encrypted_payload = encrypt_json(sensor_data)

        # 3. Upload encrypted JSON to IPFS (Pinata)
        ipfs_response = requests.post(
            PINATA_URL,
            headers={
                "Content-Type": "application/json",
                "pinata_api_key": PINATA_API_KEY,
                "pinata_secret_api_key": PINATA_API_SECRET,
            },
            data=json.dumps(encrypted_payload),
        )

        if ipfs_response.status_code != 200:
            return JsonResponse({"error": "IPFS upload failed"}, status=500)

        cid = ipfs_response.json()["IpfsHash"]

        # 4. Store CID on blockchain
        bc_result = store_on_chain(cid)

        end_time = time.perf_counter()
        storage_time_taken = end_time - start_time
        transaction_per_second = 1 / storage_time_taken if storage_time_taken > 0 else 0

        # 5. Store ONLY references in DB
        record = SensorRecord.objects.create(
            ipfs_cid=cid.strip(),
            blockchain_tx=bc_result["tx_hash"],
            blockchain_account=bc_result["account_address"],
            storage_time_taken=storage_time_taken,
            transaction_per_second=transaction_per_second,
        )

        return JsonResponse({
            "success": True,
            "message": "Random data stored successfully!",
            "data": {
                "sensor_data": sensor_data,
                "ipfs_cid": cid,
                "blockchain_tx": bc_result["tx_hash"],
                "blockchain_account": bc_result["account_address"],
                "storage_time_taken": round(storage_time_taken, 4),
                "transaction_per_second": round(transaction_per_second, 2),
            }
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Failed to store data: {str(e)}"
        }, status=500)


# ------------------------------------------------------------------
# VIEW RECORD (VERIFY → FETCH FROM IPFS)
# ------------------------------------------------------------------

# def view_record(request, cid):
#     try:
#         record = SensorRecord.objects.get(ipfs_cid=cid)
#         print("Record:", record)
#     except SensorRecord.DoesNotExist:
#         print("Record not found")
#         return JsonResponse({"error": "Record not found"}, status=404)

#     # 1. Verify CID on blockchain
#     try:
#         valid = verify_on_chain(record.ipfs_cid)
#         print("Blockchain verification:", valid)
#     except Exception as e:
#         print("Blockchain verification error:", str(e))
#         return JsonResponse({"error": f"Blockchain verification failed: {str(e)}"}, status=500)

#     if not valid:
#         print("Data tampered or CID not found")
#         return JsonResponse({"error": "Data tampered or CID not found"}, status=400)

#     # 2. Fetch encrypted data from IPFS
#     try:
#         ipfs_response = requests.get(f"https://gateway.pinata.cloud/ipfs/{record.ipfs_cid}")
#         ipfs_response.raise_for_status()
#         encrypted_data = ipfs_response.json()
#         print("Encrypted Data:", encrypted_data)
#     except Exception as e:
#         print("IPFS fetch error:", str(e))
#         return JsonResponse({"error": f"Failed to fetch IPFS data: {str(e)}"}, status=500)

#     # 3. Return payload with matching keys for frontend
#     return JsonResponse({
#         "verified": True,
#         "encrypted_data": encrypted_data,   # match JS
#         "cid": record.ipfs_cid,
#         "tx_hash": record.blockchain_tx,
#         "account_address": record.blockchain_account,
#     })

def view_record(request, cid):
    start_time = time.perf_counter()
    try:
        record = SensorRecord.objects.get(ipfs_cid=cid)
    except SensorRecord.DoesNotExist:
        endtime = time.perf_counter()
        access_time_taken = endtime - start_time
        record.access_time_taken = access_time_taken
        record.hash_matched = False
        record.save(update_fields=["access_time_taken", "hash_matched"])
        print("Access time taken:", access_time_taken)
        print("Hash matched:", record.hash_matched)
        return JsonResponse({"error": "Record not found"}, status=404)

    # Verify CID on blockchain
    try:
        valid = verify_on_chain(record.ipfs_cid)
    except Exception as e:
        endtime = time.perf_counter()
        access_time_taken = endtime - start_time
        record.access_time_taken = access_time_taken
        record.hash_matched = False
        record.save(update_fields=["access_time_taken", "hash_matched"])
        print("Access time taken:", access_time_taken)
        print("Hash matched:", record.hash_matched)
        return JsonResponse({"error": f"Blockchain verification failed: {str(e)}"}, status=500)

    if not valid:
        endtime = time.perf_counter()
        access_time_taken = endtime - start_time
        record.access_time_taken = access_time_taken
        record.hash_matched = True
        record.save(update_fields=["access_time_taken", "hash_matched"])
        print("Access time taken:", access_time_taken)
        print("Hash matched:", record.hash_matched)
        return JsonResponse({"error": "Data tampered or CID not found"}, status=400)

    # Fetch encrypted data from IPFS
    try:
        ipfs_response = requests.get(f"https://gateway.pinata.cloud/ipfs/{record.ipfs_cid}")
        ipfs_response.raise_for_status()
        encrypted_data = ipfs_response.json()
    except Exception as e:
        endtime = time.perf_counter()
        access_time_taken = endtime - start_time
        record.access_time_taken = access_time_taken
        record.hash_matched = True
        record.save(update_fields=["access_time_taken", "hash_matched"])
        print("Access time taken:", access_time_taken)
        print("Hash matched:", record.hash_matched)
        return JsonResponse({"error": f"Failed to fetch IPFS data: {str(e)}"}, status=500)
    
    endtime = time.perf_counter()
    access_time_taken = endtime - start_time
    record.access_time_taken = access_time_taken
    record.hash_matched = True
    record.save(update_fields=["access_time_taken", "hash_matched"])
    print("Access time taken:", access_time_taken)
    print("Hash matched:", record.hash_matched)

    # Return JSON payload matching frontend
    return JsonResponse({
        "verified": True,
        "encrypted_data": encrypted_data,   # JS expects this key
        "cid": record.ipfs_cid,
        "tx_hash": record.blockchain_tx,
        "account_address": record.blockchain_account,
        "access_time_taken": round(access_time_taken, 4),
        "hash_matched": record.hash_matched,
    })

# ------------------------------------------------------------------
# DECRYPT DATA
# ------------------------------------------------------------------

@csrf_exempt
def decrypt_record(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    encrypted_payload = json.loads(request.body)
    decrypted_data = decrypt_json(encrypted_payload)

    return JsonResponse(decrypted_data)
