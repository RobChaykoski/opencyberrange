# Signing In and Opening RangeBox

This first activity has two parts. First you sign in and open the correct
workspace. Then you run four simple commands inside RangeBox.

## Before You Begin

### Where everything is

The words in this table are used throughout the activity. Read them before you
start.

| Place or term | What it is | What you should see |
|---|---|---|
| **Student device** | The laptop, desktop, or tablet in front of you. | Your own screen, keyboard, and mouse or touchpad. |
| **Web browser** | The app you use to visit websites, such as Chrome, Edge, Firefox, or Safari. | A browser window with an address bar and tabs. |
| **OpenCyberRange page** | The website your teacher gave you. It has the sign-in form, Exercises, and the exercise page. | A page with **Username**, **Password**, and **Sign In**. |
| **RangeBox desktop** | The temporary Linux desktop provided by the platform. It runs inside the browser. | A desktop with a taskbar, windows, and an application menu. |
| **RangeBox terminal** | The text window inside RangeBox where you type commands. | A command prompt where you can type. |
| **Command prompt** | The place in the terminal where you type. It often shows your account and current folder. | A line waiting for your command. |
| **Target** | The practice server for this activity. | `rangebox.lab:8080` in this activity. It is the only system you may use. |
| **Account** | Your OpenCyberRange login. | The username and password your teacher gave you. Do not share them. |
| **RangeBox account** | The temporary Linux account inside the desktop. | The name printed by `whoami`. It is not your OpenCyberRange password. |

Commands run in the **RangeBox terminal**, not in your device's normal terminal.
If you see a terminal on your own device, you are in the wrong place.

### What you need

- [ ] The OpenCyberRange address from your teacher. Do not guess the address.
- [ ] Your OpenCyberRange username and password from your teacher.
- [ ] A browser on a laptop or desktop. A tablet with a keyboard may work; a
      phone is not recommended for the desktop activities.
- [ ] A notes file for what you see and what you try.

**Keyboard note:** you can use `Tab` and `Shift` + `Tab` to move between fields
and buttons, and `Enter` or `Space` to activate them. If you use a screen reader
or another assistive tool, tell your teacher what you need.

### Safe sign-in rules

- Type your password only on the OpenCyberRange sign-in page your teacher gave
  you.
- Do not share your password, write it in the workbook, paste it into the
  terminal, or include it in a screenshot.
- If you take a screenshot for help, hide personal information and never capture
  the password field.
- Do not save your password on a shared computer. Sign out when you finish.
- Do not enter real personal information into the practice desktop. Use only the
  practice account and the fictional lab.

### Estimated time

About **10–15 minutes**. The first RangeBox launch can take about a minute while
the desktop starts.

### Scope

!!! warning "Only the assigned target"
    Use only the target shown in this activity. In this activity the target is
    `rangebox.lab:8080`. Do not try the commands on your own device, your school
    network, another student's lab, or the internet. If you are unsure, stop and
    ask your teacher.

### What you will be able to do

By the end of this activity, you will be able to:

- sign in safely and recognise the OpenCyberRange page;
- open the Grade 9 exercise and launch RangeBox;
- tell the difference between your device, the browser, the OpenCyberRange page,
  the RangeBox desktop, and the RangeBox terminal;
- run `pwd`, `whoami`, `ls`, and `curl` in the RangeBox terminal;
- find the training token in the welcome file;
- recover from a wrong password, an expired session, a blocked pop-up, or a slow
  launch.

## Part 1: Sign In

Follow one step at a time. After each action, check what you should see.

### Step 1: Open your web browser

Open the browser on your device.

**You should see:** a browser window with an address bar and at least one tab.

### Step 2: Go to the OpenCyberRange address

Click the address bar and type the address your teacher gave you. Press `Enter`.

**You should see:** the OpenCyberRange sign-in page with **Username**,
**Password**, and **Sign In**.

If you see a different website, stop. Check the address with your teacher before
typing your password.

### Step 3: Click the Username field

Click the field labelled **Username**.

**You should see:** a cursor in the field and the label **Username** above it.

**Keyboard alternative:** press `Tab` until the Username field is focused.

### Step 4: Type your username

Type the username your teacher gave you.

**You should see:** your username in the field.

### Step 5: Click the Password field

Click the field labelled **Password**.

**You should see:** a cursor in the field. The characters you type will appear as
dots.

### Step 6: Type your password

Type your password carefully. Check that **Caps Lock** is off.

**You should see:** dots in the Password field. Use the **Show password** button
(the eye icon) only if you need to check what you typed and no one is looking at
your screen.

### Step 7: Click Sign In

Click **Sign In**.

**You should see:** your dashboard, your Exercises page, or a message about your
account.

If your account asks for a verification code, enter the current code from your
teacher or authenticator app and choose **Verify & Sign In**.

**Keyboard alternative:** press `Tab` to reach **Sign In**, then press `Enter`.

## Part 2: Open the Correct Workspace

### Step 8: Open Exercises

Find **Exercises** in the page or sidebar and click it.

**You should see:** the exercise tracks or the Exercises page.

### Step 9: Open the High School exercises

Choose **High School**.

**You should see:** the Grade 9, Grade 10, Grade 11, and Grade 12 levels, or the
levels your teacher has made available.

