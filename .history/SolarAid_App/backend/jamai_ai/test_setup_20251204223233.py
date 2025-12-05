"""
Test script for Voice-to-RAG functionality
Run this script to verify your setup is working correctly
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv()

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("\n" + "="*60)
    print("TESTING ENVIRONMENT VARIABLES")
    print("="*60)
    
    required_vars = {
        'ASSEMBLYAI_API_KEY': 'AssemblyAI API Key',
        'VITE_JAM_API_KEY': 'JamAI API Key',
        'VITE_JAM_PROJECT_ID': 'JamAI Project ID'
    }
    
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + '...' if len(value) > 8 else value
            print(f"✅ {description}: {masked}")
        else:
            print(f"❌ {description}: NOT FOUND")
            all_present = False
    
    return all_present


def test_imports():
    """Test if all required libraries can be imported"""
    print("\n" + "="*60)
    print("TESTING LIBRARY IMPORTS")
    print("="*60)
    
    libraries = {
        'assemblyai': 'AssemblyAI',
        'jamaibase': 'JamAI Base SDK',
        'flask': 'Flask',
        'dotenv': 'Python-dotenv'
    }
    
    all_imported = True
    for module, name in libraries.items():
        try:
            __import__(module)
            print(f"✅ {name}: Installed")
        except ImportError:
            print(f"❌ {name}: NOT INSTALLED")
            all_imported = False
    
    return all_imported


def test_audio_bridge_import():
    """Test if audio_bridge module can be imported"""
    print("\n" + "="*60)
    print("TESTING AUDIO BRIDGE MODULE")
    print("="*60)
    
    try:
        from backend.jamai_ai.audio_bridge import (
            transcribe_audio,
            upload_to_knowledge_base,
            process_enquiry,
            query_jamai_chat
        )
        print("✅ All functions imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_text_processing():
    """Test text processing functionality"""
    print("\n" + "="*60)
    print("TESTING TEXT PROCESSING")
    print("="*60)
    
    try:
        from backend.jamai_ai.audio_bridge import process_enquiry
        
        test_text = "What is my donation impact?"
        result = process_enquiry(test_text, input_type='text')
        
        if result.get('success'):
            print(f"✅ Text processing successful")
            print(f"   Query: {result.get('text')[:50]}...")
            return True
        else:
            print(f"❌ Text processing failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during text processing: {e}")
        return False


def test_jamai_connection():
    """Test connection to JamAI API"""
    print("\n" + "="*60)
    print("TESTING JAMAI CONNECTION")
    print("="*60)
    
    try:
        from backend.jamai_ai.audio_bridge import query_jamai_chat
        
        test_query = "Hello, this is a test query."
        result = query_jamai_chat(test_query)
        
        if result.get('success'):
            print(f"✅ JamAI connection successful")
            print(f"   Response preview: {result.get('response')[:100]}...")
            return True
        else:
            print(f"❌ JamAI connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to JamAI: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and provide summary"""
    print("\n" + "🚀 " + "="*56 + " 🚀")
    print("   VOICE-TO-RAG SETUP VERIFICATION")
    print("🚀 " + "="*56 + " 🚀")
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Library Imports", test_imports),
        ("Audio Bridge Module", test_audio_bridge_import),
        ("Text Processing", test_text_processing),
        ("JamAI Connection", test_jamai_connection),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Your Voice-to-RAG setup is ready.")
        print("\nNext steps:")
        print("1. Start the Flask server: python backend/server.py")
        print("2. Test the endpoint: POST http://127.0.0.1:5000/api/chat-enquiry")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("1. Install missing libraries: pip install -r requirements.txt")
        print("2. Set environment variables in .env file")
        print("3. Verify API keys are correct")
        print("4. Check JamAI table setup (meeting_transcripts, Chatbox)")


if __name__ == "__main__":
    run_all_tests()
