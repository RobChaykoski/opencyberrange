# Contributing to OpenCyberRange

Thank you for your interest in contributing to OpenCyberRange.

## How to Contribute

### Reporting Bugs

Open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Docker version, etc.)

### Feature Requests

Open an issue with the `enhancement` label describing:
- What you'd like to see
- Why it would be useful
- Any implementation ideas

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run validation: `python3 scripts/validate-lab.py labs/{Track}/{slug}/`
5. Commit with clear messages
6. Open a pull request against `main`

### Exercise Contributions

New exercise scenarios are especially welcome. Each exercise is a self-contained directory with a `lab.yaml`, a `docker-compose.yml`, and its container build files.

To contribute an exercise:
1. Scaffold it with the generator: `python3 scripts/new-lab.py --track web --level 4 --name "Reflected XSS"`. Run it with `--list` first to see which levels are seeded and which are still empty.
2. Fill in `lab.yaml` and replace the placeholder target in `containers/target/`.
3. Build and test locally with `docker compose up`.
4. Validate with `python3 scripts/validate-lab.py platform/labs/{Track}/{slug}/` (the generator runs this for you).
5. Submit a pull request or upload the ZIP via the Instructor Panel.

New labs are written as `visibility: draft`, so they stay out of the student curriculum and out of the prerequisite chain until you are ready to publish them. The generator also refuses to reuse a lab number within a level, so new exercises sort after the existing ones instead of tying with them. Run **Admin -> Scan for Exercises** (or `python /app/app/scripts/discover_labs.py` in the backend container) to load the lab after adding it.

### Documentation

Improvements to documentation, installation guides, and tutorials are always appreciated.

## Code of Conduct

Be respectful, constructive, and collaborative. This project exists to serve educators and students.

## License

By contributing, you agree that your contributions will be licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE), the same license as this project.