### Step 10: Open Grade 9

Choose the **Grade 9** level.

**You should see:** the list of Grade 9 activities, including **RangeBox First
Steps**.

### Step 11: Open RangeBox First Steps

Click **RangeBox First Steps**.

**You should see:** the exercise page with a **Launch** button and the exercise
details.

### Step 12: Launch the exercise

Click **Launch**.

**You should see:** the status change to **Starting**, then **Running**. If the
page shows **Launch RangeBox** instead, choose that.

### Step 13: Open RangeBox if it does not open automatically

If the RangeBox desktop does not appear, look for **Open RangeBox** in the
exercise panel and click it.

**You should see:** a RangeBox page or panel with a **Connecting** or
**Starting** message.

### Step 14: Choose Kali if you are asked

If the page asks which desktop to use, choose **Kali**. This chapter uses Kali.

**You should see:** the Kali desktop loading.

### Step 15: Wait for the desktop

Wait for the desktop to finish loading. The first launch can take about a
minute. Do not click the launch button repeatedly.

**You should see:** a desktop with a taskbar, windows, and an application menu.

### Step 16: Open the terminal

Open the terminal from the taskbar (the bar that shows open apps) or the
application menu (the menu for opening programs).

**You should see:** a terminal window with a command prompt.

You are now in the correct workspace. The commands in Part 3 run in this
terminal.

## Part 3: Your First Commands

### Step 17: Find your current folder

Type this command and press `Enter`:

```bash
pwd
```

**You should see:** a path such as `/home/kali`. That is your current folder
inside RangeBox.

### Step 18: Find your RangeBox account name

Type this command and press `Enter`:

```bash
whoami
```

**You should see:** the temporary account name inside the RangeBox desktop. This
is not your OpenCyberRange username.

### Step 19: List the current folder

Type this command and press `Enter`:

```bash
ls
```

**You should see:** folders such as `Desktop`, `Documents`, and `Downloads`.

### Step 20: Retrieve the welcome file

Type this command and press `Enter`:

```bash
curl http://rangebox.lab:8080/welcome.txt
```

**You should see:** the contents of the welcome file. Look for the line that
starts with `Training token:` and copy the `OCR{...}` value. The `OCR{...}` value
is the **flag**, a completion code for the activity.

### Step 21: Submit the flag

Paste the complete `OCR{...}` value into the **Submit Flag** box in the exercise
panel and click **Submit**.

**You should see:** a success message or a flag-captured message.

## What Success Looks Like

You are ready to continue when you can show:

- the RangeBox terminal prompt on screen;
- the output of `pwd`, `whoami`, `ls`, and `curl`;
- the training token from the welcome file;
- a clear explanation of which computer is the target and where the commands
  ran;
- one recovery step you would use if sign-in or launch failed.

## If You Do Not Have RangeBox

Open the lab browser and visit:

```text
http://rangebox.lab:8080/welcome.txt
```

You will see the same file. The commands are worth learning, but the browser
path lets you finish the activity on a device without a terminal. Ask your
teacher which path to use.

## If You Get Stuck

| Problem | What to check | Safe next step |
|---|---|---|
| The password is rejected | Check **Caps Lock**, the username, and the password with **Show password**. | Ask your teacher about a password reset. Do not share your password or screenshot it. |
| The account is waiting for approval | Your teacher may need to approve the account. | Tell your teacher. Do not create a second account. |
| You are returned to sign-in | Your session (your signed-in time) may have expired. | Sign in again. Keep your notes outside the lab; an expired session may lose temporary desktop work. |
| A new tab or window does not open | The browser may have blocked a pop-up (a new window or tab). | Look for the blocked-pop-up icon in the address bar and allow it for the platform address. Then try **Launch** again. |
| The desktop is slow to appear | The first launch can take about a minute. | Wait and watch the status. Do not click repeatedly. If it takes more than a few minutes, stop and launch again, or ask your teacher. |
| A button or field is hard to reach | The page may be zoomed or the control may need keyboard focus. | Use `Tab` and `Shift` + `Tab` to move, and `Enter` or `Space` to activate. Try browser zoom. Ask your teacher if it still does not work. |
| You see a terminal on your own device | You are not in the RangeBox terminal. | Close it and return to the RangeBox page. Commands must run inside RangeBox, not on your device. |
| RangeBox is not available | Your deployment may not offer it. | Use the lab browser or the terminal your teacher provides. |
| The flag is rejected | The value may have a typo or the wrong case. | Copy the whole `OCR{...}` value exactly. Do not guess or change it. |

## Analysis Questions

1. Which window is the RangeBox desktop, and which window is your device's
   normal browser?
2. Where do the commands run in this activity?
3. Which computer is the target, and which computer is your workstation?
4. What would you do if your password did not work?
5. What would you do if a new tab were blocked?

## Key Takeaways

- Sign in only on the OpenCyberRange address your teacher gave you.
- Your OpenCyberRange password is private. Never share it or put it in a
  screenshot.
- Your student device, the browser, the OpenCyberRange page, the RangeBox
  desktop, and the RangeBox terminal are different places.
- Commands run in the RangeBox terminal, and the target is only the practice
  server shown in the activity.
- If something fails, check the common recovery steps before trying a different
  command.
