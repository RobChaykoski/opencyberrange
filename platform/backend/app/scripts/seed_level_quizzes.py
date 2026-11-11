"""Seed the optional level quizzes for the Beginner Cybersecurity track.

The quiz runtime (models, endpoints, modal, scoring) already exists. This
script supplies the missing level quiz banks. It is idempotent: it updates the
quiz metadata and replaces the questions for each level.

Run inside the backend container:

    docker exec -e PYTHONPATH=/app ocr-backend \
        python -m app.scripts.seed_level_quizzes
"""
import json

from app.database import SessionLocal
from app.models import Level, LevelQuiz, QuizQuestion, Track

QUIZZES = {
    ("high-school", 9): {
        "title": "Beginner Stage 1 Check",
        "passing_score": 70,
        "questions": [
            {
                "question": "Which command prints the folder you are currently in?",
                "options": ["ls", "pwd", "whoami", "cd"],
                "correct_index": 1,
                "explanation": "pwd prints the current working directory.",
            },
            {
                "question": "What does `ls` list?",
                "options": [
                    "The current user",
                    "Open network ports",
                    "The files and folders in the current folder",
                    "The last command",
                ],
                "correct_index": 2,
                "explanation": "ls lists directory contents.",
            },
            {
                "question": "Base64 is best described as:",
                "options": [
                    "Encryption that needs a secret key",
                    "A one-way hash",
                    "A password manager",
                    "An encoding that can be reversed",
                ],
                "correct_index": 3,
                "explanation": "Base64 changes representation; it is not encryption.",
            },
            {
                "question": (
                    "In https://library.example@windosrlibrary-secure.example/verify, "
                    "which part is the real host?"
                ),
                "options": [
                    "windosrlibrary-secure.example",
                    "library.example",
                    "https",
                    "verify",
                ],
                "correct_index": 0,
                "explanation": "The host is the part after the @, before the next slash.",
            },
            {
                "question": "A file named photo.png is always an image.",
                "options": [
                    "True - the extension proves it",
                    "True if it opens",
                    "False - check the file's real type",
                    "False - only PDFs are images",
                ],
                "correct_index": 2,
                "explanation": "Extensions are labels; verify the actual file signature.",
            },
        ],
    },
    ("high-school", 10): {
        "title": "Beginner Stage 2 Check",
        "passing_score": 70,
        "questions": [
            {
                "question": "DNS is used to:",
                "options": [
                    "Translate hostnames into IP addresses",
                    "Encrypt web traffic",
                    "Store email attachments",
                    "Compress files",
                ],
                "correct_index": 0,
                "explanation": "DNS maps names such as web.lab to IP addresses.",
            },
            {
                "question": "Which curl option shows response headers?",
                "options": ["-o", "-i", "-s", "-X POST"],
                "correct_index": 1,
                "explanation": "curl -i includes the response headers in the output.",
            },
            {
                "question": "SPF, DKIM, and DMARC are used to:",
                "options": [
                    "Compress email attachments",
                    "Encode the email body",
                    "Check whether an email sender is authenticated",
                    "Delete old messages",
                ],
                "correct_index": 2,
                "explanation": "They record sender-authentication results for an email.",
            },
            {
                "question": "You lost your MFA phone. What is the safest next step?",
                "options": [
                    "Disable MFA for the account",
                    "Share the password with a colleague",
                    "Turn off the account lockout",
                    "Use a saved recovery code or backup method",
                ],
                "correct_index": 3,
                "explanation": "Recovery codes exist so MFA can stay enabled.",
            },
            {
                "question": (
                    "A log shows repeated 404s from one IP, then a 200 to "
                    "/admin?token=... . What does that suggest?"
                ),
                "options": [
                    "A probe followed by a possible successful request",
                    "Normal health monitoring",
                    "A DNS failure",
                    "A backup job",
                ],
                "correct_index": 0,
                "explanation": "The failed probes followed by a success are a classic pattern.",
            },
        ],
    },
    ("high-school", 11): {
        "title": "Beginner Stage 3 Check",
        "passing_score": 70,
        "questions": [
            {
                "question": (
                    "Repeated 404 responses from one source, then a 200 with an "
                    "unusual query string, is:"
                ),
                "options": [
                    "A normal page view",
                    "A pattern worth investigating",
                    "Proof of a backup",
                    "A DNS record",
                ],
                "correct_index": 1,
                "explanation": "The sequence suggests probing and a possible success.",
            },
            {
                "question": (
                    "An image has no independent source, venue log, or second "
                    "photographer. How should you treat it?"
                ),
                "options": [
                    "As definitely real",
                    "As definitely fake",
                    "As unverified until corroborated",
                    "As a password reset link",
                ],
                "correct_index": 2,
                "explanation": "Provenance requires corroboration, not just the pixels.",
            },
            {
                "question": (
                    "A social platform strips metadata from an uploaded image. What "
                    "does that prove?"
                ),
                "options": [
                    "The image is fake",
                    "The image is original",
                    "The image was encrypted",
                    "Nothing by itself; absence of metadata is not proof of manipulation",
                ],
                "correct_index": 3,
                "explanation": "Metadata loss is common and is not evidence either way.",
            },
            {
                "question": "Which evidence best supports a claim that an event happened?",
                "options": [
                    "Independent sources and records that agree",
                    "A single anonymous post",
                    "A high number of likes",
                    "A screenshot with no source",
                ],
                "correct_index": 0,
                "explanation": "Independent corroboration is stronger than popularity.",
            },
        ],
    },
    ("high-school", 12): {
        "title": "Beginner Stage 4 Check",
        "passing_score": 70,
        "questions": [
            {
                "question": (
                    "A link contains userinfo@host. Which part should you inspect as "
                    "the destination?"
                ),
                "options": [
                    "The text before the @",
                    "The host after the @",
                    "The word https",
                    "The fragment after #",
                ],
                "correct_index": 1,
                "explanation": "Text before @ is userinfo; the host follows it.",
            },
            {
                "question": "Why URL-decode a link before trusting it?",
                "options": [
                    "It makes the link faster",
                    "It proves the link is safe",
                    "Percent-encoding can hide the real path or token",
                    "It removes the domain",
                ],
                "correct_index": 2,
                "explanation": "Decoding reveals hidden paths, tokens, and characters.",
            },
            {
                "question": "A file named .png starts with PK. What should you do?",
                "options": [
                    "Open it because the extension is png",
                    "Rename it to .zip and run it",
                    "Email it to a colleague",
                    "Check the real file type before opening it",
                ],
                "correct_index": 3,
                "explanation": "PK indicates a ZIP archive, regardless of the name.",
            },
            {
                "question": (
                    "A token project promises guaranteed returns, then community "
                    "funds move to a new wallet and offshore. What is the best response?"
                ),
                "options": [
                    "Follow the ledger and report the suspicious flow",
                    "Invest more before it is too late",
                    "Post the wallet key publicly",
                    "Ignore the transactions",
                ],
                "correct_index": 0,
                "explanation": "The ledger is the evidence; report the flow.",
            },
        ],
    },
}


