![Alt text](https://i.postimg.cc/Xqmv8DGM/logo-extractor.png)

A tool for creating text dumps (extracts) of a project. It fully exports the directory structure and file contents in a human-readable text format. It offers the flexibility to choose between creating a single comprehensive file with all project contents or generating separate, focused dumps for each subdirectory. This allows the output to be tailored to specific analysis or data transfer tasks.

Furthermore, automatic splitting into parts allows for large projects to be transferred in chunks, respecting the buffer limitations of the receiving system. This is particularly useful for the incremental analysis of a codebase and for working with large projects that do not fit into a single document.

Each part contains clear labeling of its sequence number and the total number of fragments, ensuring the project structure's integrity is perceived even when transferred separately.

###### Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

###### Configuration
```bash
# Create an isolated config file
cp .env.example .env
```

###### Running
```bash
# Uses settings from .env
python main.py
```

```txt
# Specify a different project
python main.py --root ../my_project

# Disable SAFE_MODE and set a max file size
python main.py --safe false --max-size 2MB

# Change the encoding
python main.py --encoding cp1251

# Exclude folders
python main.py --exclude .git,.idea,venv

# Enable modular mode (separate extracts for each subfolder)
python main.py --modular true
```

###### Modular Mode
When modular mode is enabled (`MODULAR_MODE=true`), the utility recursively creates separate extracts for each subfolder in the project. This is useful for:
- Analyzing individual system components
- Creating isolated dumps for microservices
- Incremental transfer of code for large projects

Output file structure:
```
out/
└── project_name/
    ├── extract_project_name.txt          # Full project extract
    ├── parts/                           # Parts of the main extract
    └── subfolder/                       # Subfolder extracts (in modular mode)
        ├── extract_subfolder.txt
        └── parts/
```

###### Running Tests
```bash
# Install testing dependencies
pip install -r requirements-test.txt

# Run the tests
python -m pytest tests/ -v

# Run tests with coverage (text report)
python -m pytest tests/ -v --cov=.

# Run tests with an HTML coverage report
python -m pytest tests/ -v --cov=. --cov-report=html

# After generating the report, open it in a browser
# File: htmlcov/index.html

# Short coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing

# XML report for CI systems
python -m pytest tests/ --cov=. --cov-report=xml

# Coverage for specific files only
python -m pytest tests/ --cov=extractor.py,utils.py --cov-report=html
```