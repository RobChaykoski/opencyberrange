VOIP CALL RECONSTRUCTION - EVIDENCE PACKAGE
============================================

The help desk received a suspicious call. The network team captured the SIP
signalling and the RTP media stream from the call.

Files:
  voip-call.pcap    SIP and RTP capture
  reconstruct.py    Optional helper that rebuilds the u-law audio as a WAV

The capture is fictional training data. The audio was synthesized for this
exercise, and the people and phone numbers are not real.

Suggested starting points:
  - Open the capture in Wireshark and filter for SIP.
  - Find the INVITE and the SDP offer.
  - Follow the RTP media stream, reconstruct the audio, and listen.
  - Review the SIP headers after you have the audio.
