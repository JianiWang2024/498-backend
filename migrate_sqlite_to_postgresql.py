#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script

This script helps migrate data from an existing SQLite database to PostgreSQL.
Run this script only if you have existing SQLite data that needs to be migrated.

Usage:
    python migrate_sqlite_to_postgresql.py

Prerequisites:
    1. Configure your PostgreSQL connection in .env file
    2. Ensure the SQLite database file (faq.db) exists
    3. Make sure PostgreSQL database is accessible
"""

import sqlite3
import json
import os
from datetime import datetime
from app import app, db, FAQ, Log, ConversationSession, Feedback, User

def export_sqlite_data(sqlite_db_path='faq.db'):
    """Export data from SQLite database to JSON files"""
    if not os.path.exists(sqlite_db_path):
        print(f"SQLite database {sqlite_db_path} not found.")
        return False
    
    print(f"Exporting data from {sqlite_db_path}...")
    
    try:
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()
        
        # Export FAQs
        cursor.execute('SELECT * FROM faqs')
        faqs = cursor.fetchall()
        with open('faqs_export.json', 'w') as f:
            json.dump(faqs, f, indent=2)
        print(f"Exported {len(faqs)} FAQs")
        
        # Export Logs
        try:
            cursor.execute('SELECT * FROM log')
            logs = cursor.fetchall()
            with open('logs_export.json', 'w') as f:
                json.dump(logs, f, indent=2, default=str)
            print(f"Exported {len(logs)} logs")
        except sqlite3.OperationalError:
            print("No logs table found")
        
        # Export Users
        try:
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
            with open('users_export.json', 'w') as f:
                json.dump(users, f, indent=2, default=str)
            print(f"Exported {len(users)} users")
        except sqlite3.OperationalError:
            print("No users table found")
        
        # Export Sessions
        try:
            cursor.execute('SELECT * FROM conversation_sessions')
            sessions = cursor.fetchall()
            with open('sessions_export.json', 'w') as f:
                json.dump(sessions, f, indent=2, default=str)
            print(f"Exported {len(sessions)} sessions")
        except sqlite3.OperationalError:
            print("No conversation_sessions table found")
        
        # Export Feedback
        try:
            cursor.execute('SELECT * FROM feedback')
            feedback = cursor.fetchall()
            with open('feedback_export.json', 'w') as f:
                json.dump(feedback, f, indent=2, default=str)
            print(f"Exported {len(feedback)} feedback entries")
        except sqlite3.OperationalError:
            print("No feedback table found")
        
        conn.close()
        print("SQLite data export completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error exporting SQLite data: {e}")
        return False

def import_to_postgresql():
    """Import data from JSON files to PostgreSQL"""
    print("Importing data to PostgreSQL...")
    
    try:
        with app.app_context():
            # Import FAQs
            if os.path.exists('faqs_export.json'):
                with open('faqs_export.json', 'r') as f:
                    faqs_data = json.load(f)
                
                for faq_data in faqs_data:
                    faq = FAQ(id=faq_data[0], question=faq_data[1], answer=faq_data[2])
                    db.session.merge(faq)  # Use merge to handle existing IDs
                
                db.session.commit()
                print(f"Imported {len(faqs_data)} FAQs")
            
            # Import Users
            if os.path.exists('users_export.json'):
                with open('users_export.json', 'r') as f:
                    users_data = json.load(f)
                
                for user_data in users_data:
                    user = User(
                        id=user_data[0],
                        username=user_data[1],
                        email=user_data[2],
                        password_hash=user_data[3],
                        role=user_data[4] if len(user_data) > 4 else 'employee',
                        created_at=datetime.fromisoformat(user_data[5]) if len(user_data) > 5 else datetime.utcnow()
                    )
                    db.session.merge(user)
                
                db.session.commit()
                print(f"Imported {len(users_data)} users")
            
            # Import Sessions
            if os.path.exists('sessions_export.json'):
                with open('sessions_export.json', 'r') as f:
                    sessions_data = json.load(f)
                
                for session_data in sessions_data:
                    session = ConversationSession(
                        id=session_data[0],
                        session_id=session_data[1],
                        user_id=session_data[2],
                        start_time=datetime.fromisoformat(session_data[3]) if session_data[3] else datetime.utcnow(),
                        end_time=datetime.fromisoformat(session_data[4]) if session_data[4] else None,
                        is_active=bool(session_data[5]) if len(session_data) > 5 else True,
                        question_count=session_data[6] if len(session_data) > 6 else 0
                    )
                    db.session.merge(session)
                
                db.session.commit()
                print(f"Imported {len(sessions_data)} sessions")
            
            # Import Logs
            if os.path.exists('logs_export.json'):
                with open('logs_export.json', 'r') as f:
                    logs_data = json.load(f)
                
                for log_data in logs_data:
                    log = Log(
                        id=log_data[0],
                        question=log_data[1],
                        keywords=log_data[2] if len(log_data) > 2 else None,
                        category=log_data[3] if len(log_data) > 3 else None,
                        session_id=log_data[4] if len(log_data) > 4 else None,
                        is_session_end=bool(log_data[5]) if len(log_data) > 5 else False,
                        timestamp=datetime.fromisoformat(log_data[6]) if len(log_data) > 6 else datetime.utcnow()
                    )
                    db.session.merge(log)
                
                db.session.commit()
                print(f"Imported {len(logs_data)} logs")
            
            # Import Feedback
            if os.path.exists('feedback_export.json'):
                with open('feedback_export.json', 'r') as f:
                    feedback_data = json.load(f)
                
                for fb_data in feedback_data:
                    feedback = Feedback(
                        id=fb_data[0],
                        satisfied=bool(fb_data[1]),
                        session_id=fb_data[2] if len(fb_data) > 2 else None,
                        rating=fb_data[3] if len(fb_data) > 3 else None,
                        comment=fb_data[4] if len(fb_data) > 4 else None,
                        timestamp=datetime.fromisoformat(fb_data[5]) if len(fb_data) > 5 else datetime.utcnow()
                    )
                    db.session.merge(feedback)
                
                db.session.commit()
                print(f"Imported {len(feedback_data)} feedback entries")
            
            print("PostgreSQL data import completed successfully!")
            return True
            
    except Exception as e:
        print(f"Error importing to PostgreSQL: {e}")
        return False

def cleanup_export_files():
    """Clean up temporary export files"""
    export_files = [
        'faqs_export.json',
        'logs_export.json', 
        'users_export.json',
        'sessions_export.json',
        'feedback_export.json'
    ]
    
    for file in export_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")

def main():
    print("SQLite to PostgreSQL Migration Tool")
    print("====================================")
    
    # Check if SQLite database exists
    if not os.path.exists('faq.db'):
        print("No SQLite database (faq.db) found. Migration not needed.")
        return
    
    print("Found SQLite database. Starting migration...")
    
    # Step 1: Export from SQLite
    if not export_sqlite_data():
        print("Failed to export SQLite data. Aborting migration.")
        return
    
    # Step 2: Import to PostgreSQL
    if not import_to_postgresql():
        print("Failed to import to PostgreSQL. Export files preserved for manual review.")
        return
    
    # Step 3: Clean up
    print("\nMigration completed successfully!")
    response = input("Do you want to remove the temporary export files? (y/N): ")
    if response.lower() in ['y', 'yes']:
        cleanup_export_files()
    
    print("\nMigration process finished.")
    print("You can now safely remove the SQLite database file (faq.db) if desired.")

if __name__ == '__main__':
    main()