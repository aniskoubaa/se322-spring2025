"""
Security utilities for the IoT security project.
Provides functions for encryption, decryption, and message authentication.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# This is a demo key - in a real application, this would be securely stored
# and not hardcoded in the source code
DEFAULT_SECRET_KEY = b'IoTSecurityDemoKey12345678901234'  # 32 bytes for AES-256

# Device credentials (for demo purposes only)
# In a real application, this would be stored securely
DEVICE_CREDENTIALS = {
    "farm_sensor_01": {
        "key": "sensor01_secret_key",
        "permissions": ["publish_data"]
    },
    "admin_device": {
        "key": "admin_secret_key",
        "permissions": ["publish_data", "send_commands"]
    }
}

def generate_iv():
    """Generate a random initialization vector for AES encryption."""
    return os.urandom(16)  # 16 bytes IV for AES

def encrypt_message(message_dict, key=DEFAULT_SECRET_KEY):
    """
    Encrypt a dictionary message using AES-256-CBC.
    
    Args:
        message_dict (dict): The message to encrypt
        key (bytes): The encryption key
        
    Returns:
        dict: A dictionary with the encrypted message and metadata
    """
    # Convert dictionary to JSON string
    plaintext = json.dumps(message_dict).encode('utf-8')
    
    # Pad the plaintext
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()
    
    # Generate IV
    iv = generate_iv()
    
    # Create the cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    
    # Encrypt the padded plaintext
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    
    # Create the result dictionary
    encrypted_message = {
        "encrypted_data": base64.b64encode(ciphertext).decode('utf-8'),
        "iv": base64.b64encode(iv).decode('utf-8'),
        "timestamp": time.time(),
        "is_encrypted": True
    }
    
    return encrypted_message

def decrypt_message(encrypted_message, key=DEFAULT_SECRET_KEY):
    """
    Decrypt an encrypted message using AES-256-CBC.
    
    Args:
        encrypted_message (dict): The encrypted message dictionary
        key (bytes): The decryption key
        
    Returns:
        dict: The decrypted message as a dictionary
    """
    # Extract the ciphertext and IV
    ciphertext = base64.b64decode(encrypted_message["encrypted_data"])
    iv = base64.b64decode(encrypted_message["iv"])
    
    # Create the cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    
    # Decrypt the ciphertext
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Unpad the plaintext
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    # Convert JSON string back to dictionary
    return json.loads(plaintext.decode('utf-8'))

def sign_message(message, device_id, timestamp=None):
    """
    Sign a message using HMAC-SHA256.
    
    Args:
        message (dict): The message to sign
        device_id (str): The ID of the device sending the message
        timestamp (float, optional): Custom timestamp or current time if None
        
    Returns:
        dict: The original message with signature and metadata added
    """
    if device_id not in DEVICE_CREDENTIALS:
        raise ValueError(f"Unknown device ID: {device_id}")
    
    device_key = DEVICE_CREDENTIALS[device_id]["key"].encode('utf-8')
    
    # Add metadata
    if timestamp is None:
        timestamp = time.time()
        
    message_copy = message.copy()
    message_copy["device_id"] = device_id
    message_copy["timestamp"] = timestamp
    
    # Create the signature
    message_str = json.dumps(message_copy, sort_keys=True)
    signature = hmac.new(
        device_key, 
        message_str.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    # Add the signature to the message
    message_copy["signature"] = signature
    
    return message_copy

def verify_signature(signed_message):
    """
    Verify the signature of a signed message.
    
    Args:
        signed_message (dict): The signed message to verify
        
    Returns:
        bool: True if the signature is valid, False otherwise
    """
    # Extract the device ID and signature
    device_id = signed_message.get("device_id")
    signature = signed_message.get("signature")
    
    if device_id is None or signature is None:
        return False
    
    if device_id not in DEVICE_CREDENTIALS:
        return False
    
    # Create a copy of the message without the signature
    message_copy = signed_message.copy()
    message_copy.pop("signature")
    
    # Create the expected signature
    device_key = DEVICE_CREDENTIALS[device_id]["key"].encode('utf-8')
    message_str = json.dumps(message_copy, sort_keys=True)
    expected_signature = hmac.new(
        device_key, 
        message_str.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    # Compare the signatures
    return hmac.compare_digest(signature, expected_signature)

def is_message_recent(signed_message, max_age_seconds=60):
    """
    Check if a message's timestamp is recent enough.
    
    Args:
        signed_message (dict): The signed message to check
        max_age_seconds (int): Maximum allowed age in seconds
        
    Returns:
        bool: True if the message is recent, False otherwise
    """
    timestamp = signed_message.get("timestamp")
    
    if timestamp is None:
        return False
    
    current_time = time.time()
    message_age = current_time - timestamp
    
    return message_age <= max_age_seconds

def validate_message_permissions(signed_message, required_permission):
    """
    Check if the device sending the message has the required permission.
    
    Args:
        signed_message (dict): The signed message to check
        required_permission (str): The required permission
        
    Returns:
        bool: True if the device has the required permission, False otherwise
    """
    device_id = signed_message.get("device_id")
    
    if device_id is None or device_id not in DEVICE_CREDENTIALS:
        return False
    
    return required_permission in DEVICE_CREDENTIALS[device_id]["permissions"] 