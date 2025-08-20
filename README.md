# Resumaker

A powerful, modular resume workshop tool for creating, managing, and optimizing resume variants with AI assistance.

## Features

- 🎯 **Resume Variant Management**: Create and manage multiple versions of your resume tailored to different job opportunities
- 🔗 **LinkedIn Job Integration**: Automatically fetch and parse job descriptions from LinkedIn URLs
- 🌳 **Genealogy Tree View**: Visualize the relationship between resume variants
- 🤖 **AI-Powered Optimization**: Generate targeted resume variants using AI
- 📄 **PDF Generation**: Convert HTML resumes to professional PDFs
- 🧩 **Modular Architecture**: Component-based frontend with lazy loading for optimal performance

## Quick Start

### Prerequisites

- Python 3.8+
- Chrome/Chromium (for PDF generation)
- Basic web browser

### Installation

1. Clone the repository:
```bash
git clone https://github.com/rvpatarini/resumaker.git
cd resumaker
```

2. Install Python dependencies:
```bash
pip install requests beautifulsoup4
```

3. Set up the directory structure:
```bash
./setup_ai_agent.sh  # If available, or manually create directories
```

### Running the Application

#### Quick Start
```bash
# Standard server (recommended for most users)
python run.py

# Modular server (advanced users)
python run.py --modular

# Custom port
python run.py --port 8080
```

#### Manual Server Start
```bash
# Standard server
cd src && python server.py

# Modular server  
cd src && python server_modular.py
```

Then open your browser to:
- Standard: `http://localhost:8081`
- Modular: `http://localhost:8083`

## Project Structure

```
resumaker/
├── run.py                # Main entry point
├── README.md            # Project documentation  
├── LICENSE              # MIT License
├── docs/                # Documentation
│   └── ARCHITECTURE.md  # Detailed architecture guide
├── examples/            # Example HTML files
│   ├── index.html       # Basic landing page
│   └── workshop.html    # Original workshop interface
├── src/                 # Source code
│   ├── backend/         # Backend API modules
│   │   ├── api/         # API endpoints (LinkedIn, variants, etc.)
│   │   ├── core/        # Core configuration
│   │   ├── handlers/    # Request handlers  
│   │   ├── services/    # Background services
│   │   └── utils/       # Utility functions
│   ├── frontend/        # Frontend components
│   │   ├── components/  # UI components (job mgmt, variants, etc.)
│   │   ├── services/    # Frontend services
│   │   └── styles/      # CSS styles
│   ├── scripts/         # Utility scripts
│   ├── templates/       # Base resume templates
│   ├── server.py        # Standard server
│   └── server_modular.py # Modular server
└── agent_workspace/     # Working directory (created at runtime)
    ├── variants/        # Generated resume variants
    ├── output/          # PDF outputs
    └── job_descriptions/ # Saved job descriptions
```

## Core Features

### 1. Resume Variants
Create multiple versions of your resume optimized for specific roles:
- Clone existing variants
- Branch from any variant in the tree
- Track lineage and relationships

### 2. LinkedIn Integration
Fetch job descriptions directly from LinkedIn:
- Automatic parsing of job title, company, and location
- Full job description extraction
- Template fallback for manual entry

### 3. AI Optimization
Generate targeted resume variants:
- Focus on specific skills or experiences
- Tailor to job descriptions
- Maintain professional formatting

### 4. Visual Genealogy Tree
Track your resume evolution:
- Interactive tree visualization
- Minimap navigation
- Quick actions on each variant

## API Endpoints

- `GET /api/variants` - List all resume variants
- `GET /api/fetch-linkedin?url=` - Fetch LinkedIn job data
- `POST /api/create-variant` - Create new variant
- `GET /api/genealogy` - Get variant genealogy tree
- `POST /api/delete-variant` - Delete a variant
- `GET /api/generate-pdf?variant=` - Generate PDF

## Technologies Used

- **Backend**: Python 3, HTTP Server
- **Frontend**: Vanilla JavaScript, Component-based architecture
- **Styling**: CSS3 with modern layouts
- **PDF Generation**: Chrome headless via shell script
- **Data Parsing**: BeautifulSoup4 (optional for LinkedIn)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built with a focus on modularity, performance, and user experience.