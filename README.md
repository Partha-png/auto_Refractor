# Auto-Refractor

**Automated Code Refactoring Bot powered by LLMs**

Auto-Refractor is an intelligent GitHub bot that automatically analyzes and refactors code in pull requests, providing quality metrics and creating clean, maintainable code suggestions.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Features

- **Automated Code Analysis**: Detects code quality issues, complexity, and maintainability problems
- **LLM-Powered Refactoring**: Uses Groq's LLaMA models to intelligently refactor code
- **Quality Metrics**: Calculates and compares code quality scores before and after refactoring
- **Automatic PR Creation**: Creates new pull requests with refactored code
- **Multi-Language Support**: Supports Python, JavaScript, TypeScript, Java, C++, C, Go, and Rust
- **GitHub Integration**: Seamless webhook integration with GitHub repositories
- **Professional Output**: Clean, production-ready code without LLM artifacts

---

## How It Works

```
┌─────────────────┐
│  Developer      │
│  Creates PR     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub Webhook │
│  Triggers Bot   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Auto-Refractor │
│  Analyzes Code  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Refactors  │
│  Code (Groq)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Quality Scores │
│  Calculated     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  New PR Created │
│  with Results   │
└─────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- GitHub Personal Access Token
- Groq API Key
- Railway account (for deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Partha-png/auto_Refractor.git
   cd auto_Refractor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file:
   ```env
   GITHUB_TOKEN=your_github_personal_access_token
   GROQ_API_KEY=your_groq_api_key
   GITHUB_WEBHOOK_SECRET=your_webhook_secret
   LLM_MODEL=llama-3.1-8b-instant
   LLM_PROVIDER=groq
   ```

4. **Run locally**
   ```bash
   uvicorn src.webhook.server:app --host 0.0.0.0 --port 8000
   ```

---

## Deployment

### Deploy to Railway

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Railway**
   - Visit [railway.app](https://railway.app)
   - Create new project from GitHub repo
   - Add environment variables in Railway dashboard
   - Railway will auto-deploy

3. **Configure GitHub Webhook**
   - Go to your repository → Settings → Webhooks
   - Add webhook:
     - **Payload URL**: `https://your-railway-url.up.railway.app/webhook`
     - **Content type**: `application/json`
     - **Secret**: Your `GITHUB_WEBHOOK_SECRET`
     - **Events**: Select "Pull requests"

---

## Usage

### Basic Workflow

1. **Create a Pull Request** in your repository with code that needs refactoring
2. **Auto-Refractor automatically**:
   - Receives the webhook event
   - Analyzes the code for quality issues
   - Refactors the code using LLM
   - Calculates quality metrics
   - Creates a new PR with refactored code
   - Comments on the original PR with a link

3. **Review the refactored PR** and merge if satisfied

### Example

**Original PR**: Contains code with deep nesting, too many parameters, unused imports

**Auto-Refractor creates**:
- New PR titled: "Refactored: [Original PR Title]"
- Contains cleaned, refactored code
- Includes quality score comparison table
- Links back to original PR

---

## Architecture

### Project Structure

```
auto_Refractor/
├── src/
│   ├── config/           # Configuration and settings
│   ├── gh_integration/   # GitHub API client and PR creator
│   ├── ingestion/        # Code loading and parsing
│   ├── refactor/         # Refactoring engine and LLM agents
│   ├── scoring/          # Code quality metrics
│   ├── utils/            # Helper functions and logging
│   └── webhook/          # FastAPI webhook server
├── Procfile              # Railway deployment config
├── railway.json          # Railway build settings
├── requirements.txt      # Python dependencies
└── README.md
```

### Key Components

#### 1. Webhook Server (`src/webhook/`)
- FastAPI-based server
- Handles GitHub webhook events
- Validates webhook signatures
- Processes PRs in background tasks

#### 2. Refactoring Engine (`src/refactor/`)
- LLM-powered code analysis
- Multi-agent architecture (Linter, Complexity, Parser)
- Groq LLaMA integration
- Code cleaning and validation

#### 3. GitHub Integration (`src/gh_integration/`)
- PyGithub wrapper
- PR creation and management
- File content fetching
- Comment posting

#### 4. Scoring System (`src/scoring/`)
- BLEU score calculation
- Cyclomatic complexity
- Maintainability index
- Lines of code metrics
- Perplexity analysis

---

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | Yes | - |
| `GROQ_API_KEY` | Groq API Key for LLM | Yes | - |
| `GITHUB_WEBHOOK_SECRET` | Webhook signature secret | Yes | - |
| `LLM_MODEL` | LLM model to use | No | `llama-3.1-8b-instant` |
| `LLM_PROVIDER` | LLM provider (groq/ollama) | No | `groq` |
| `LLM_TEMPERATURE` | LLM temperature | No | `0.7` |
| `LLM_MAX_TOKENS` | Max tokens for LLM | No | `4096` |

### Supported Languages

- ✅ Python (`.py`)
- ✅ JavaScript (`.js`)
- ✅ Java (`.java`)
- ✅ C++ (`.cpp`, `.cc`, `.cxx`)
- ✅ C (`.c`)
- ✅ TypeScript (`.ts`)
- ✅ Go (`.go`)
- ✅ Rust (`.rs`)

---

## API Reference

### Webhook Endpoints

#### `POST /webhook`
Receives GitHub webhook events for pull requests.

**Headers:**
- `X-Hub-Signature-256`: GitHub webhook signature
- `X-GitHub-Event`: Event type (should be `pull_request`)

**Events Handled:**
- `pull_request.opened`
- `pull_request.synchronize`
- `pull_request.reopened`

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "auto-refractor-webhook"
}
```

---

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

### Local Development

1. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run with hot reload**
   ```bash
   uvicorn src.webhook.server:app --reload
   ```

3. **Use ngrok for webhook testing**
   ```bash
   ngrok http 8000
   ```

---

## Troubleshooting

### Common Issues

**Bot creates infinite PRs**
- Ensure bot-created PRs have "Refactored:" prefix in title
- Bot automatically skips PRs with this prefix

**Webhook not triggering**
- Check webhook delivery in GitHub settings
- Verify `GITHUB_WEBHOOK_SECRET` matches
- Check Railway logs for errors

**LLM errors**
- Verify `GROQ_API_KEY` is valid
- Check Groq API rate limits
- Ensure model name is correct

**File not found errors**
- Bot uses in-memory code from GitHub
- No local file system access needed

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## Roadmap

- [x] Multi-language support (Python, JavaScript, Java, C++, Go, Rust)
- [ ] Custom refactoring rules configuration
- [ ] Integration with CI/CD pipelines
- [ ] Web dashboard for analytics
- [ ] Multi-repository support
- [ ] Configurable quality thresholds
- [ ] Slack/Discord notifications
- [ ] Support for additional languages (Swift, Kotlin, PHP)
- [ ] Code review suggestions and comments
- [ ] Performance benchmarking

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Groq** - For providing fast LLM inference
- **PyGithub** - For GitHub API integration
- **FastAPI** - For the webhook server framework
- **LangChain** - For LLM orchestration
- **Tree-sitter** - For code parsing

---

## Contact

**Partha Sarathi**
- GitHub: [@Partha-png](https://github.com/Partha-png)
- Project Link: [https://github.com/Partha-png/auto_Refractor](https://github.com/Partha-png/auto_Refractor)

---

## Support

If you find this project helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing code

---

**Made with ❤️ by Partha Sarathi**
