"""Seed level quizzes with 20-question multiple-choice sets.

Add new quizzes by appending to QUIZZES. Each quiz attaches to a level by
(track_slug, level_number). Re-running upserts the questions.
"""
import json
import os
import sys

sys.path.insert(0, "/app")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://labuser:labpass@db:5432/labdb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.models import Track, LevelQuiz, QuizQuestion


def upsert_quiz(db, track_slug, level_number, title, questions):
    track = db.query(Track).filter(Track.slug == track_slug).first()
    if not track:
        print(f"  ! track {track_slug} not found, skipping")
        return
    level = next((lv for lv in track.levels if lv.level_number == level_number), None)
    if not level:
        print(f"  ! level {level_number} not found for {track_slug}, skipping")
        return

    quiz = db.query(LevelQuiz).filter(LevelQuiz.level_id == level.id).first()
    if not quiz:
        quiz = LevelQuiz(level_id=level.id, title=title, passing_score=70, is_active=True)
        db.add(quiz)
        db.flush()
    else:
        quiz.title = title
        # remove old questions
        for q in list(quiz.questions):
            db.delete(q)
        db.flush()

    for i, q in enumerate(questions):
        db.add(QuizQuestion(
            quiz_id=quiz.id,
            sort_order=i,
            question=q["q"],
            options=json.dumps(q["options"]),
            correct_index=q["answer"],
            explanation=q.get("expl", ""),
        ))
    db.commit()
    print(f"  [ok] {track_slug} L{level_number}: {len(questions)} questions")


# ---------------- M1: Malware Fundamentals ----------------
M1_QUESTIONS = [
    {"q": "What is the purpose of a sandbox in malware analysis?", "options": ["To execute malware safely in isolation", "To compile source code", "To encrypt files", "To scan for viruses"], "answer": 0, "expl": "A sandbox isolates execution so the sample cannot harm the host."},
    {"q": "Which command identifies a file's true type regardless of its extension?", "options": ["ls", "file", "cat", "strings"], "answer": 1, "expl": "`file` reads magic bytes."},
    {"q": "What does `strings` extract from a binary?", "options": ["Only source code", "Printable character sequences", "Encrypted data", "Network packets"], "answer": 1, "expl": "strings prints runs of printable characters."},
    {"q": "Why are malware samples often shipped in password-protected ZIPs?", "options": ["To compress them", "To prevent scanners from auto-opening them", "To encrypt them permanently", "To hide from users"], "answer": 1, "expl": "The password stops gateways/endpoints from auto-extracting."},
    {"q": "What is the standard password for malware sample archives?", "options": ["password", "infected", "malware", "virus"], "answer": 1, "expl": "The standard password is 'infected'."},
    {"q": "Which indicator is host-based?", "options": ["C2 IP address", "Domain name", "Registry key change", "Beacon URI"], "answer": 2, "expl": "Registry changes are host-based indicators."},
    {"q": "Why might `strings` fail to recover a runtime-built key?", "options": ["The key is too short", "The key is constructed at runtime, not stored", "strings only reads headers", "The file is encrypted"], "answer": 1, "expl": "Runtime-built keys never appear as static strings."},
    {"q": "What does Ghidra's decompiler produce?", "options": ["Machine code", "C-like pseudocode", "Assembly only", "Source code"], "answer": 1, "expl": "The decompiler lifts assembly to C-like pseudocode."},
    {"q": "In a PCAP, how do you reconstruct an HTTP conversation?", "options": ["Follow TCP stream", "Filter by MAC", "Drop all packets", "Replay DNS"], "answer": 0, "expl": "Follow TCP Stream reassembles the conversation."},
    {"q": "What does INetSim simulate?", "options": ["A real internet", "Common internet services for safe C2 analysis", "A firewall", "A VPN"], "answer": 1, "expl": "INetSim simulates services so malware beacons safely."},
    {"q": "Why use a network tap instead of tcpdump on the victim?", "options": ["It is faster", "It sees all traffic without host access", "It encrypts traffic", "It blocks malware"], "answer": 1, "expl": "A tap mirrors all traffic without touching the host."},
    {"q": "What does SPF fail indicate?", "options": ["The sender IP is not authorized", "The message is encrypted", "DKIM passed", "DMARC passed"], "answer": 0, "expl": "SPF fail means the sending IP is unauthorized."},
    {"q": "What is a Reply-To mismatch a sign of?", "options": ["Legitimate mail", "Phishing", "Encryption", "Compression"], "answer": 1, "expl": "Reply-To to a different/lookalike domain is a phishing signal."},
    {"q": "The attachment is named .doc but its bytes are HTML. What does this tell you?", "options": ["It is a real Word doc", "The extension hides the true type", "It is compressed", "It is encrypted"], "answer": 1, "expl": "Extension does not equal content type."},
    {"q": "Which is safer: parsing MIME with Python or opening the attachment?", "options": ["Opening in Word", "Parsing with Python", "Double-clicking", "Email preview"], "answer": 1, "expl": "Parse as text; never open the attachment."},
    {"q": "What does DMARC do?", "options": ["Encrypts email", "Ties SPF/DKIM to the From domain and sets policy", "Compresses attachments", "Scans for viruses"], "answer": 1, "expl": "DMARC aligns SPF/DKIM with the visible From domain."},
    {"q": "A JScript block in an HTML 'doc' is best treated as:", "options": ["A macro to enable", "A lure/payload", "A stylesheet", "A font"], "answer": 1, "expl": "Treat the script as the payload, not an instruction."},
    {"q": "What is the first step in malware triage?", "options": ["Execute the sample", "Acquire evidence without executing", "Patch the system", "Delete the file"], "answer": 1, "expl": "Acquire without executing."},
    {"q": "Why hash the original sample before analysis?", "options": ["To encrypt it", "To verify integrity and identify it", "To compress it", "To execute it"], "answer": 1, "expl": "Hashes identify and verify samples."},
    {"q": "What does a beacon's user-agent string help identify?", "options": ["The victim's password", "The implant family/configuration", "The C2 IP", "The flag"], "answer": 1, "expl": "User-agent often reveals the implant."},
]

