# Sample FAQ Data
# For testing AI intelligent customer service functionality

from models import db, FAQ
from app import app

def load_sample_faqs():
    """Load sample FAQ data into database"""
    
    sample_faqs = [
        {
            "question": "How do I apply for vacation leave?",
            "answer": "You can apply for vacation leave through the HR portal under 'Leave Management'. Log in with your employee credentials, select 'Request Leave', choose 'Vacation', and fill in the required dates and details."
        },
        {
            "question": "How to reset my password?",
            "answer": "To reset your password, go to the IT self-service portal and click 'Reset Password'. You can also contact the IT helpdesk at ext. 1234 or email it-support@company.com."
        },
        {
            "question": "Where can I find my payroll information?",
            "answer": "Your payroll information is available in the Employee Self-Service portal under 'Payroll & Benefits'. You can view pay stubs, tax documents, and update direct deposit information there."
        },
        {
            "question": "What are the company working hours?",
            "answer": "Standard working hours are Monday to Friday, 9:00 AM to 5:00 PM. Some departments may have flexible hours. Please check with your manager for specific arrangements."
        },
        {
            "question": "How do I access the company VPN?",
            "answer": "To access the company VPN, download the VPN client from the IT portal, use your domain credentials to log in. For setup assistance, contact IT support at it-support@company.com."
        },
        {
            "question": "What is the dress code policy?",
            "answer": "Our dress code is business casual. Jeans are allowed on Fridays. For client meetings, business formal attire is required. Please refer to the employee handbook for detailed guidelines."
        },
        {
            "question": "How to book a meeting room?",
            "answer": "Meeting rooms can be booked through Outlook calendar or the room booking system on the intranet. Rooms are available on a first-come, first-served basis. Please cancel if you no longer need the room."
        },
        {
            "question": "What are the health insurance benefits?",
            "answer": "We offer comprehensive health insurance including medical, dental, and vision coverage. Details are available in the Benefits section of the HR portal. Open enrollment is in November each year."
        },
        {
            "question": "How do I report a technical issue?",
            "answer": "Technical issues can be reported through the IT helpdesk portal, by calling ext. 1234, or emailing it-support@company.com. Please provide detailed information about the issue for faster resolution."
        },
        {
            "question": "What is the remote work policy?",
            "answer": "Remote work is available 2-3 days per week depending on your role and manager approval. Please discuss with your manager and submit a remote work request through HR for approval."
        },
        {
            "question": "How to access company training programs?",
            "answer": "Training programs are available through the Learning Management System (LMS) on the company intranet. You can browse courses, enroll, and track your progress. Some courses require manager approval."
        },
        {
            "question": "What is the expense reimbursement process?",
            "answer": "Submit expense reports through the Finance portal with receipts attached. Business expenses are typically reimbursed within 2 weeks. For questions, contact finance@company.com."
        }
    ]
    
    with app.app_context():
        # Check if data already exists
        existing_count = FAQ.query.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} FAQ records")
            return
        
        # Add sample data
        for faq_data in sample_faqs:
            faq = FAQ(question=faq_data["question"], answer=faq_data["answer"])
            db.session.add(faq)
        
        db.session.commit()
        print(f"Successfully loaded {len(sample_faqs)} sample FAQ records")

if __name__ == '__main__':
    load_sample_faqs()