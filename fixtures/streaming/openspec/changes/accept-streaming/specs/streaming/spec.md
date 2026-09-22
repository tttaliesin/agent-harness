# streaming specification

## Purpose

Provide a reproducible real execution example that verifies the original shared-skill capabilities without modifying a production product.

## ADDED Requirements

### Requirement: Real media recovery

The fixture SHALL publish a changing synthetic RTSP source, verify a bounded outage and decode genuinely new frames after source restart.

#### Scenario: Initial receive

- **WHEN** the source publishes
- **THEN** the decoder receives at least 12 frames with advancing timestamps and at least four distinct images

#### Scenario: Forced outage

- **WHEN** the owned source stops for at least two seconds
- **THEN** the live server reports unavailability and the decoder receives no frames

#### Scenario: Recovery

- **WHEN** the source restarts with a new epoch marker
- **THEN** readiness completes within 10 seconds and decoding within 12 seconds yields at least four images not observed before the outage

### Requirement: Browser receive

When browser verification is selected the fixture SHALL verify actual WebRTC reception after recovery.

#### Scenario: Decoded browser video

- **WHEN** a new browser receiver connects after recovery
- **THEN** inbound bytes, decoded frames and media time advance and at least four rendered images differ

#### Scenario: Missing browser

- **WHEN** the required browser executable is unavailable
- **THEN** the run is BLOCKED rather than passed

### Requirement: Resource isolation and evidence limits

The fixture SHALL isolate loopback ports, stream paths, output directories and owned processes while reporting CPU transport separately from product GPU or tracker acceptance.

#### Scenario: Concurrent tasks

- **WHEN** one fixture finishes while another runs
- **THEN** the first cleans only its owned resources and the second can continue receiving

#### Scenario: Scope of proof

- **WHEN** CPU synthetic media and browser checks pass
- **THEN** GPU inference, tracker identity and actual product forwarding remain explicitly unverified
