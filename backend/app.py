from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from datetime import datetime
import uuid
import re
import json
import os
import time

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Your Google Form link
GOOGLE_FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSeeM-BxM0i6WwCyjZx0SwZvnNTiCaOFF4HXcu0tZyy9284fPw/viewform?usp=publish-editor"

# In-memory storage
users_db = []
events_db = []
voice_calls_db = []
current_id = 1

# Helper functions
def validate_skasc_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@skasc\.ac\.in$'
    return re.match(pattern, email) is not None

def find_user_by_email(email):
    return next((u for u in users_db if u['email'] == email), None)

def find_user_by_id(user_id):
    return next((u for u in users_db if u['id'] == user_id), None)

def find_event_by_id(event_id):
    return next((e for e in events_db if e['id'] == event_id), None)

# Serve frontend
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Auth endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').lower()
        password = data.get('password', '')
        name = data.get('name', '')
        
        if not validate_skasc_email(email):
            return jsonify({'error': 'Only @skasc.ac.in emails allowed'}), 400
        
        if find_user_by_email(email):
            return jsonify({'error': 'Email already registered'}), 400
        
        global current_id
        user = {
            'id': current_id,
            'email': email,
            'name': name,
            'password': password,  # In production, hash this!
            'college': 'SKASC',
            'created_at': datetime.utcnow().isoformat()
        }
        
        users_db.append(user)
        current_id += 1
        
        # Generate simple token
        token = f"token-{user['id']}-{uuid.uuid4().hex[:16]}"
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'college': user['college']
            }
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').lower()
        password = data.get('password', '')
        
        if not validate_skasc_email(email):
            return jsonify({'error': 'Only @skasc.ac.in emails allowed'}), 400
        
        user = find_user_by_email(email)
        if not user or user['password'] != password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate simple token
        token = f"token-{user['id']}-{uuid.uuid4().hex[:16]}"
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'college': user['college']
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        # Extract user ID from token
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                user_id = int(token.split('-')[1])
                user = find_user_by_id(user_id)
                if user:
                    return jsonify({
                        'id': user['id'],
                        'email': user['email'],
                        'name': user['name'],
                        'college': user['college']
                    }), 200
            except Exception as e:
                print(f"Token parse error: {str(e)}")
        
        return jsonify({'error': 'Invalid token'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Event endpoints
@app.route('/api/events/create', methods=['POST'])
def create_event():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        # Verify token
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid token format'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['event_type', 'event_name', 'team_limit', 'theme']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract user ID from token
        token = auth_header[7:]
        try:
            user_id = int(token.split('-')[1])
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Create event with your Google Form link
        event = {
            'id': len(events_db) + 1,
            'user_id': user_id,
            'event_type': data.get('event_type'),
            'event_name': data.get('event_name'),
            'team_limit': data.get('team_limit'),
            'theme': data.get('theme'),
            'problem_statement': data.get('problem_statement', ''),
            'prizes': data.get('prizes', ''),
            'rules': data.get('rules', ''),
            'google_form_link': GOOGLE_FORM_LINK,  # Use your specific link
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Add additional fields
        if data.get('start_date'):
            event['start_date'] = data.get('start_date')
        if data.get('end_date'):
            event['end_date'] = data.get('end_date')
        
        events_db.append(event)
        
        # Log the created event
        print(f"\n{'='*50}")
        print("EVENT CREATED SUCCESSFULLY!")
        print(f"{'='*50}")
        print(f"Event Name: {event['event_name']}")
        print(f"Event Type: {event['event_type']}")
        print(f"Theme: {event['theme']}")
        print(f"Team Limit: {event['team_limit']}")
        print(f"Google Form: {event['google_form_link']}")
        print(f"{'='*50}\n")
        
        return jsonify({
            'message': 'Event created successfully',
            'event': {
                'id': event['id'],
                'event_name': event['event_name'],
                'event_type': event['event_type'],
                'google_form_link': event['google_form_link'],
                'created_at': event['created_at']
            }
        }), 201
        
    except Exception as e:
        print(f"Event creation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/my-events', methods=['GET'])
def get_my_events():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid token format'}), 401
        
        # Extract user ID from token
        token = auth_header[7:]
        try:
            user_id = int(token.split('-')[1])
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Filter events by user_id
        user_events = [e for e in events_db if e['user_id'] == user_id]
        
        events_list = [{
            'id': e['id'],
            'event_type': e['event_type'],
            'event_name': e['event_name'],
            'theme': e['theme'],
            'team_limit': e['team_limit'],
            'google_form_link': e['google_form_link'],
            'created_at': e['created_at']
        } for e in user_events]
        
        return jsonify({'events': events_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Voice endpoints
@app.route('/api/voice/call', methods=['POST'])
def initiate_call():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid token format'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        event_id = data.get('event_id')
        college_name = data.get('college_name')
        phone_number = data.get('phone_number')
        
        if not all([event_id, college_name, phone_number]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find event
        event = find_event_by_id(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Create voice call record
        voice_call = {
            'id': len(voice_calls_db) + 1,
            'event_id': event_id,
            'college_name': college_name,
            'phone_number': phone_number,
            'call_status': 'completed',
            'called_at': datetime.utcnow().isoformat()
        }
        
        voice_calls_db.append(voice_call)
        
        # Generate voice message
        message = f"Hi, I'm calling from {event['event_name']}. We're hosting a {event['event_type']} competition on the theme: {event['theme']}. We would like to invite participants from {college_name}. For more details, please visit our registration form at: {event['google_form_link']}. Thank you!"
        
        print(f"\n{'='*50}")
        print("VOICE AGENT CALL INITIATED!")
        print(f"{'='*50}")
        print(f"To: {college_name}")
        print(f"Phone: {phone_number}")
        print(f"For Event: {event['event_name']}")
        print(f"Message: {message}")
        print(f"{'='*50}\n")
        
        return jsonify({
            'message': 'Voice call initiated successfully',
            'call_id': voice_call['id'],
            'status': voice_call['call_status'],
            'event_name': event['event_name'],
            'college_name': college_name,
            'voice_message': message
        }), 200
        
    except Exception as e:
        print(f"Voice call error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Design endpoints
@app.route('/api/design/poster', methods=['POST'])
def generate_poster():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        data = request.get_json()
        poster_id = str(uuid.uuid4())[:8]
        
        print(f"\n{'='*50}")
        print("POSTER GENERATED SUCCESSFULLY!")
        print(f"{'='*50}")
        print(f"Poster ID: {poster_id}")
        if data.get('event_name'):
            print(f"Event: {data.get('event_name')}")
        print(f"{'='*50}\n")
        
        return jsonify({
            'message': 'Poster generated successfully',
            'poster_id': poster_id,
            'download_url': f'/api/download/poster/{poster_id}',
            'preview_url': f'/api/preview/poster/{poster_id}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/design/certificate', methods=['POST'])
def generate_certificate():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        data = request.get_json()
        certificate_id = str(uuid.uuid4())[:8]
        
        print(f"\n{'='*50}")
        print("CERTIFICATE GENERATED SUCCESSFULLY!")
        print(f"{'='*50}")
        print(f"Certificate ID: {certificate_id}")
        if data.get('participant_name'):
            print(f"For: {data.get('participant_name')}")
        print(f"{'='*50}\n")
        
        return jsonify({
            'message': 'Certificate generated successfully',
            'certificate_id': certificate_id,
            'download_url': f'/api/download/certificate/{certificate_id}',
            'preview_url': f'/api/preview/certificate/{certificate_id}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Download endpoints (mock)
@app.route('/api/download/poster/<poster_id>', methods=['GET'])
def download_poster(poster_id):
    return jsonify({
        'message': f'Downloading poster {poster_id}',
        'status': 'success'
    })

@app.route('/api/download/certificate/<certificate_id>', methods=['GET'])
def download_certificate(certificate_id):
    return jsonify({
        'message': f'Downloading certificate {certificate_id}',
        'status': 'success'
    })

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'SKASC Event Manager',
        'version': '1.0.0',
        'google_form_link': GOOGLE_FORM_LINK,
        'users_count': len(users_db),
        'events_count': len(events_db),
        'voice_calls_count': len(voice_calls_db)
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("SKASC EVENT MANAGEMENT SYSTEM")
    print("=" * 60)
    print("\nStarting server...")
    print("Access the application at: http://localhost:5000")
    print("\nFeatures:")
    print("- SKASC email authentication (@skasc.ac.in)")
    print("- Event creation (Hackathon, Paper Presentation, Ideathon)")
    print(f"- Google Form: {GOOGLE_FORM_LINK}")
    print("- Poster and certificate generation")
    print("- Voice agent for participant outreach")
    print("\nAPI Endpoints:")
    print("- POST /api/auth/register")
    print("- POST /api/auth/login")
    print("- POST /api/events/create")
    print("- GET  /api/events/my-events")
    print("- POST /api/voice/call")
    print("- POST /api/design/poster")
    print("- POST /api/design/certificate")
    print("\nServer is running...")
    print("=" * 60)
    
    app.run(debug=True, port=5000)