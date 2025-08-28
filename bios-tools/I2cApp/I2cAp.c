/** @file
  UEFI application to interact with I2C HID devices.
  Provides functionality to read and print HID descriptors.

  Copyright (c) 2006 - 2008, Intel Corporation. 
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/

#include <Uefi.h>
#include <Library/PcdLib.h>
#include <Library/UefiLib.h>
#include <Library/UefiApplicationEntryPoint.h>
#include <Library/ShellLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Protocol/I2cEnumerate.h>
#include <Protocol/I2cHost.h>
#include <Protocol/I2cIo.h>
#include <Protocol/I2cMaster.h>
#include <Protocol/I2cBusConfigurationManagement.h>
#include <Pi/PiI2c.h>
#include <I2CMaster/Dxe/PortA0Pio/I2cPort.h>

#define HID_DESCRIPTOR_LENGTH  0x1E
#define DEFAULT_HID_ADDR       0x1
#define DEFAULT_BUS_FREQUENCY  400000   // 400 KHz

// Global variables
STATIC UINT8 DebugFlag = 0;
STATIC UINT8 SlaveAddress = 0;
STATIC UINT16 HidAddr = DEFAULT_HID_ADDR;
STATIC UINTN BusFrequency = DEFAULT_BUS_FREQUENCY;
STATIC INTN HandleIndex = -1;  // -1 means scan all

extern EFI_SYSTEM_TABLE *gST;
extern EFI_BOOT_SERVICES *gBS;

// Shell command-line parameters
STATIC CONST SHELL_PARAM_ITEM ParamList[] = {
  {L"-h",     TypeFlag},   // Help flag
  {L"-hid",   TypeFlag},   // Get HID descriptor
  {L"-d",     TypeFlag},   // Debug mode
  {L"-index", TypeValue},  // Optional: handle index
  {L"-addr",  TypeValue},  // Optional: HID descriptor base address
  {L"-freq",  TypeValue},  // Optional: I2C bus frequency
  {NULL,      TypeMax}
};

#pragma pack (1)
typedef struct {
  UINT16 DescLength;
  UINT16 BcdVersion;
  UINT16 ReportDescLength;
  UINT16 ReportDescRegister;
  UINT16 InputRegister;
  UINT16 MaxInputLength;
  UINT16 OutputRegister;
  UINT16 MaxOutputLength;
  UINT16 CommandRegister;
  UINT16 DataRegister;
  UINT16 VendorID;
  UINT16 ProductID;
  UINT16 VersionID;
  UINT32 Reserved;
} HID_DESCRIPTOR_FORMAT;
#pragma pack ()

/**
  Get HID descriptor from an I2C device.

  @param[in]  I2cMaster            Pointer to EFI_I2C_MASTER_PROTOCOL.
  @param[in]  SlaveAddress7Bits    7-bit I2C device address.
  @param[in]  HidDescriptorAddress HID descriptor base register address.
  @param[out] HidDescriptor        Pointer to HID_DESCRIPTOR_FORMAT.

  @retval EFI_SUCCESS   HID descriptor retrieved successfully.
  @retval Others        Error retrieving descriptor.
**/
EFI_STATUS
EFIAPI
GetHidDescriptor(
  EFI_I2C_MASTER_PROTOCOL   *I2cMaster,
  IN UINT8                  SlaveAddress7Bits,
  IN UINT16                 HidDescriptorAddress,
  OUT HID_DESCRIPTOR_FORMAT *HidDescriptor
  )
{
  EFI_STATUS                Status;
  EFI_I2C_REQUEST_PACKET    *RequestPacket;

  RequestPacket = AllocateZeroPool (sizeof (EFI_I2C_REQUEST_PACKET) + sizeof(EFI_I2C_OPERATION));
  if (RequestPacket == NULL) {
    return EFI_OUT_OF_RESOURCES;
  }

  RequestPacket->OperationCount = 2;
  RequestPacket->Operation[0].Flags = 0;
  RequestPacket->Operation[0].Buffer = (void *)&HidDescriptorAddress;
  RequestPacket->Operation[0].LengthInBytes = sizeof(UINT16);
  RequestPacket->Operation[1].Flags = I2C_FLAG_READ;
  RequestPacket->Operation[1].Buffer = (void *)HidDescriptor;
  RequestPacket->Operation[1].LengthInBytes = sizeof (HID_DESCRIPTOR_FORMAT);

  Status = I2cMaster->StartRequest (I2cMaster, SlaveAddress7Bits, RequestPacket, NULL, NULL);

  FreePool (RequestPacket);
  return Status;
}

