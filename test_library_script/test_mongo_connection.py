"""MongoDB Atlas connection test script.

This script tests the MongoDB Atlas connection and helps diagnose common issues.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    OperationFailure,
    ServerSelectionTimeoutError,
)

load_dotenv()


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_connection():
    """Test MongoDB Atlas connection with detailed diagnostics."""

    print_section("MongoDB Atlas Connection Test")

    # 1. Check environment variable
    print("\n[1] Checking MONGO_URI environment variable...")
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        print("❌ FAIL: MONGO_URI environment variable is not set!")
        print("\nPlease set the MONGO_URI environment variable:")
        print("  export MONGO_URI='mongodb+srv://<username>:<password>@<cluster>/...'")
        print("\nOr create a .env file with:")
        print("  MONGO_URI=mongodb+srv://<username>:<password>@<cluster>/...")
        return False
    else:
        print("✓ MONGO_URI is set")
        # Mask sensitive parts of URI
        masked_uri = mongo_uri
        if "@" in mongo_uri:
            parts = mongo_uri.split("@")
            auth_part = parts[0].split("://")[1] if "://" in parts[0] else parts[0]
            masked_uri = mongo_uri.replace(auth_part, "***:***")
        print(f"  URI: {masked_uri}")

    # 2. Validate URI format
    print("\n[2] Validating URI format...")
    if mongo_uri.startswith("mongodb+srv://"):
        print("✓ Using SRV record (recommended for Atlas)")
    elif mongo_uri.startswith("mongodb://"):
        print("⚠ Using standard mongodb:// protocol")
        print("  For Atlas, consider using mongodb+srv://")
    else:
        print("❌ Invalid URI format!")
        return False

    # 3. Test connection with timeout
    print("\n[3] Testing connection (this may take up to 10 seconds)...")
    client = None

    try:
        # Create client with explicit timeout settings for Atlas
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=10000,  # 10 second timeout
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            retryWrites=True,
        )

        # Force connection with ping
        client.admin.command("ping")
        print("✓ Successfully connected to MongoDB Atlas!")

        # 4. Get server info
        print("\n[4] Getting server information...")
        server_info = client.server_info()
        print(f"✓ MongoDB Version: {server_info.get('version', 'unknown')}")

        # 5. List databases
        print("\n[5] Listing available databases...")
        databases = client.list_database_names()
        print(f"✓ Found {len(databases)} database(s):")
        for db_name in sorted(databases):
            print(f"  - {db_name}")

        # 6. Test database and collection access
        print("\n[6] Testing database and collection access...")
        db_name = "news_org"
        collection_name = "articles"

        db = client[db_name]
        collection = db[collection_name]

        # Count documents
        count = collection.count_documents({})
        print(f"✓ Database '{db_name}' - Collection '{collection_name}'")
        print(f"  Current document count: {count}")

        # 7. Test write operation (optional)
        print("\n[7] Testing write operation...")
        test_doc = {
            "title": "Connection Test",
            "content": "This is a connection test document",
            "url": f"https://test.example.com/{datetime.now().timestamp()}",
            "source": "connection_test",
            "published_at": datetime.now(),
            "crawled_at": datetime.now(),
        }

        try:
            result = collection.insert_one(test_doc)
            print(f"✓ Successfully inserted test document (ID: {result.inserted_id})")

            # Clean up test document
            collection.delete_one({"_id": result.inserted_id})
            print("✓ Test document cleaned up")

        except OperationFailure as e:
            print(f"⚠ Write operation failed (permissions?): {e}")
            print("  Note: Read-only access is sufficient for most operations")

        # 8. Summary
        print_section("Connection Test Summary")
        print("✅ All tests passed! Your MongoDB Atlas connection is working.")
        print("\nConnection details:")
        print(f"  - Host: {client.HOST}")
        print(f"  - Port: {client.PORT}")
        print(f"  - Database: {db_name}")
        print(f"  - Collection: {collection_name}")
        print(f"  - Documents: {count}")

        return True

    except ServerSelectionTimeoutError as e:
        print("\n❌ FAIL: Server selection timeout")
        print("\nPossible causes:")
        print("  1. IP whitelist - Your IP is not in Atlas whitelist")
        print("     → Go to Atlas > Network Access > Add IP Address")
        print("  2. Incorrect username/password in connection string")
        print("  3. Cluster not running or paused")
        print(f"\nError details: {e}")
        return False

    except ConnectionFailure as e:
        print("\n❌ FAIL: Connection failed")
        print(f"\nError details: {e}")
        print("\nPossible causes:")
        print("  - Network connectivity issues")
        print("  - Firewall blocking connection")
        print("  - Incorrect connection string format")
        return False

    except OperationFailure as e:
        print("\n❌ FAIL: Authentication failed")
        print(f"\nError details: {e}")
        print("\nPossible causes:")
        print("  - Incorrect username or password")
        print("  - User doesn't have permission to access this database")
        print("  - Database user not created in Atlas")
        return False

    except Exception as e:
        print("\n❌ FAIL: Unexpected error")
        print(f"\nError type: {type(e).__name__}")
        print(f"Error details: {e}")
        return False

    finally:
        if client:
            client.close()
            print("\n✓ Connection closed")


def show_troubleshooting():
    """Show troubleshooting tips."""
    print_section("Troubleshooting Tips")

    print("""
Common MongoDB Atlas Connection Issues:

1. IP Whitelist Not Set
   → Go to: Atlas Console > Database > Network Access
   → Click "Add IP Address" and add your current IP
   → Or use "Allow Access from Anywhere" (0.0.0.0/0) for testing

2. Incorrect Connection String
   → Go to: Atlas Console > Database > Connect > Connect your application
   → Select your Python version
   → Copy the connection string
   → Replace <password> with your actual password

3. Database User Not Created
   → Go to: Atlas Console > Database > Database Access
   → Click "Add New Database User"
   → Set username and password
   → Grant required permissions (Read and Write)

4. Network/Firewall Issues
   → Ensure outbound connections to MongoDB ports (27017-27019) are allowed
   → Check if corporate firewall is blocking the connection

5. Cluster Paused
   → Go to: Atlas Console > Database > Clusters
   → Resume the cluster if paused
    """)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test MongoDB Atlas connection")
    parser.add_argument(
        "--troubleshoot",
        action="store_true",
        help="Show troubleshooting tips without testing",
    )

    args = parser.parse_args()

    if args.troubleshoot:
        show_troubleshooting()
    else:
        success = test_connection()
        sys.exit(0 if success else 1)