# ---------------- M2: Executable Analysis ----------------
M2_QUESTIONS = [
    {"q": "What does 'PE' stand for?", "options": ["Portable Executable", "Protected Environment", "Process Entry", "Program Extension"], "answer": 0, "expl": "PE = Portable Executable."},
    {"q": "What is the DOS header's first two bytes?", "options": ["PE", "MZ", "ELF", "MZ is optional"], "answer": 1, "expl": "DOS header starts with MZ."},
    {"q": "Where is the PE signature offset stored?", "options": ["0x00", "0x3C (e_lfanew)", "0x80", "0x100"], "answer": 1, "expl": "e_lfanew at 0x3C points to the PE signature."},
    {"q": "What machine value indicates i386?", "options": ["0x8664", "0x014C", "0x0200", "0x10B"], "answer": 1, "expl": "0x014C = i386."},
    {"q": "What does the COFF timestamp represent?", "options": ["Install time", "Build time (Unix epoch)", "Expiry", "Last run"], "answer": 1, "expl": "TimeDateStamp is the build time."},
    {"q": "What is an RVA?", "options": ["Raw Virtual Address", "Relative Virtual Address", "Random Virtual Access", "Real Virtual Address"], "answer": 1, "expl": "RVA = Relative Virtual Address (from image base)."},
    {"q": "Which section typically holds executable code?", "options": [".data", ".rdata", ".text", ".bss"], "answer": 2, "expl": ".text holds code."},
    {"q": "Which section holds read-only data and imports?", "options": [".text", ".rdata", ".data", ".reloc"], "answer": 1, "expl": ".rdata holds read-only data/imports."},
    {"q": "What does an import of InternetOpenA suggest?", "options": ["File access", "Network (WinINet) access", "Graphics", "Audio"], "answer": 1, "expl": "InternetOpenA is a WinINet network API."},
    {"q": "What does CreateFileA suggest?", "options": ["Network access", "File system access", "Graphics", "Audio"], "answer": 1, "expl": "CreateFileA accesses the file system."},
    {"q": "Why is the marker XOR-encoded in .data?", "options": ["To compress it", "To avoid plaintext detection", "To encrypt for transport", "To speed up loading"], "answer": 1, "expl": "XOR obfuscation avoids simple string detection."},
    {"q": "How do you convert an RVA to a file offset?", "options": ["Add image base", "Use the section table (VA/RVA/raw offset)", "Multiply by 2", "It's the same"], "answer": 1, "expl": "Section table maps RVA to raw file offset."},
    {"q": "What is the entry point?", "options": ["The file size", "The RVA where execution begins", "The image base", "The timestamp"], "answer": 1, "expl": "AddressOfEntryPoint is the starting RVA."},
    {"q": "What does subsystem 3 mean?", "options": ["GUI", "Console", "Driver", "Native"], "answer": 1, "expl": "3 = console subsystem."},
    {"q": "Why is the COFF timestamp useful despite being forgeable?", "options": ["It is always accurate", "It narrows triage and clusters samples", "It prevents execution", "It encrypts the file"], "answer": 1, "expl": "Timestamps help cluster and triage even if forgeable."},
    {"q": "What is an imphash used for?", "options": ["Encrypting imports", "Clustering malware variants", "Compressing the file", "Running the file"], "answer": 1, "expl": "Import hashing clusters variants sharing a build."},
    {"q": "Which tool prints PE headers and imports?", "options": ["strings", "objdump -x", "file", "xxd"], "answer": 1, "expl": "objdump -x prints PE headers/imports."},
    {"q": "Why must you never execute an unknown PE?", "options": ["It is slow", "It may be malicious", "It needs a license", "It is incompatible"], "answer": 1, "expl": "Unknown executables may be malicious."},
    {"q": "What does a large .data section with execute permission suggest?", "options": ["Normal code", "Possible packed/obfuscated payload", "A font", "A help file"], "answer": 1, "expl": "Anomalous sections warrant investigation."},
    {"q": "What is the first step before deeper analysis?", "options": ["Run in a sandbox", "Static triage of headers/sections/imports", "Patch the binary", "Delete it"], "answer": 1, "expl": "Start with static triage of the format."},
]

