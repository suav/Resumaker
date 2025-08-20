#!/usr/bin/env python3
"""
Resumaker - Entry point for the resume workshop application

Usage:
    python run.py [--port PORT] [--modular]
    
Options:
    --port PORT    Port to run the server on (default: 8081 for standard, 8083 for modular)
    --modular      Use the modular server architecture
    --help         Show this help message
"""

import sys
import os
import argparse

# Add src directory to path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    parser = argparse.ArgumentParser(description='Resumaker - Modular resume workshop tool')
    parser.add_argument('--port', type=int, help='Port to run the server on')
    parser.add_argument('--modular', action='store_true', help='Use modular server architecture')
    parser.add_argument('--version', action='version', version='Resumaker 1.0.0')
    
    args = parser.parse_args()
    
    if args.modular:
        # Import and run modular server
        from server_modular import ModularResumeWorkshopServer
        port = args.port or 8083
        server = ModularResumeWorkshopServer(port)
        
        print(f"🚀 Starting Resumaker (Modular) on port {port}")
        print(f"📍 Open your browser to: http://localhost:{port}")
        
        if server.start():
            try:
                print("🔄 Server running... Press Ctrl+C to stop")
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down server...")
                server.stop()
    else:
        # Import and run standard server
        import sys
        sys.path.append('src')
        
        # Run the standard server
        port = args.port or 8081
        print(f"🚀 Starting Resumaker (Standard) on port {port}")
        print(f"📍 Open your browser to: http://localhost:{port}")
        
        # Import the server module and run it
        os.chdir('src')
        exec(open('server.py').read())

if __name__ == "__main__":
    main()