def main():
    db = SessionLocal()
    try:
        for (track_slug, level_number), data in QUIZZES.items():
            track = db.query(Track).filter(Track.slug == track_slug).first()
            if not track:
                print(f"[skip] track not found: {track_slug}")
                continue
            level = db.query(Level).filter(
                Level.track_id == track.id,
                Level.level_number == level_number,
            ).first()
            if not level:
                print(f"[skip] level not found: {track_slug} level {level_number}")
                continue

            quiz = db.query(LevelQuiz).filter(LevelQuiz.level_id == level.id).first()
            if not quiz:
                quiz = LevelQuiz(
                    level_id=level.id,
                    title=data["title"],
                    passing_score=data["passing_score"],
                    is_active=True,
                )
                db.add(quiz)
                db.flush()
            else:
                quiz.title = data["title"]
                quiz.passing_score = data["passing_score"]
                quiz.is_active = True
                for question in list(quiz.questions):
                    db.delete(question)
                db.flush()

            for index, question in enumerate(data["questions"]):
                db.add(QuizQuestion(
                    quiz_id=quiz.id,
                    sort_order=index,
                    question=question["question"],
                    options=json.dumps(question["options"]),
                    correct_index=question["correct_index"],
                    explanation=question["explanation"],
                ))
            print(
                f"[ok] {track_slug} level {level_number}: "
                f"{len(data['questions'])} questions"
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
