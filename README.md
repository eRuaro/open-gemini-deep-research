# Open Gemini Deep Research

A powerful AI research assistant powered by Google's Gemini AI models that performs deep, multi-layered research on any topic with customizable depth and breadth.

## Overview

Open Gemini Deep Research is an advanced research tool that leverages Google's Gemini AI to conduct comprehensive research on any topic. The system uses a structured research methodology, following up with clarifying questions, generating multiple research queries, and synthesizing findings into a detailed report.

## Key Features

- **Multi-layered Research**: Automatically explores topics with adjustable breadth and depth parameters
- **Smart Query Generation**: Creates focused, non-overlapping research queries based on your topic
- **Follow-up Questions**: Refines research focus through intelligent clarifying questions
- **Research Tree Structure**: Visualizes the research process with a tree-based approach
- **Comprehensive Reporting**: Generates detailed reports with citations and source tracking
- **Multiple Research Modes**:
  - **Fast**: Quick overview for time-sensitive needs (1-2 minutes)
  - **Balanced**: Optimal depth-speed tradeoff (3-6 minutes)
  - **Comprehensive**: In-depth analysis with recursive exploration (5-15 minutes)
- **Progress Tracking**: Monitors research status with detailed visualization
- **Web & CLI Interfaces**: Use as a command-line tool or interactive web application

## Use Cases

- Academic research and literature reviews
- Market research and competitive analysis
- Technology trend exploration
- Policy and regulatory analysis
- Topic discovery and exploration
- Educational content creation
- Background research for writing

## Getting Started

### Prerequisites

- Python 3.9+
- Google Gemini API key
- Docker (for containerized deployment)

### Installation

#### Option 1: Direct Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/open-gemini-deep-research.git
cd open-gemini-deep-research

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your Gemini API key
# Create a .env file with your API key
echo "GEMINI_KEY=your_api_key_here" > .env
```

#### Option 2: Using Docker

```bash
# Build and run with Docker
docker build -t open-gemini-deep-research .
docker run -it -e GEMINI_KEY=your_api_key_here open-gemini-deep-research
```

## Usage

### Command Line Interface

Run research directly from the command line:

```bash
# Basic usage
python main.py "Your research topic or question"

# With options
python main.py "Impact of artificial intelligence on healthcare" --mode comprehensive --num-queries 5
```

#### CLI Options:
- `--mode`: Research mode (`fast`, `balanced`, `comprehensive`) [default: balanced]
- `--num-queries`: Number of initial queries to generate [default: 3]
- `--learnings`: List of previous learnings to incorporate [optional]

### Web Interface

Launch the interactive web application:

```bash
streamlit run app.py
```

The web interface provides:
- Interactive research configuration
- Live progress tracking
- Research tree visualization
- Downloadable reports and data
- Source and citation management

## How It Works

### Research Process Architecture

1. **Query Analysis**: Analyzes topic complexity to determine optimal research parameters
2. **Follow-up Questions**: Generates clarifying questions to refine research focus
3. **Query Generation**: Creates semantically diverse search queries
4. **Deep Research**: Conducts multi-layered research with the specified depth and breadth
   - For comprehensive mode: Implements recursive exploration of sub-topics
5. **Research Tree Building**: Maintains a structured tree of research queries and findings
6. **Report Generation**: Synthesizes findings into a detailed markdown report with citations

### Research Modes in Detail

| Mode | Depth | Breadth | Processing Time | Recursive | Follow-up Questions |
|------|-------|---------|----------------|-----------|---------------------|
| Fast | Low | Limited | 1-2 min | No | 2-3 |
| Balanced | Medium | Medium | 3-6 min | No | 3-5 |
| Comprehensive | High | Wide + Deep | 5-15 min | Yes | 5-7 |

### Technical Implementation

- **Model Rotation**: Automatically rotates between available Gemini models for optimal performance
- **Tree-based Progress Tracking**: Visualizes research progress with a hierarchical tree structure
- **Concurrent Processing**: Processes multiple queries in parallel for efficiency
- **Citation Management**: Tracks and formats sources with proper citations
- **Custom JSON Schemas**: Uses structured output for consistent data handling

## Project Structure

```
open-gemini-deep-research/
├── app.py                    # Streamlit web interface
├── dockerfile                # Docker configuration
├── main.py                   # CLI entry point
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── results/                  # Directory for saved research results
└── src/                      # Source code
    ├── __init__.py
    ├── deep_research.py      # Core research functionality
    └── gemini_client.py      # Gemini API integration
```

## Output Files

Each research session produces:
- `final_report.md`: Comprehensive markdown report with findings and citations
- `results/report_{query}.md`: Saved copy of the report with a timestamped filename
- `results/research_tree_{query}.json`: JSON representation of the research process tree

## License

[MIT License](LICENSE)

## Acknowledgments

- Google Gemini API for providing the underlying AI capabilities
- Streamlit for the interactive web interface framework
