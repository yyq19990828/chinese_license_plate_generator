# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### 🔄 Project Awareness & Context

- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Consult `TASK.md` before starting a new task:** Search for any 'Not Started' tasks and identify the one that best matches the current assignment. If a match is found, follow its TODO list, marking items as complete (`[x]`) as you progress. If no suitable task exists, create a new one using the standard format, including a TODO list, and then begin work.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.
- **Use venv_linux** (the virtual environment) whenever executing Python commands, including for unit tests.

### 🧱 Code Structure & Modularity

- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
  For agents this looks like:
  - `agent.py` - Main agent definition and execution logic 
  - `tools.py` - Tool functions used by the agent 
  - `prompts.py` - System prompts
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Use python_dotenv and load_env()** for environment variables.

### 🧪 Testing & Reliability

- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case

### ✅ Task Completion

- **Mark completed tasks in `TASK.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASK.md` under a “Discovered During Work” section.

### 📎 Style & Conventions

- **Use Python** as the primary language.

- **Follow PEP8**, use type hints, and format with `black`.

- **Use `pydantic` for data validation**.

- Use `FastAPI` for APIs and `SQLAlchemy` or `SQLModel` for ORM if applicable.

- Write **docstrings for every function** using the Google style:
  
  ```python
  def example():
      """
      Brief summary.
  
      Args:
          param1 (type): Description.
  
      Returns:
          type: Description.
      """
  ```

### 📚 Documentation & Explainability

- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

### 🧠 AI Behavior Rules

- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASK.md`.


### Architecture

This repository is a Chinese license plate generator.

*   `src/`: Contains the core source code.
    *   `src/core/`: Core utilities for managing configuration (`config.py`) and custom exceptions (`exceptions.py`).
    *   `src/generator/`: Handles the image generation process.
        *   `font_manager.py`: Manages loading and applying fonts.
        *   `image_composer.py`: Composes the final license plate image from templates and characters.
        *   `plate_generator.py`: Generates the characters and structure for a given plate number.
        *   `integrated_generator.py`: Integrates the rules and generation process.
    *   `src/rules/`: Defines the rules for generating different types of license plates.
        *   `province_codes.py`: Contains mappings for province abbreviations.
        *   `regional_codes.py`: Manages city/regional codes.
        *   `sequence_generator.py`: Generates the alphanumeric sequence for the plate.
        *   `ordinary_plate.py`, `new_energy_plate.py`, `special_plate.py`: Define rules for specific plate types.
    *   `src/validators/`: Contains validation logic for generated plates and rules.
    *   `src/utils/`: Shared utilities and constants.
*   Root scripts (`generate_by_province.py`, etc.): High-level scripts that act as user-facing entry points for generating plates.
*   `font_model/`: Contains font files used for rendering characters on the plates.
*   `plate_model/`: Contains template images for different types of license plates.
*   `province_output/`: Default output directory for generated license plates, organized by province.
*   `tests/`: Contains unit and integration tests for the various components.

## Memories

*   永远用中文回复
*   不要索引和查找git项目中 @.gitignore 文件忽略的内容
*   所有响应必须显示可点击的代码构造和文件名引用, 必须使用相对路径
