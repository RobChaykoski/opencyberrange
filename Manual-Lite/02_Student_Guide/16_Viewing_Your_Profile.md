# Viewing Your Profile

Open your profile to check your account details, view your certificates and completion record, download a PDF transcript, see your enrolled courses, join a new course, and change your password. The profile is your single account page.

## Opening your profile

Click **Profile** in the sidebar. The page opens with your profile card: avatar, display name, account badges, and completion stats.

<figure markdown>

![Profile page showing the profile card, certificates, track progress, and account sections](img/profile.png)

<figcaption>The profile page shows your avatar and completion summary, your certificates and track progress, your account fields, enrolled courses, and the change password section.</figcaption>
</figure>

## Profile tabs

The profile is split into five tabs so the page stays scannable:

| Tab | What it holds |
|---|---|
| **Overview** | Four signals: your next practice step, learning evidence, Cyber DNA class, and recent recognition. |
| **Skill tree** | The five-branch skill tree, Cyber DNA traits, practice affinities, career alignment, and title collection. |
| **Learning record** | Course achievements, certificates, track progress, and completion details. |
| **Account** | Personal information, account status, Exercise Studio (when available), and course enrolment. |
| **Security & privacy** | MFA, password change, survey consent, data export, and account deletion. |

The selected tab is kept in the page URL, so you can bookmark or share a link to
a specific tab without exposing any private data.

## Profile photo

Use **Add photo** under your avatar to upload a profile picture. The browser resizes the image before saving it, so ordinary phone photos work. PNG, JPEG, and WebP images are accepted, up to 10 MB before resizing. Use **Change photo** to replace it or **Remove** to go back to your initials.

## Skill tree, Cyber DNA, and titles

Open the **Skill tree** tab to see the visual skill tree and your learner
character sheet. The tree has one branch for each Cyber DNA trait, built from
your completed exercises, course participation, and feedback. It shows what you
have practised; it is not a ranking. The branch cards below it repeat the same
evidence in a readable list, with a practical next step for each branch.

The five traits are:

<figure markdown>

![Cyber DNA section showing the class card, five trait bars, and the equipped title](img/profile-dna.png)

<figcaption>The Cyber DNA section shows your current class, five activity-based traits, and your equipped title.</figcaption>
</figure>

| Trait | What it reflects |
|---|---|
| Explorer | Breadth across tracks, categories, and labs you have opened |
| Builder | Hands-on completions, time on task, and clean solves |
| Defender | Defensive, forensics, network-analysis, and OT practice |
| Investigator | OSINT, reconnaissance, traffic analysis, and forensics |
| Leader | Events, courses, badges, advanced labs, and teaching |

Your highest trait becomes your **class**: Pathfinder, Artificer, Warden,
Seeker, or Commander. Each trait has a score from 0 to 100 and a tier from
**Unranked** (no activity yet) through Initiate to Master. The numbers describe
what you have practised; they are not a grade or a ranking.

Below the traits, **Practice affinities** shows where your completed labs point
next. It covers Offensive Security / Penetration Testing, Defensive Security /
SOC, DFIR / Investigation, and Security Leadership / Education. Each card shows
the evidence behind the match and a practical next step. For example, a learner
with several web, exploitation, privilege-escalation, and post-exploitation labs
sees an offensive-security affinity with the evidence listed. This is positive
practice evidence, not a job label, a certification, or permission to test any
system. A learner with no offensive labs sees "No direct evidence yet", not a
negative label.

The **Career alignment** card maps your current class to a certification path
using the same track guidance as the certification panel. The roadmap link opens
Paul Jerimy's Security Certification Roadmap. Treat it as guidance, not an
official mapping. The [Career and certification resources](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/CAREER-AND-CERTIFICATION-RESOURCES.md)
page lists additional external practice and learning references. Those links are
references only; their content is not copied into the platform.

Achievements also unlock cosmetic **titles**. Open **Title collection**, choose
an unlocked title, and select **Equip**. Select **Clear** to return to your class
title. Hidden titles show as **Secret title** until you unlock them.

## Career profile exports

The Skill tree tab offers two career-profile downloads:

- **Download career profile (Markdown)** for a portable text summary.
- **Download career profile (printable HTML)** for a print-ready copy.

Both contain your Cyber DNA, learning evidence, reflection questions, and
external resource links. They are separate from the **Download PDF** transcript
on the Learning record tab. Career profiles are conversation aids, not job
labels or certifications. The export is logged for accountability and is not
shared with anyone automatically.

Your DNA updates as you complete labs and earn badges. A new account starts as a
Recruit; open an exercise to begin.

## Certificates and completion

The **Certificates & completion** section lists every certificate you have earned. Each card opens that level's printable certificate. The section also shows:

- **Track progress** with a bar and per-level completion pills. A check mark marks a level where you earned a certificate.
- **Completion details**, an expandable table of every completed exercise with its completed date, attempts, and hints used.
- **Course achievements** earned in your enrolled courses, including the
  range-wide learning-hour badges.
- **Secret badges** when you click **Show secret badges**. The switch is
  remembered on your account and can be turned off again.

## Downloading a PDF transcript

Click **Download PDF** at the top of the certificates section. The PDF contains your display name and account details, completion totals, every certificate ID, track progress, every completed exercise, and your course achievements. The file downloads as `SWOCTS-Cyber-Range-Transcript-<username>.pdf`.

## Account Information

The Account Information grid shows:

| Field | Meaning |
|-------|---------|
| Username | Your login name |
| Email | The address on your account |
| Account Status | Approved or Pending |
| Account Active | Whether your account is enabled |
| Registration Date | When you registered |
| VPN Registered | Yes or No, whether your VPN peer is set up |
| Role | Student, Instructor, or Admin |

## Course Enrollment

The Course Enrollment section holds a join by code form and your My Courses list. You can join a course here exactly as on the Courses page. See [Joining a Course](12_Joining_a_Course.md).

## Change Password

A Change Password section is embedded on the profile page. For the full procedure and the password rules, see [Changing Your Password](17_Changing_Your_Password.md).

!!! note "VPN Registered field"
    The VPN Registered field reads Yes only after you download your VPN config and your peer registers. If it reads No, download your config. See [Connecting via VPN](05_Connecting_via_VPN.md).

!!! tip "Account Status Pending"
    A new account shows Account Status as Pending until an admin approves it. While pending, you cannot launch labs. Approval is required once, after registration.
