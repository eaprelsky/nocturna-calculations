# Quick Start Guide

This guide will get you up and running with Nocturna Calculations in 5 minutes.

## Prerequisites

- **Python 3.9+** 
- **Conda** (Miniconda or Anaconda) - [Install Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- **Git**
- **PostgreSQL** and **Redis** (optional - will be installed automatically)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations
```

### 2. Run Setup

```bash
make setup
```

This single command will:
- ✅ Create a development environment with all dependencies
- ✅ Install PostgreSQL and Redis if needed
- ✅ Setup the database
- ✅ Create configuration files
- ✅ Run initial migrations

### 3. Activate Environment

```bash
conda activate nocturna-dev
```

### 4. Start Development Server

```bash
make dev
```

Visit http://localhost:8000/docs to see the API documentation.

## That's It! 🎉

You now have a fully functional development environment.

## Next Steps

- **Run tests**: `make test`
- **Format code**: `make format`
- **Open Jupyter**: `make jupyter`
- **See all commands**: `make help`

## Common Commands

| Command | Description |
|---------|-------------|
| `make setup` | Complete setup (first time) |
| `make dev` | Start development server |
| `make test` | Run all tests |
| `make format` | Format code |
| `make lint` | Check code quality |
| `make shell` | Open Python shell |
| `make help` | Show all commands |

## Troubleshooting

### Conda not found
Install Miniconda from https://docs.conda.io/en/latest/miniconda.html

### PostgreSQL/Redis issues
```bash
make services-check  # Check status
make services-install  # Install if needed
```

### Environment issues
```bash
make env-info  # Show environment details
```

## Different Installation Options

### Testing Environment
```bash
make setup-test
conda activate nocturna-test
```

### Production Environment
```bash
make setup-prod
conda activate nocturna-prod
```

### Manual Service Installation
```bash
make services-install  # Install PostgreSQL and Redis
```

## Getting Help

- Run `make help` to see all available commands
- Check `docs/installation/` for detailed guides
- Open an issue on GitHub for bugs 