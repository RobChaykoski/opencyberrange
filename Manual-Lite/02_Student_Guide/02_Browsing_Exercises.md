# Browsing Exercises

The Exercises hub is where you find every training path open to you. The page groups labs into tracks, shows your progress in each, and lets you open a track to see its levels and labs. Start here whenever you want to choose what to work on.

## Prerequisites

- A logged-in, approved account. See [Logging In](../01_Getting_Started/05_Logging_In.md).

## Open the hub

The hub lives at `/exercises`. You reach it from the **Exercises** item in the left sidebar, from the **Resume Training** button on your dashboard, or by typing the address directly. The platform redirects the older `/labs` and `/curriculum` addresses here, so any old bookmark still lands you on the same page.

<figure markdown>

![The Exercises hub showing the overall progress summary and a grid of track cards](img/browsing-exercises.png)

<figcaption>The Exercises hub lists your tracks as cards, each with a progress bar and exercise count.</figcaption>
</figure>

The page opens with the title "Exercises" and a three-stat progress summary: labs Completed, Exercises in view, and progress percent. Below the summary sits a grid of track cards.

## Start with a career focus

Your **career target** sets a shorter, focused catalogue. The selector at the top of the page shows the target you are aiming for, and the tracks aligned with that target appear first. A new learner starts in the **Cybersecurity Foundations** focus, which keeps the first screen small and beginner-first.

- Use the career-target selector to choose a different pathway, such as SOC Analyst, Incident Responder, or Penetration Tester.
- The focus bar tells you how many of the available tracks you are seeing and offers **Show all tracks**.
- The full catalogue is always one click away. The focus is a starting point, not a lock.
- When every track in the focus is complete, the page marks the pathway complete and invites you to explore all tracks.

The progress summary follows the view: it counts the exercises in the focused tracks while the focus is active, and every track when you open the full catalogue. Your career target is a preference, not a grade; changing it never changes your completed work.

Each track card shows:

- An icon and the track name.
- A short description of the track.
- An "X/Y exercises" count.
- A "Level N" chip marking your current level in that track.
- A progress bar, and a green "Complete" badge once you finish the track.

## Choose a track and open it

Current tracks include Windows Penetration Testing (with the Active Directory
attack-and-remediation pathway), Linux Fundamentals, Web Application Security
(with the modern application-security pathway: API, GraphQL, JWT, OAuth,
DevSecOps, containers, Kubernetes, and supply chain), Network Security, Malware
Analysis, OT/ICS Security, OSINT, Digital Forensics, Identity and Access, and AI
Security. Release 5.38 ships **215 lab definitions**; **170** are in the public
catalogue and **45** are scoped to an assigned course. The available set also
depends on the edition and content enabled on your server.

1. Open `/exercises` from the sidebar.
2. Check the career target at the top. Choose a different pathway if your direction has changed, or select **Show all tracks** to browse everything.
3. Scan the track cards and read the descriptions to pick a path.
4. Click a track card. The platform opens that track at `/exercises/<slug>`, where the levels and labs appear.

**What you should see:** the track page loads with its levels listed as an accordion and the labs inside each level. See [Understanding Tracks, Levels, and Labs](03_Understanding_Tracks_Levels_and_Labs.md).

## When the hub looks empty or different

!!! note "Empty state"
    If no active tracks are published, the hub shows "No learning paths available yet". If the focused view finds no active tracks for your career target, it says so and offers **Show all tracks**. Check back later or ask your instructor.

!!! tip "Deep links open the right track"
    A link that carries a lab, course, or wiki reference resolves automatically and drops you into the matching track. Instructors and the dashboard use these links so you do not have to hunt for a lab by hand.

Reordering handles on the track cards belong to instructors and admins only. As a student you never see them, and the card order is fixed for you.

If a track you expect is missing, the labs in it may be reserved for a course you have not joined. See [Course Labs and Assignments](13_Course_Labs_and_Assignments.md).
