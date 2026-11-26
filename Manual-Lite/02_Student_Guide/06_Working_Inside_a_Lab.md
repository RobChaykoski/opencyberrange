# Working Inside a Lab

The Active Lab panel is the single screen that hosts everything you do during an exercise: the scenario, your objectives, the network and target details, the workbook link, the flag form, hints, and the session timer. Once a lab is running, you spend your time here.

## Prerequisites

- A running lab. See [Launching a Lab](04_Launching_a_Lab.md).
- A way to reach the targets: either the VPN tunnel or the in-browser RangeBox desktop. See [Connecting via VPN](05_Connecting_via_VPN.md).

## What the panel contains

The Active Lab panel opens on the track page. It has a control bar and two working columns:

- **Control bar:** the exercise name, an **Active** badge, **Knowledge check**, **CyberChef**, **Stop Exercise**, **Exit**, a live countdown timer, **Pause**, and **+1 Hour**. The knowledge check is the optional benchmark, not the level quiz. See [Knowledge Checks and Level Quizzes](33_Knowledge_Checks_and_Level_Quizzes.md), [Extending a Lab Session](09_Extending_a_Lab_Session.md), and [Stopping a Lab](10_Stopping_a_Lab.md).
- **Reaction bar:** "Was this exercise useful?" with Like and Dislike. Your instructor sees totals, not your name.
- **Connect to this lab over the VPN:** the lab subnet and an **Open VPN Setup** button. Labs with RangeBox show a desktop entry point instead.
- **New to this exercise?:** a short prompt and **Open workbook** when the lab has a workbook.
- **Submit the flag:** the flag field, **Paste**, **Submit**, and **Request human review**. See [Submitting Flags](07_Submitting_Flags.md).
- **Hints:** time-gated help inside the panel or the workbook callout. See [Using Hints](08_Using_Hints.md).
- **Workbook pane:** the guided walkthrough, with **Shrink workbook** and **Open in new tab**.

Scenario, objectives, target hostnames, and per-node IPs live in the workbook and the lab brief. Some labs also list target IPs in the connection panel; others ask you to scan the subnet.

<figure markdown>

![The Active Lab panel of a running lab showing the Active badge, timer, Stop Exercise and +1 Hour controls, VPN connection panel, flag form, and workbook pane](img/working-in-a-lab.png)

<figcaption>The Active Lab panel combines the session controls, the VPN connection details, the flag form, and the workbook in one workspace.</figcaption>
</figure>

## Reach the targets two ways

You attack the same lab targets from one of two starting points. The diagram below shows both.

```mermaid
flowchart LR
    subgraph Option A
        RB[RangeBox browser desktop] --> Bridge[Lab bridge]
    end
    subgraph Option B
        Local[Your machine] --> WG[WireGuard tunnel] --> Bridge
    end
    Bridge --> Tgt[Lab targets 10.100.x]
```

**RangeBox** is a Kali, Ubuntu, or REMnux desktop that runs in your browser, already on the lab network. Pick the image you need before you launch: Kali for general pentesting, Ubuntu for a plain Linux environment, and REMnux for malware analysis and reverse engineering. When a running exercise has RangeBox enabled, the Active Lab panel shows **Open RangeBox**. On a desktop, the exercise opens the combined workspace: RangeBox on the left, the briefing and flag on the right, and the workbook along the bottom. You need no VPN for RangeBox.

The RangeBox toolbar offers:

- **Stream quality**: High quality, Balanced, or Low bandwidth.
- **Ctrl+Alt+Del**: send the key combination to the guest.
- **Clipboard**: text-only send, get, and read.
- **Minimize** and **Fullscreen** (native fullscreen where the browser allows it).
- **Pop out**: move the desktop into its own resizable window while the main tab keeps the briefing, notes, and workbook.

!!! note "Standalone RangeBox"
    The **RangeBox** item in the sidebar opens a standalone practice desktop. It is not attached to a lab, so use it for tool access or connectivity checks. To work an exercise with the lab network and flag dock, launch RangeBox from that exercise instead.

!!! note "Phones and tablets"
    The in-browser desktop needs a keyboard and mouse for comfortable lab work.
    On a phone, the platform shows a desktop-recommended notice instead of the
    embedded viewer. See [Using a Mobile Device](19_Using_a_Mobile_Device.md).

At the bottom of the RangeBox window, the **lab dock** shows the lab name,
its subnet, and the target IPs when the exercise is built to reveal them. The
same dock contains a **Flag** field and **Submit flag** button. Copying an
`OCR{...}` value inside the desktop fills the field automatically; if it does
not, use **Paste** or Ctrl+V. You can capture the flag in the desktop, submit it
without leaving RangeBox, and then close the window or return to the exercise. A
correct flag shows the usual success message and tears the environment down.

!!! tip "Workbook and flags in one place"
    In the workspace, the workbook is the full-width pane under the desktop. It
    scrolls on its own and hides the wiki header and sidebars, so you can read a
    step while the RangeBox stays open. Use **Expand** for a taller pane or
    **Open in new tab** for a separate reading tab. The **Pop out** button moves
    the desktop to its own window if you want more room for the workbook.

!!! tip "Resize the workspace"
    On a wide screen, drag the vertical divider between the RangeBox and the
    exercise details to give the desktop more room. Drag the horizontal divider
    above the workbook to change how much height the workbook gets. The split is
    remembered in your browser; **Reset layout** restores the defaults. The
    dividers also work with the arrow keys when focused.

**Your own machine** reaches the same targets over the WireGuard tunnel. Use this when you prefer your local tools.

## Steps to start working

1. Read the lab brief and the **New to this exercise?** prompt at the top of the panel.
2. Note the subnet in **Connect to this lab over the VPN**, or open the workbook for target details.
3. Connect: launch RangeBox from the panel, or activate your VPN tunnel and open **Open VPN Setup** for the config.
4. Open the workbook with **Open workbook** for guided steps when one is provided.
5. Work toward the objectives, then submit your flag.

**What you should see:** the lab subnet in the connection panel, a reachable target once your tunnel or desktop is up, and the workbook pane if the lab ships one.

## When something looks off

!!! note "Per-node IPs only appear for some labs"
    Target IPs in "Your targets:" show only when the lab is built to expose them. Other labs ask you to scan the subnet to find hosts. Both are normal.

If a target will not respond, see [Cannot Reach Lab Target](../07_Troubleshooting/05_Cannot_Reach_Lab_Target.md).
