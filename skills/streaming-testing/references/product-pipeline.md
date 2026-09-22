# Product pipeline evidence

Use this reference when the approved scope includes inference, forwarding, or tracker behavior beyond the synthetic CPU transport fixture.
Have the product adapter call its existing commands and preserve the common evidence and failure rules; the shared workflow does not need product-name branches.

## Keep acceptance criteria independent

These observations prove different behavior.

| Criterion | Required observation |
| --- | --- |
| Synthetic source | Real FFmpeg publication and receiver-side decoded changing frames |
| Outage | Defined interruption, live-server unavailability, and no received frames |
| Recovery | New source-epoch frames received within the approved deadline |
| Browser receive | Actual WebRTC inbound bytes, decoded-frame growth, and rendered-pixel changes |
| Product forwarding | Frames observed after the actual product route, with source/frame correlation |
| GPU inference | Actual model loaded on the required device, inference executed, and checked outputs |
| Tracker identity | Known object trajectories matched against expected identity behavior across the chosen interruption |

## Exercise the real route

Point the product's input at the isolated synthetic RTSP source, then receive from the product's actual WebRTC output.
Record model and configuration versions, input dimensions, output timestamps, device/runtime identification, detection assertions, and latency limits selected by product policy.
For GPU acceptance, execute the real model on the required GPU and retain runtime/device and inference evidence.
A GPU inventory command alone, a CPU substitute, or a skipped test does not prove GPU inference.

Use an annotated sequence containing the same identifiable objects before and after interruption for tracker tests.
Define whether reconnect preserves or intentionally resets identity, the permitted gap, and the expected association; compare actual tracked outputs to those expectations.
The synthetic fixture's red-to-blue corner proves a new source epoch and does not establish tracker identity continuity.

## Diagnose the receiving boundary

Inspect transport availability, codec compatibility, signaling, ICE connectivity, decoder counters, and rendered frames in that order as applicable to the observed failure.
For MediaMTX browser tests, H264 baseline without B-frames avoids a documented WebRTC incompatibility.
Keep STUN/TURN disabled for the loopback fixture and advertise only loopback candidates.
For a product requiring NAT traversal, test its approved network path separately.

Consult the [MediaMTX WebRTC guidance](https://mediamtx.org/docs/features/webrtc-specific-features) for codec and connectivity behavior, the [FFmpeg frame checksum format](https://ffmpeg.org/ffmpeg-formats.html#framemd5) for decoded frame evidence, and the [Playwright browser documentation](https://playwright.dev/docs/browsers) for the browser version tied to the test dependency.
Confirm command flags against the pinned executable before changing a fixture.
