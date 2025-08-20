#!/usr/bin/env python3
"""
PostgreSQL Connection Test Script

This script tests the PostgreSQL database connection and verifies
that all tables can be created successfully.

Usage:
    python test_postgresql_connection.py

Prerequisites:
    1. Configure your PostgreSQL connection in .env file
    2. Ensure PostgreSQL database is accessible
"""

import os
import sys
from datetime import datetime

try:
    from app import app, db, FAQ, Log, ConversationSession, Feedback, User
    from config import Config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're in the correct directory and all dependencies are installed.")
    sys.exit(1)

def test_database_connection():
    """Test basic database connection"""
    print("Testing PostgreSQL database connection...")
    
    try:
        with app.app_context():
            # Test basic connection
            result = db.engine.execute(db.text('SELECT 1')).scalar()
            if result == 1:
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Database connection failed - unexpected result")
                return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_table_creation():
    """Test table creation"""
    print("\nTesting table creation...")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['faqs', 'log', 'conversation_sessions', 'feedback', 'users']
            
            print("\nVerifying tables:")
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
                    return False
            
            return True
            
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

def test_basic_operations():
    """Test basic CRUD operations"""
    print("\nTesting basic database operations...")
    
    try:
        with app.app_context():
            # Test FAQ creation
            test_faq = FAQ(
                question="Test question for PostgreSQL",
                answer="Test answer for PostgreSQL connection"
            )
            db.session.add(test_faq)
            db.session.commit()
            print("✅ FAQ creation successful")
            
            # Test FAQ retrieval
            retrieved_faq = FAQ.query.filter_by(question="Test question for PostgreSQL").first()
            if retrieved_faq:
                print("✅ FAQ retrieval successful")
            else:
                print("❌ FAQ retrieval failed")
                return False
            
            # Test FAQ update
            retrieved_faq.answer = "Updated test answer"
            db.session.commit()
            print("✅ FAQ update successful")
            
            # Test FAQ deletion
            db.session.delete(retrieved_faq)
            db.session.commit()
            print("✅ FAQ deletion successful")
            
            return True
            
    except Exception as e:
        print(f"❌ Basic operations failed: {e}")
        return False

def display_configuration():
    """Display current database configuration"""
    print("\nCurrent Database Configuration:")
    print("==============================")
    
    config = Config()
    
    # Mask sensitive information
    db_uri = config.SQLALCHEMY_DATABASE_URI
    if db_uri:
        # Hide password in connection string
        if '@' in db_uri and ':' in db_uri:
            parts = db_uri.split('@')
            if len(parts) == 2:
                user_pass = parts[0].split('//')[-1]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    masked_uri = db_uri.replace(user_pass, f"{user}:****")
                    print(f"Database URI: {masked_uri}")
                else:
                    print(f"Database URI: {db_uri}")
            else:
                print(f"Database URI: {db_uri}")
        else:
            print(f"Database URI: {db_uri}")
    else:
        print("Database URI: Not configured")
    
    print(f"Engine Options: {config.SQLALCHEMY_ENGINE_OPTIONS}")
    print(f"Track Modifications: {config.SQLALCHEMY_TRACK_MODIFICATIONS}")

def main():
    print("PostgreSQL Connection Test")
    print("==========================")
    
    # Display configuration
    display_configuration()
    
    # Test connection
    if not test_database_connection():
        print("\n❌ Connection test failed. Please check your configuration.")
        return False
    
    # Test table creation
    if not test_table_creation():
        print("\n❌ Table creation test failed.")
        return False
    
    # Test basic operations
    if not test_basic_operations():
        print("\n❌ Basic operations test failed.")
        return False
    
    print("\n🎉 All tests passed! PostgreSQL is configured correctly.")
    print("\nYour application is ready to use PostgreSQL database.")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)