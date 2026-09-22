---
name: streaming-testing
description: Test RTSP publication, decoded frame delivery, bounded outage and recovery, and browser WebRTC reception with MediaMTX and FFmpeg fixtures. Use for streaming transport regressions and product video pipeline acceptance; distinguish GPU inference and tracker identity from media transport.
---

# Streaming testing

Use the product's existing verification commands and approved timing criteria.
MediaMTX provides an isolated synthetic source for the test; keep the product's existing media server and inference path.

## Choose the evidence

Record the candidate, source, expected receiver, startup deadline, outage duration, recovery deadline, and whether browser or GPU execution is required.
For the reusable CPU fixture, use the [repository streaming fixture](https://github.com/tttaliesin/agent-harness/tree/main/fixtures/streaming) at the same checked-out revision as the skills.
That fixture includes pinned native tools, loopback configuration, a changing synthetic source, and a reproducible browser receiver.
It is optional example source; this installed skill and its probe are self-contained.

For a product RTSP source, use the bundled [decoded-frame probe](scripts/stream_probe.py) with Python 3.12 or newer and FFmpeg supporting RTSP TCP and `framemd5`.
Run it from the product's task directory, substituting the installed skill path, authorized source, executable, and a new report path:

```sh
python <SKILL_DIR>/scripts/stream_probe.py rtsp://127.0.0.1:18554/test --ffmpeg <FFMPEG> --frames 12 --timeout 12 --output receive.json
```

The probe uses a bounded decoder process and requires advancing timestamps and at least four distinct decoded image hashes.
It is appropriate for deliberately moving synthetic content; choose an explicit product criterion for a legitimately static camera scene.
Keep credentials out of the URL because the command and decoder diagnostics are preserved in the report.
Exit `0` means observed frames passed these criteria, `1` means failed evidence or timeout, and `2` means an unavailable executable.
An existing output file is rejected so a previous passing report cannot mask a failed rerun.

## Exercise interruption and recovery

1. Start only task-owned resources on dynamically selected loopback ports, with unique stream paths and report directories.
   Confirm MediaMTX path readiness and decode frames from the actual receiving side.
2. Interrupt the owned publisher for a bounded interval.
   Confirm the live server reports the path unavailable and the receiver gets no frames; an unrelated executable failure is not evidence of an outage.
3. Restart publication with a visibly different source epoch marker.
   Require new decoded hashes after restart within the recovery deadline and record the measured duration.
   A socket reconnect, unchanged frame count, or replayed pre-outage image is insufficient.
4. If browser reception is required, execute the saved browser test against the actual WebRTC path.
   Require increasing inbound RTP bytes, decoded frames, media time, and changing rendered pixels.
   A loaded player, successful signaling response, screenshot, or TCP connection alone is insufficient.
5. Stop only recorded owned processes and children, close their handles, and report cleanup failures.
   Preserve another task's listeners, containers, browser sessions, and output directories.

## Connect product acceptance

For RTSP → inference → WebRTC, GPU execution, or tracking requirements, read [product pipeline evidence](references/product-pipeline.md).
Keep transport, browser receive, inference, and tracker identity outcomes separate.
Report unavailable required resources as `BLOCKED` and unexecuted checks as `NOT_RUN`; neither can satisfy an acceptance criterion.
Local reports support development feedback and must not be presented as trusted CI, production health, or current-candidate evidence after relevant source changes.