# ---------------- OT: Modbus Fundamentals ----------------
OT_QUESTIONS = [
    {"q": "What port does Modbus TCP use by default?", "options": ["80", "443", "502", "3306"], "answer": 2, "expl": "Modbus TCP default port is 502."},
    {"q": "Does Modbus TCP have authentication by default?", "options": ["Yes, password-based", "Yes, certificate-based", "No", "Only on port 502"], "answer": 2, "expl": "Modbus has no built-in authentication."},
    {"q": "What function code reads holding registers?", "options": ["0x01", "0x02", "0x03", "0x04"], "answer": 2, "expl": "Function 0x03 = Read Holding Registers."},
    {"q": "What is the size of a Modbus register?", "options": ["8 bits", "16 bits", "32 bits", "64 bits"], "answer": 1, "expl": "Modbus registers are 16-bit."},
    {"q": "What is the MBAP header length?", "options": ["4 bytes", "7 bytes", "12 bytes", "16 bytes"], "answer": 1, "expl": "MBAP header is 7 bytes."},
    {"q": "Which tool reads Modbus registers from the CLI?", "options": ["nmap", "mbpoll", "curl", "dig"], "answer": 1, "expl": "mbpoll is a Modbus CLI client."},
    {"q": "What does a Modbus coil represent?", "options": ["A 16-bit value", "A single bit (on/off)", "A string", "A float"], "answer": 1, "expl": "Coils are single-bit outputs."},
    {"q": "Why is Modbus risky on a flat network?", "options": ["It is slow", "No auth/encryption, anyone can read/write", "It uses too much bandwidth", "It requires a license"], "answer": 1, "expl": "No auth/encryption on a flat network is dangerous."},
    {"q": "What is a holding register used for?", "options": ["Read-only inputs", "Read/write configuration/setpoints", "Coils", "Diagnostics"], "answer": 1, "expl": "Holding registers are read/write."},
    {"q": "What is an input register?", "options": ["Read/write", "Read-only device inputs", "A coil", "A counter"], "answer": 1, "expl": "Input registers are read-only."},
    {"q": "How is ASCII text often stored in Modbus registers?", "options": ["One char per 16-bit register", "Binary only", "Compressed", "Encrypted"], "answer": 0, "expl": "One character per 16-bit register is common."},
    {"q": "What does function code 0x06 do?", "options": ["Read coils", "Write single register", "Read inputs", "Diagnostics"], "answer": 1, "expl": "0x06 = Write Single Register."},
    {"q": "What is the unit ID in Modbus TCP?", "options": ["The port number", "The slave/device address", "The transaction ID", "The protocol ID"], "answer": 1, "expl": "Unit ID addresses the slave device."},
    {"q": "What is the protocol ID for Modbus TCP?", "options": ["0x0000", "0x0001", "0x0002", "0xFFFF"], "answer": 0, "expl": "Protocol ID is 0 for Modbus TCP."},
    {"q": "Which Nmap script enumerates Modbus?", "options": ["http-enum", "modbus-discover", "smb-enum", "dns-brute"], "answer": 1, "expl": "modbus-discover NSE script."},
    {"q": "What is the safest first step in OT triage?", "options": ["Write to registers", "Passive enumeration and read-only queries", "Reboot the PLC", "Disable the service"], "answer": 1, "expl": "Read-only passive enumeration first."},
    {"q": "What does 'defense in depth' mean for OT?", "options": ["One firewall", "Multiple layers of control", "No monitoring", " Open internet access"], "answer": 1, "expl": "Multiple layers of defense."},
    {"q": "Why segment OT networks?", "options": ["For speed", "To limit blast radius", "To save money", "To avoid backups"], "answer": 1, "expl": "Segmentation limits blast radius."},
    {"q": "What is a PLC?", "options": ["A web server", "A Programmable Logic Controller", "A database", "A router"], "answer": 1, "expl": "PLC = Programmable Logic Controller."},
    {"q": "What is the key risk of writing to a PLC register in production?", "options": ["It is slow", "It can alter physical process state", "It uses bandwidth", "It is logged"], "answer": 1, "expl": "Writes can change physical process state."},
]

QUIZZES = [
    ("malware", 1, "Malware Fundamentals Quiz", M1_QUESTIONS),
    ("malware", 2, "Executable Analysis Quiz", M2_QUESTIONS),
    ("ot", 1, "Modbus Fundamentals Quiz", OT_QUESTIONS),
]


def main():
    db = SessionLocal()
    try:
        for track_slug, level_number, title, questions in QUIZZES:
            upsert_quiz(db, track_slug, level_number, title, questions)
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
