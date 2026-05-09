"""Test script for Supabase auth with Google token"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_with_token(token: str):
    """Test endpoints with a valid Supabase access token"""
    headers = {"Authorization": f"Bearer {token}"}

    print("\n=== Testing with token ===")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Me: {response.status_code}")
    if response.ok:
        print(f"  User: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"  Error: {response.json()}")

    response = requests.get(f"{BASE_URL}/auth/session", headers=headers)
    print(f"\nSession: {response.status_code}")
    if response.ok:
        print(f"  Session: {json.dumps(response.json(), indent=2)}")

def main():
    print("=== Supabase Auth Test ===\n")

    # Test health
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.status_code} - {response.json()}")

    # Test unauthenticated (should fail)
    print("\n=== Testing without token ===")
    response = requests.get(f"{BASE_URL}/auth/me")
    print(f"Me (no auth): {response.status_code} - {response.json()}")

    # Get token from frontend session file
    token_file = os.path.expanduser("~/Library/Application Support/Arc/Session State/session.json")
    if os.path.exists(token_file):
        print(f"\nFound session file: {token_file}")
    else:
        print("\n=== Instructions ===")
        print("1. Open the frontend in browser (http://localhost:4321)")
        print("2. Login with Google")
        print("3. Open DevTools -> Application -> Local Storage")
        print("4. Find 'supabase.auth.token' and copy the access_token")
        print("5. Run: test_with_token('your-token-here')")

if __name__ == "__main__":
    main()