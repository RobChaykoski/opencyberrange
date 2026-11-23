# AI02 Chapter Review

## Check Your Understanding

1. **Instruction versus data.** In your own words, why should retrieved content
   never be treated as an instruction?
2. **Tool scope.** List three tools a GRC intake agent might legitimately need
   and one it probably should not have.
3. **Confused deputy.** Who has the authority in the TrailGuard exercise: Priya
   Patel, Elena Vance, or the agent? Why does that matter?
4. **Non-human identity.** Why is `svc-trailguard-bot` more dangerous than a
   human account with the same intent?
5. **Detection.** What would you log to investigate an unexpected export?
6. **Defence in depth.** Which single control would you add first, and what
   would still be possible after adding it?
7. **Machine identity.** In the capstone, why is the leaked token useful even
   after the agent-to-agent trust gap is fixed?
8. **Semantic forensics.** Which fields would let you prove that a specific
   document caused a specific tool call?
9. **Governance.** Who should own `svc-trailguard-bot`, and why is an ownerless
   identity a finding rather than a paperwork problem?

## Practical Checklist

- [ ] I analyzed the benign LumenPay report and saw no tool calls.
- [ ] I identified the sentence that changed TrailGuard's plan.
- [ ] I captured the flag from the export response.
- [ ] I can explain the difference between prompt injection and agent hijacking.
- [ ] I can name at least three controls that would reduce the impact.
- [ ] I can describe how least-privilege scopes would limit
  `svc-trailguard-bot`.
- [ ] I enumerated the capstone API and found the leaked machine credential.
- [ ] I reconstructed the agent-to-agent decision chain from telemetry.
- [ ] I proposed workload identity, scoped OAuth, policy-as-code, and approval.

## Next Steps

The next Release 6 labs continue the Trailline story:

- a poisoned model or dependency in the TrailGuard pipeline;
- detection-as-code against automated swarms;
- a post-quantum migration for a legacy Trailline service.

Return to the web exploitation stream if you want more input-validation practice
before continuing. The core habit carries over: treat model input and model
output as untrusted, and treat every tool call as a security decision.
