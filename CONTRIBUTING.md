# Contributing to taskmg
Thank you for your interest in contributing to taskmg.<br>
This project defines a new human‑friendly .task file format and provides a lightweight Python library for working with it.<br>
Contributions that improve correctness, clarity, or consistency of the format and library are welcome.<br>

## 1. Overview
taskmg has two core goals:

> 1. Provide a clean, minimal, and readable .task file format, inspired by INI, todo.txt, YAML, and TOML.
> 2. Offer a simple and dependency‑light Python library for reading, writing, and manipulating .task files.

All contributions must preserve these design principles.
## 2. What You Can Contribute
At this time, the project accepts contributions only for code, including:

* parser and serializer improvements
* performance optimizations
* format consistency fixes
* internal refactoring
* documentation inside source code (docstrings)

Contributions for documentation, examples, or tests may be accepted later, but are not the current focus.
## 3. Before You Start
### 3.1 Reporting Issues Before Major Changes
For any contribution that affects the `.task` format itself, you must:

1. Open an Issue describing the proposed change.
2. Update SPEC.md as part of your PR to reflect the new behavior.

Format stability is important, so changes must be discussed beforehand.
## 4. Development Guidelines
### 4.1 Code Style
The project follows a simple, readable Python style, with optional formatting using Black.

* Keep code clear and explicit
* Avoid clever or obscure patterns
* Prefer consistency over complexity

### 4.2 Docstrings Required
Every public function or class must include a Python docstring that explains:

* purpose
* parameters
* return value
* edge cases (if any)

> PRs without docstrings will not be accepted.
### 4.3 Dependencies
**taskmg** aims to stay dependency‑free.

> Do not introduce new dependencies unless absolutely necessary and discussed in an Issue first.
## 5. Git Workflow
Use this standard and simple Git flow:

1. Fork the repository
2. Create a new branch:
```bash
   git checkout -b feature/my-improvement
```
3. Make your changes
4. Ensure the code is formatted (optional but recommended):
```bash
   black .
```
Commit with a *clear message*:
```bash
   git commit -m "Add support for X in .task parser"
```
5. Push and open a Pull Request to the main branch

> This workflow should be followed, but is not enforced rigidly.
## 6. Maintainer
This project is maintained by:

> ***Keyhan khalghani***

All contributions are reviewed by the maintainer before merging.
## 7. Pull Request Checklist
Before submitting a PR:

- [ ] The code is clear and readable
- [ ] Docstrings are complete and accurate
- [ ] No unnecessary dependencies were added
- [ ] Behavior matches or updates SPEC.md
- [ ] Format changes have an Issue opened beforehand

## 8. Thank You
Your contributions help make the .task format and its Python library more robust, expressive, and pleasant to use.<br>
Thank you for supporting the growth of taskmg.
