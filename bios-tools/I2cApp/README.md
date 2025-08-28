# UEFI I2C Application

This is a sample UEFI shell application demonstrating how to:
- Locate I2C master handles
- Initialize I2C masters
- Read HID descriptors
- Handle errors gracefully

## Flow Diagram

```text
Start
  │
  ▼
Locate I2C Master Handles
  │
  ├─> Error? ───> Print Error & Exit
  │
  ▼
For each I2C Handle
  │
  ▼
  [Initialize I2C Master]
    │
    ├─> Call HandleProtocol -> Get I2cMaster
    │
    ▼
    ├─> Call I2cMaster->Reset
    │
    ▼
    ├─> Call I2cMaster->SetBusFrequency
    │
    ▼
    └─> Any step above failed? ──> Print Error & Continue to next Handle
        │
        ▼
  [Read and Validate HID Descriptor]
    │
    ├─> GetHidDescriptor (Use the I2cMaster->StartRequest, Slave Address, HID Address)
    │
    ▼
    └─> Error or Invalid DescLength/BcdVersion? ──> Print Error & Continue to next Handle
        │
        ▼
  [Print HID Descriptor Info]
    │
    └─> Print HID_DESCRIPTOR_FORMAT
        │
        ▼
  Next Handle
  │
  ▼
End
