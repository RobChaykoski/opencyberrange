# Crypto Rug Pull: Follow the Liquidity

## Before You Begin

- [ ] You have completed **Media Provenance**
- [ ] You have the exercise panel open
- [ ] You can open the token page and the ledger
- [ ] You will use only the simulated token and wallets
- [ ] You will not connect a real wallet or share a seed phrase

!!! warning "Defensive education only"
    There is no real token, wallet, or money in this lab. Never connect a real
    wallet to an unknown site, never share a seed phrase, and never send money
    to a “recovery agent.”

## Scenario

A community centre is considering a sponsorship from a token project called
$MILK. The site promises guaranteed weekly returns, a countdown, and a free
airdrop if supporters connect a wallet. The team is anonymous and the audit is
“pending.”

The coordinator asks you to look at the public ledger before anyone signs
anything. Trace the money, identify the wallet that removed the liquidity, and
recover the case token.

## Background: the scam menu

| Pattern | What it looks like |
|---|---|
| **Rug pull** | The team removes liquidity and disappears |
| **Fake airdrop** | “Free tokens” require connecting a wallet, which can drain approvals |
| **Pump and dump** | Coordinated hype, then the promoters sell at the top |
| **Influencer shilling** | Paid promotion disguised as personal opinion |
| **Recovery-agent scam** | A second layer that asks for a fee to “get your money back” |

The red-flag rule: **any two of guaranteed returns, urgency, wallet-connect
airdrop, anonymous team, influencer-only credibility, or no paper trail is a
reason to walk away.**

## Walkthrough

### Step 1: Read the offer

Open the token page and list the red flags you see. Do not connect a wallet.
The **Connect wallet** page is a simulation and will not ask for a seed phrase.

### Step 2: Open the ledger

Open `/ledger.json`. The ledger is the public record of simulated transfers.
Find:

- the treasury;
- the community wallet;
- the wallet that received the largest outgoing transfer from the community
  wallet;
- where that wallet sent the money next.

### Step 3: Follow the liquidity

The community wallet sends the liquidity to a new wallet. That wallet forwards
almost all of it to an external wallet and swaps a small remainder. That is the
exit.

Copy the wallet address that received the community liquidity.

### Step 4: Request the case file

Open:

```text
http://crypto.lab:8080/case?wallet=<the wallet you identified>
```

A wrong wallet returns 404. The correct wallet returns the case token. Copy the
`OCR{...}` value into the flag box.

### Step 5: Write the anatomy

Fill in five lines:

```text
Hook:
Trust builders:
The ask:
The exit:
Who profited:
```

Then add one line: “If I had already lost money, the next safe step is ___.”
Do not contact a recovery agent who asks for an upfront fee.

## What Just Happened?

- The offer used guaranteed returns, urgency, an anonymous team, and a
  wallet-connect airdrop.
- The ledger showed the liquidity moving from the community wallet to a new
  wallet and then offshore.
- The token page was marketing; the ledger was evidence.
- The “recovery agent” is a second-layer scam that targets people who have
  already lost money.
- Crypto transfers are usually irreversible, so prevention is the main control.

## The Fixes

| Problem | Fix |
|---|---|
| Guaranteed returns | Treat any guaranteed return as a red flag |
| Urgency | Slow down; a real opportunity survives a day of checking |
| Wallet-connect airdrop | Never connect a wallet to an unknown site |
| Anonymous team | Require a named entity, audit, and registered address |
| No paper trail | Check the ledger, the contract, and independent reporting |
| Recovery-agent offer | Stop paying and report through a trusted channel |

## Analysis Questions

**1. Which two red flags were strongest in this offer?**

**2. Which wallet received the community liquidity?**

**3. Why is the ledger stronger evidence than the token page?**

**4. Why is a recovery agent often a second scam?**

**5. Why does irreversibility make prevention more important than recovery?**

**6. What would you tell a friend who was about to connect a wallet?**

## Accessibility

- The token page, ledger, and case page are text. You can complete the exercise
  with a keyboard.
- Copy the wallet address from the ledger instead of retyping it.
- If JSON is difficult to read, ask for a plain-text ledger with one transaction
  per line.
- Never use a real wallet address or a real trading platform in this lab.
