# Contributing to OpenCyberRange

Thank you for your interest in contributing to OpenCyberRange.

This repository is an updated build maintained by Robert Chaykoski, based on the
original OpenCyberRange/OCR-Lite build by Lewis Heuermann. Contributions must
preserve the upstream copyright, `Required Notice:`, and license terms. The
updated build was created with AI assistance and reviewed by a human maintainer;
see [`BUILD_NOTICE.md`](BUILD_NOTICE.md) for provenance and
[`LICENSING.md`](LICENSING.md) for the license summary.

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

Available track slugs include `windows`, `linux`, `web`, `network`, `malware`,
`ot`, and `ai`. AI labs use `category: ai` and must follow the safety rules in
the AI Hacking workbook: deterministic mock targets, no real model keys, no
external network dependency for the core solve path, and no real personal data,
credentials, or malware.

New labs are written as `visibility: draft`, so they stay out of the student curriculum and out of the prerequisite chain until you are ready to publish them. The generator also refuses to reuse a lab number within a level, so new exercises sort after the existing ones instead of tying with them. Run **Admin -> Scan for Exercises** (or `python /app/app/scripts/discover_labs.py` in the backend container) to load the lab after adding it.

### Design and frontend changes

For UI work, load the project skill at
`.opencode/skills/opencyberrange-design/SKILL.md` first. It is the project source
of truth for tokens, page patterns, accessibility, Vue conventions, and course
content. The generic `ui-ux-pro-max` skill is available as an advisory input, but
the project skill takes precedence.

For course, lab, workbook, persona, or achievement content, also load
`.opencode/skills/opencyberrange-inclusive-curriculum/SKILL.md`. It covers
inclusive representation, avoiding stock hacker/victim tropes, and adding a
restrained near-future AI texture without turning the exercise into science
fiction.

Before submitting frontend changes:

```bash
cd platform/frontend
npm run lint
npm run build
```

### AI-assisted contributions

AI assistance is allowed, but the human contributor remains responsible for the
result. In the pull request:

- State that the change was AI-assisted.
- List the tests, builds, or manual checks you ran.
- Verify commands, claims, and licence implications rather than trusting
  generated text.
- Do not submit generated secrets, personal data, or unlicensed third-party
  content.

### Documentation and workbooks

Workbook source lives in `Workbook/`. The built wiki is generated with MkDocs
and checked into `platform/frontend/wiki/`.

- Add or update the chapter markdown in `Workbook/`.
- Add the chapter to the relevant `mkdocs-*.yml` navigation.
- Add the generated wiki output under `platform/frontend/wiki/range/<track>/`.
- Update `Workbook/index.md` when a new chapter is added.
- Keep `README.md`, `Manual-Lite/`, and workbook links consistent with the
  current track and lab names.

### Documentation

Improvements to documentation, installation guides, and tutorials are always appreciated.

## Code of Conduct

Be respectful, constructive, and collaborative. This project exists to serve educators and students.

## License

By contributing, you agree that your contributions will be licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE), the same license as this project.
