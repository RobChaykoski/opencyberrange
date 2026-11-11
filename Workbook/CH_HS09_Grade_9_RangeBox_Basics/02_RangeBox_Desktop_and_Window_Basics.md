# RangeBox Desktop and Window Basics

This extra practice activity helps you tell the difference between your local
browser and the remote RangeBox desktop. You will open, switch, resize, and
safely close two approved applications.

## Before You Begin

Complete [Signing In and Opening RangeBox](01_First_Steps.md) first. You should
already have the RangeBox desktop open and a terminal available.

### Where everything is

| Term | What it means | What you should see |
|---|---|---|
| **Local device** | The laptop, desktop, or tablet in front of you. | Your own screen, keyboard, and mouse or touchpad. |
| **Browser controls** | The parts of your web browser, such as the address bar, tabs, back/forward buttons, refresh button, and browser window buttons. | The browser frame around the OpenCyberRange page. |
| **Address bar** | The field at the top of the browser that shows the page address. | The OpenCyberRange address your teacher gave you. |
| **Browser tab** | One page area inside your browser. | The tab showing the OpenCyberRange page. |
| **Remote workspace** | The RangeBox desktop running on the platform and shown inside your browser. | A Linux desktop with a panel, windows, and an application menu. |
| **RangeBox controls** | The toolbar in the RangeBox viewer. It includes **Clipboard**, **Minimize**, **Fullscreen**, and **Close** when the viewer is opened as its own page. | A toolbar above the remote desktop. |
| **Panel or taskbar** | The bar on the RangeBox desktop that shows open applications and shortcuts. | A bar at the bottom or side of the desktop. |
| **Application menu** | The menu used to open programs on the desktop. | A menu with categories or a list of programs. |
| **Application** | A program that runs on the desktop, such as File Manager or Terminal. | A window with its own title and controls. |
| **Window** | A framed area that holds an application. | A title bar, content area, and window controls. |
| **Title bar** | The top bar of a window. It shows the window title and controls. | The application name and **minimize**, **maximize**, and **close** controls. |
| **Minimize** | Hide a window without closing it. | The window disappears from the desktop and appears in the panel. |
| **Maximize** | Make a window fill the desktop. | The window becomes large; a restore control appears. |
| **Restore** | Return a maximized window to its previous size. | The window returns to its earlier size. |
| **Close** | Close an application window. | The application window disappears; RangeBox stays open. |
| **Fullscreen** | A RangeBox viewer control that expands the remote desktop. Browser fullscreen (`F11`) is different: it hides the browser controls. | The remote desktop fills more of the screen. |
| **Disconnect** | Lose or close the remote viewer connection. The lab may keep running. | The desktop view disappears or the viewer closes. |
| **Stop** | End the lab or RangeBox session. Unsaved work in the desktop may be lost. | The lab or RangeBox stops. |
| **Approved application** | An application the activity says is safe to open. In this activity, use **File Manager** and **Terminal**. | A window for that application. |

**Keyboard note:** you can use `Tab` and `Shift` + `Tab` to move between browser
controls, and `Enter` or `Space` to activate them. The standard XFCE desktop
shortcuts are often `Alt` + `Tab` to switch windows, `Alt` + `F4` to close,
`Alt` + `F9` to minimize, `Alt` + `F10` to maximize or restore, `Alt` + `F7` to
move, and `Alt` + `F8` to resize. If a shortcut does not work in your desktop,
use the window menu or ask your teacher.

### What you need

- [ ] The RangeBox desktop open from the first activity.
- [ ] A mouse, touchpad, or keyboard.
- [ ] A notes file for what you see.
- [ ] The patience to check what each control does before clicking it.

### Estimated time

About **10–15 minutes**.

### Scope

!!! warning "Stay inside the remote workspace"
    Use only the RangeBox desktop and the approved applications in this
    activity. Do not open real personal accounts, real email, or real websites
    from the practice desktop. If you use the terminal, the only target is the
    practice server shown in the activity.

### What you will be able to do

By the end of this activity, you will be able to:

- label the browser controls and the RangeBox controls;
- tell the local browser apart from the remote desktop;
- open, switch, resize, minimize, maximize, restore, and close approved
  applications;
- explain which close button closes an application, which one hides a window,
  and which one disconnects or stops the remote session;
- use keyboard alternatives for the main actions;
- follow directions that use labels and positions instead of colours.

