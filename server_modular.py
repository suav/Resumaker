#!/usr/bin/env python3
"""
Modular Resume Workshop Server
Slim server with component-based architecture and lazy loading
"""

import os
import socketserver
import threading
import time
from datetime import datetime

# Import modular components
from backend.core.config import WORKSHOP_DIR
PORT = 8083  # Use available port for modular server
from backend.core.router import ModularHandler


class ModularResumeWorkshopServer:
    """Modular server with lazy-loaded components"""
    
    def __init__(self, port=PORT):
        self.port = port
        self.httpd = None
        self.server_thread = None
    
    def start(self):
        """Start the modular server"""
        try:
            self.httpd = socketserver.TCPServer(("", self.port), ModularHandler)
            self.server_thread = threading.Thread(target=self.httpd.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            print(f"🚀 Modular Resume Workshop Server started!")
            print(f"📍 Server running at: http://localhost:{self.port}")
            print(f"🏠 Workshop home: http://localhost:{self.port}")
            print(f"📄 Frontend: http://localhost:{self.port}/frontend/")
            print(f"🔧 API endpoints: http://localhost:{self.port}/api/")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📁 Working directory: {WORKSHOP_DIR}")
            print("\n" + "="*60)
            print("🧩 Modular architecture active:")
            print("   - Lazy-loaded API components")
            print("   - Conditional frontend modules") 
            print("   - Background job processing")
            print("   - Component-based routing")
            print("="*60)
            
            return True
            
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"⚠️  Port {self.port} is already in use!")
                print(f"🔗 Workshop likely running at: http://localhost:{self.port}")
                return False
            else:
                print(f"❌ Error starting modular server: {e}")
                return False
    
    def stop(self):
        """Stop the server"""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            print(f"🛑 Modular server stopped")
    
    def is_running(self):
        """Check if server is running"""
        return self.httpd is not None and self.server_thread.is_alive()


def create_directories():
    """Create necessary directories"""
    directories = [
        'agent_workspace/templates', 
        'agent_workspace/variants', 
        'agent_workspace/output', 
        'agent_workspace/scripts',
        'agent_workspace/job_descriptions',
        'agent_workspace/quality_feedback',
        'scripts',
        'frontend/components',
        'frontend/styles',
        'frontend/services'
    ]
    
    for subdir in directories:
        os.makedirs(os.path.join(WORKSHOP_DIR, subdir), exist_ok=True)


if __name__ == "__main__":
    print("🧩 Starting Modular Resume Workshop Server...")
    
    # Create directories
    create_directories()
    
    # Start modular server
    server = ModularResumeWorkshopServer(PORT)
    
    if server.start():
        try:
            print("🔄 Modular server running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down modular server...")
            server.stop()
    else:
        print("⚠️  Server may already be running. Try visiting the workshop URL above.")
        print("💡 To switch to modular mode, stop the existing server first.")