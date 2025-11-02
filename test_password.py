#!/usr/bin/env python3
# Quick test for password hashing with "puneeth@2005"

from auth import get_password_hash, verify_password

# Test the password
test_password = "puneeth@2005"
print(f"Testing password: {test_password}")
print(f"Password length: {len(test_password)} characters")
print(f"Password bytes: {len(test_password.encode('utf-8'))} bytes")

# Hash the password
hashed = get_password_hash(test_password)
print(f"Hashed successfully: {hashed[:50]}...")

# Verify the password
is_valid = verify_password(test_password, hashed)
print(f"Password verification: {is_valid}")

print("Password test completed successfully!")