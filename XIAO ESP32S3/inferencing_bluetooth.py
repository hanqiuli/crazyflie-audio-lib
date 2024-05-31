import asyncio
from bleak import BleakClient, BleakScanner

BLE_DEVICE_NAME = "Arduino"
LABEL_CHAR_UUID = "2101"

async def run():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    found = False

    for device in devices:
        print(f"Found device: {device.name}, Address: {device.address}")
        if device.name == BLE_DEVICE_NAME:
            found = True
            print(f"Found target device: {device.name}, Address: {device.address}")
            async with BleakClient(device) as client:
                def handle_notification(sender, data):
                    label = data.decode('utf-8')
                    print(f"Received label: {label}")

                await client.start_notify(LABEL_CHAR_UUID, handle_notification)

                print("Waiting for notifications...")
                await asyncio.sleep(1000)
                await client.stop_notify(LABEL_CHAR_UUID)
            break

    if not found:
        print(f"Device named {BLE_DEVICE_NAME} not found.")

asyncio.run(run())