## Close, Hide, or Stop?

This is the most important table in the activity. Read the label, not the colour.

| Control | What it does | Does it stop the lab? |
|---|---|---|
| **Application window close (X)** | Closes that application window. | No. RangeBox and the lab stay open. |
| **Application window minimize** | Hides the window in the panel. | No. The application is still running. |
| **Application window maximize** | Makes the window fill the desktop. | No. |
| **RangeBox Minimize** | Collapses or hides the RangeBox viewer. | No. The remote desktop may keep running. |
| **RangeBox Fullscreen** | Expands the viewer. | No. |
| **RangeBox Close** (when shown on its own page) | Leaves the RangeBox viewer and returns to the platform. | Not necessarily. The lab may keep running. |
| **Exercise panel Exit** | Leaves the exercise panel. | No. The lab keeps running. |
| **Stop Exercise** | Ends the exercise and its lab environment. | Yes. Unsaved desktop work may be lost. |
| **Stop RangeBox** (on the RangeBox page) | Stops the standalone RangeBox. | Yes. Unsaved desktop work may be lost. |
| **Browser tab close (X)** | Closes the local browser tab. | Not the same as Stop. The remote lab may keep running, but you lose the view. |
| **Browser window close (X)** | Closes the local browser window. | Not the same as Stop. The remote lab may keep running, but you lose the view. |
| **Browser fullscreen (`F11`)** | Hides the browser controls. | No. Use `F11` or `Esc` to leave it. |

When you are unsure, **minimize** first. Minimizing an application or the viewer
is safer than closing the browser tab or stopping the lab.

## Walkthrough: Two Approved Applications

You will use **File Manager** and **Terminal**. Follow one action per step and
check what you should see.

### Step 1: Find the panel and application menu

Look at the RangeBox desktop. Find the panel (the bar that shows open
applications) and the application menu.

**You should see:** a bar at the bottom or side of the desktop and a menu for
opening programs.

**If you do not see them:** move the mouse to the edge of the desktop or ask your
teacher. Do not close the browser tab.

### Step 2: Open File Manager

Open the application menu and choose **File Manager**. On some Kali desktops the
same program is listed as **Thunar**.

**You should see:** a File Manager window with folders on the desktop.

**Keyboard alternative:** use the application menu with `Tab` and `Enter`, or
press `Alt` + `F2` if your desktop uses the standard application launcher, then
type `thunar` and press `Enter`. If that does not work, use the menu.

### Step 3: Open a Terminal

Open the application menu and choose **Terminal**. On some desktops the same
program is listed as **Terminal Emulator** or **QTerminal**.

**You should see:** a terminal window with a command prompt. The File Manager
window is still open behind or beside it.

### Step 4: Switch to File Manager with the panel

Click the File Manager entry in the panel.

**You should see:** the File Manager window comes to the front.

### Step 5: Switch back with the keyboard

Press `Alt` + `Tab`.

**You should see:** the Terminal window comes to the front.

**If it does not work:** use the panel or the window menu. The keyboard shortcut
may be different on your desktop.

### Step 6: Move the File Manager window

Bring File Manager to the front, then drag its title bar to a different part of
the desktop.

**You should see:** the window moves without closing.

**Keyboard alternative:** press `Alt` + `F7`, use the arrow keys to move the
window, and press `Enter` to finish.

### Step 7: Resize the File Manager window

Drag one edge or corner of the File Manager window to make it smaller or larger.

**You should see:** the window changes size. The application stays open.

**Keyboard alternative:** press `Alt` + `F8`, use the arrow keys to resize, and
press `Enter` to finish.

### Step 8: Maximize and restore File Manager

Double-click the File Manager title bar, or use its **maximize** button.

**You should see:** File Manager fills the desktop. Use the **restore** button or
double-click the title bar again to return it to its earlier size.

**Keyboard alternative:** press `Alt` + `F10` to maximize or restore.

### Step 9: Minimize File Manager

Click the **minimize** button on the File Manager window.

**You should see:** File Manager disappears from the desktop and appears in the
panel. It is not closed.

**Keyboard alternative:** press `Alt` + `F9`.

### Step 10: Restore File Manager

Click the File Manager entry in the panel.

**You should see:** the File Manager window returns.

### Step 11: Close File Manager

Click the **close** button (X) on the File Manager window.

**You should see:** File Manager closes. The RangeBox desktop and the Terminal
window are still open.