/**
  Entry point for the I2C HID tool.

  Usage:
    I2cAp.efi -hid <SlaveAddress> [-index N] [-addr HID_ADDR] [-freq HZ] [-d]

  Options:
    -h          Show this help message.
    -hid        Retrieve HID descriptor from I2C device at <SlaveAddress>.
    -index N    Use specific I2C Master Handle index. If omitted, scan all.
    -addr VAL   HID descriptor base address (default: 0x1).
    -freq VAL   I2C bus frequency in Hz (default: 400000).
    -d          Enable debug output.

  Example:
    I2cAp.efi -hid 0x10 -index 2 -addr 0x1 -freq 100000
**/
EFI_STATUS
EFIAPI
UefiMain (
  IN EFI_HANDLE        ImageHandle,
  IN EFI_SYSTEM_TABLE  *SystemTable
  )
{
  EFI_STATUS                      Status;
  EFI_I2C_MASTER_PROTOCOL          *I2cMaster;
  EFI_HANDLE                       *Handles = NULL;
  UINTN                            HandleNum = 0;
  UINT32                           Index;
  LIST_ENTRY                       *Package;
  CHAR16                           *ProblemParam;
  CONST CHAR16                     *Param1;
  HID_DESCRIPTOR_FORMAT            HidDescriptor;

  gBS = SystemTable->BootServices;
  gST->ConOut->ClearScreen(gST->ConOut);
  Print(L"I2C HID Tool\n");

  Status = ShellInitialize();
  if (EFI_ERROR(Status)) {
    return Status;
  }

  Status = ShellCommandLineParse(ParamList, &Package, &ProblemParam, TRUE);
  if (EFI_ERROR(Status)) {
    Print(L"ShellCommandLineParse failed: %r\n", Status);
    return Status;
  }

  if (ShellCommandLineGetFlag(Package, L"-h")) {
    Print(L"Usage: I2cAp.efi -hid <SlaveAddress> [-index N] [-addr HID_ADDR] [-freq HZ] [-d]\n");
    Print(L"  -h          Show this help message.\n");
    Print(L"  -hid        Retrieve HID descriptor from I2C device.\n");
    Print(L"  -index N    Use specific I2C Master Handle index. If omitted, scan all.\n");
    Print(L"  -addr VAL   HID descriptor base address (default: 0x1).\n");
    Print(L"  -freq VAL   I2C bus frequency in Hz (default: 400000).\n");
    Print(L"  -d          Enable debug output.\n");
    return EFI_SUCCESS;
  }

  DebugFlag = ShellCommandLineGetFlag(Package, L"-d");

  Param1 = ShellCommandLineGetRawValue(Package, 1);
  if (Param1 != NULL) {
    SlaveAddress = (UINT8)ShellStrToUintn(Param1);
  }

  if (ShellCommandLineGetFlag(Package, L"-hid")) {
    CONST CHAR16 *Val;
    Val = ShellCommandLineGetValue(Package, L"-index");
    if (Val != NULL) {
      HandleIndex = (INTN)ShellStrToUintn(Val);
    }
    Val = ShellCommandLineGetValue(Package, L"-addr");
    if (Val != NULL) {
      HidAddr = (UINT16)ShellStrToUintn(Val);
    }
    Val = ShellCommandLineGetValue(Package, L"-freq");
    if (Val != NULL) {
      BusFrequency = (UINTN)ShellStrToUintn(Val);
    }

    Status = gBS->LocateHandleBuffer(
                    ByProtocol,
                    &gEfiI2cMasterProtocolGuid,
                    NULL,
                    &HandleNum,
                    &Handles
                    );
    if (EFI_ERROR(Status)) {
      Print(L"LocateHandleBuffer failed: %r\n", Status);
      return Status;
    }

    Print(L"Found %u I2C Master Handles\n", HandleNum);

    for (Index = 0; Index < HandleNum; Index++) {
      if (HandleIndex >= 0 && (INTN)Index != HandleIndex) {
        continue; // skip if specific index requested
      }

      Print(L"Using Handle[%u]\n", Index);

      Status = gBS->OpenProtocol(
        Handles[Index],
        &gEfiI2cMasterProtocolGuid,
        (VOID **)&I2cMaster,
        ImageHandle,
        NULL,
        EFI_OPEN_PROTOCOL_GET_PROTOCOL
        );
      if (EFI_ERROR(Status)) {
        Print(L"OpenProtocol failed: %r\n", Status);
        continue;
      }

      Status = I2cMaster->Reset(I2cMaster);
      if (EFI_ERROR(Status)) {
        Print(L"I2cMaster->Reset failed: %r\n", Status);
        continue;
      }

      Status = I2cMaster->SetBusFrequency(I2cMaster, &BusFrequency);
      if (EFI_ERROR(Status)) {
        Print(L"SetBusFrequency failed: %r\n", Status);
        continue;
      }

      ZeroMem(&HidDescriptor, sizeof(HID_DESCRIPTOR_FORMAT));
      Status = GetHidDescriptor(I2cMaster, SlaveAddress, HidAddr, &HidDescriptor);
      if (EFI_ERROR(Status)) {
        Print(L"GetHidDescriptor failed: %r\n", Status);
        continue;
      }

      Print(L"=== HID Descriptor ===\n");
      Print(L"DescLength        : %d\n", HidDescriptor.DescLength);
      Print(L"BcdVersion        : 0x%x\n", HidDescriptor.BcdVersion);
      Print(L"ReportDescLength  : %d\n", HidDescriptor.ReportDescLength);
      Print(L"ReportDescRegister: 0x%x\n", HidDescriptor.ReportDescRegister);
      Print(L"InputRegister     : 0x%x\n", HidDescriptor.InputRegister);
      Print(L"MaxInputLength    : %d\n", HidDescriptor.MaxInputLength);
      Print(L"OutputRegister    : 0x%x\n", HidDescriptor.OutputRegister);
      Print(L"MaxOutputLength   : %d\n", HidDescriptor.MaxOutputLength);
      Print(L"CommandRegister   : 0x%x\n", HidDescriptor.CommandRegister);
      Print(L"DataRegister      : 0x%x\n", HidDescriptor.DataRegister);
      Print(L"VendorID          : 0x%x\n", HidDescriptor.VendorID);
      Print(L"ProductID         : 0x%x\n", HidDescriptor.ProductID);
      Print(L"VersionID         : 0x%x\n", HidDescriptor.VersionID);
      Print(L"Reserved          : 0x%x\n", HidDescriptor.Reserved);

      if (HidDescriptor.DescLength != 0x1E || HidDescriptor.BcdVersion != 0x0100) {
        Print(L"Invalid HID Descriptor!\n");
        Status = EFI_DEVICE_ERROR;
      }

      if (HandleIndex >= 0) {
        break; // only one if specific index requested
      }
    }

    if (Handles != NULL) {
      FreePool(Handles);
    }
  }

  ShellCommandLineFreeVarList(Package);
  return EFI_SUCCESS;
}
