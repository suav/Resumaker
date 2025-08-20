# Resumaker Architecture

## Overview

Resumaker is a modular resume workshop tool built with a clean separation between frontend and backend components. The application supports two server architectures: a standard monolithic server and a modular component-based server.

## Project Structure

```
resumaker/
├── run.py                 # Main entry point
├── README.md             # Project documentation
├── LICENSE               # MIT License
├── docs/                 # Documentation
│   └── ARCHITECTURE.md   # This file
├── examples/             # Example HTML files
│   ├── index.html        # Basic landing page
│   └── workshop.html     # Original workshop interface
├── src/                  # Source code
│   ├── backend/          # Backend API modules
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core configuration
│   │   ├── handlers/    # Request handlers
│   │   ├── services/    # Background services
│   │   └── utils/       # Utility functions
│   ├── frontend/        # Frontend components
│   │   ├── components/  # UI components
│   │   ├── services/    # Frontend services
│   │   └── styles/      # CSS styles
│   ├── scripts/         # Utility scripts
│   │   ├── pdf_converter.sh
│   │   ├── setup_ai_agent.sh
│   │   └── *.py         # Python utilities
│   ├── templates/       # Base resume templates
│   ├── server.py        # Standard server
│   └── server_modular.py # Modular server
└── agent_workspace/     # Working directory (created at runtime)
    ├── variants/        # Generated resume variants
    ├── output/          # PDF outputs
    └── job_descriptions/ # Saved job descriptions
```

## Architecture Components

### Backend (Python)

#### Standard Server (`server.py`)
- Monolithic HTTP server
- All functionality in a single file
- Direct request handling
- Suitable for simple deployments

#### Modular Server (`server_modular.py`)
- Component-based architecture
- Lazy-loaded API modules
- Background job processing
- Scalable and maintainable

#### API Modules (`backend/api/`)
- `linkedin.py`: LinkedIn job fetching and parsing
- `variants.py`: Resume variant management
- `genealogy.py`: Variant relationship tree generation
- `job_descriptions.py`: Job description CRUD operations

### Frontend (JavaScript)

#### Component System
- Lazy-loaded components for optimal performance
- Event-driven communication
- State management across components
- Responsive design

#### Key Components
- **Variant Management**: Create, edit, and manage resume variants
- **Job Management**: Import and manage job descriptions
- **LinkedIn Integration**: Fetch job data from LinkedIn URLs
- **Genealogy Tree**: Visual representation of variant relationships
- **PDF Generation**: Convert HTML resumes to PDFs

### Features

#### Resume Variant System
- Create multiple targeted resume versions
- Track relationships between variants
- Clone and branch from existing resumes
- Automatic metadata tracking

#### LinkedIn Integration
- URL parsing and job ID extraction
- Company name, job title, and location extraction
- Full job description content parsing
- Fallback templates for manual entry

#### AI Integration Ready
- Extensible AI service integration
- Background job processing for AI tasks
- Template-based optimization
- Quality feedback systems

## Data Flow

1. **Job Import**: LinkedIn URLs → Job Description Database
2. **Variant Creation**: Base Template + Job Description → Optimized Variant
3. **Tree Management**: Variant Relationships → Visual Genealogy
4. **PDF Export**: HTML Variant → Professional PDF

## Security Considerations

- No personal data stored in repository
- Local file system storage only
- No external API keys required for basic functionality
- Optional AI integration with secure key management

## Deployment Options

### Local Development
```bash
python run.py
```

### Production Deployment
- Docker containerization ready
- Reverse proxy compatible
- Static file serving optimized
- Background job queue support

## Extension Points

- AI service providers (OpenAI, Anthropic, etc.)
- Additional job board integrations
- Custom resume templates
- Export format plugins
- Quality analysis modules