**Keyboard alternative:** select File Manager and press `Alt` + `F4`.

### Step 12: Close the Terminal

Click the **close** button on the Terminal window, or press `Alt` + `F4`.

**You should see:** the Terminal closes. RangeBox is still open. You have not
stopped the lab.

### Step 13: Test RangeBox Minimize

In the RangeBox toolbar, click **Minimize**.

**You should see:** the viewer collapses or hides. The remote desktop is not
necessarily stopped.

### Step 14: Restore RangeBox

Click **Expand** or the control that restores the viewer.

**You should see:** the RangeBox desktop returns. If the viewer does not return,
look for the RangeBox tab or the **Open RangeBox** button in the exercise panel.

### Step 15: Test RangeBox Fullscreen

Click **Fullscreen** in the RangeBox toolbar.

**You should see:** the remote desktop expands. Click **Exit FS** to leave
RangeBox fullscreen.

Remember: **RangeBox Fullscreen** is not the same as **browser fullscreen**.
Browser fullscreen (`F11`) hides the browser controls; RangeBox fullscreen
expands the viewer.

### Step 16: Do not use the browser tab as an application close button

Leave the browser tab open. Do not click the browser tab's **X** to close an
application; that closes your local view, not the application inside RangeBox.

**You should see:** the RangeBox desktop still available for the next activity.

## Success Check: Local or Remote?

Answer these questions in your notes.

| Question | Your answer |
|---|---|
| Which window is on your local device: the browser or the RangeBox desktop? | |
| Which window is remote: the browser or the RangeBox desktop? | |
| What did closing the File Manager window do to RangeBox? | |
| What did minimizing RangeBox do to the lab? | |
| What does **Exit** in the exercise panel do? | |
| What does **Stop Exercise** do? | |
| What happens if you close the browser tab? | |
| Which keyboard shortcut switches windows? | |

A strong answer can explain that the browser is local, RangeBox is remote,
closing an application does not stop the lab, and **Stop Exercise** is the
action that ends the lab.

## What Success Looks Like

You are ready to continue when you can show:

- two approved applications opened, switched, resized, and closed;
- RangeBox still open after the applications were closed;
- one example of minimizing and restoring RangeBox;
- one example of RangeBox fullscreen and returning to the normal view;
- a clear explanation of the difference between closing an application,
  minimizing the viewer, exiting the panel, and stopping the lab.

## If You Get Stuck

| Problem | What to check | Safe next step |
|---|---|---|
| A window is hidden | It may be minimized. | Look in the panel and click its entry. |
| You cannot find the application menu | The panel may be at a different edge. | Move the mouse to the edge of the desktop or ask your teacher. |
| A keyboard shortcut does not work | Your desktop may use a different shortcut. | Use the mouse, the window menu, or ask your teacher. |
| The browser tab closed | The local view is gone, but the lab may still run. | Reopen the platform, sign in if needed, and open the exercise and RangeBox again. |
| RangeBox says it is disconnected | The viewer lost its connection. | Use **Reconnect** if shown, or stop and relaunch the exercise. |
| You accidentally clicked Stop Exercise | The lab is ending. | Launch the exercise again. Unsaved desktop work may be lost. |
| You are not sure which desktop you are looking at | Your local browser and the remote desktop are different layers. | If you see your own device's normal desktop, you are not in RangeBox. Return to the platform and open RangeBox. |
| A control is hard to see or reach | The page may be zoomed or the control may be small. | Use browser zoom, `Tab` and `Enter`, or ask your teacher. |

## Analysis Questions

1. Which close button closes only an application?
2. Which control hides a window without closing the application?
3. Which action leaves the exercise panel but keeps the lab running?
4. Which action ends the lab?
5. What does closing the browser tab do to your local view, and what might it
   not do to the remote lab?
6. How can you switch windows without a mouse?

## Key Takeaways

- Your browser is local. RangeBox is the remote practice desktop.
- Closing an application window does not stop RangeBox or the lab.
- Minimizing an application or the RangeBox viewer is safer than closing the
  browser tab.
- **Exit** leaves the panel; **Stop Exercise** and **Stop RangeBox** end the lab
  or desktop.
- RangeBox **Fullscreen** and browser fullscreen (`F11`) are different controls.
- Use labels and positions, not colours, to identify controls.
- Keyboard shortcuts can help, but the window menu and panel are always
  available alternatives.
