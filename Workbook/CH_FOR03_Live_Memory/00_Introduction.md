# FOR03B: Live Memory Acquisition

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `FOR03B` — Live Memory Acquisition
    **Prerequisites:** `FOR01` — Memory Forensics
    **Recommended next:** `OSINT01` — OSINT Foundations
<!-- END GENERATED CHAPTER POSITION -->

Volatile memory is the evidence that disappears when a host powers off. This
chapter adds the acquisition step in front of the analysis you already practised
in FOR01: capture memory from a running Linux guest, prove the image is intact,
and only then examine it.

## What you will practise

- choosing acquisition over shutdown when volatile evidence matters;
- acquiring memory with AVML from a running guest;
- hashing and verifying the image for chain of custody;
- transferring the image safely to the analyst workstation;
- confirming the live process and its environment in the acquired image;
- writing a short finding that states what happened, the evidence, your
  confidence, and the next step.

## Chapter exercise

| Exercise | Format | Time | Evidence |
|---|---|---|---|
| 3.1 Live Linux Memory Acquisition | Guided | ~120 min | Flag, image hash, command transcript, analyst finding |

The lab target is an isolated Linux guest. Nothing leaves the lab network.
