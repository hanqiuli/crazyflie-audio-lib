import asyncio
from bleak import BleakClient, BleakScanner

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "abcdef01-2345-6789-abcd-ef0123456789"
NOTIFY_CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdeff"

notification_received = asyncio.Event()

async def handle_notification(sender, data):
    print(f"Notification from {sender}: {data.decode('utf-8')}")
    notification_received.set()

async def send_command(client, command):
    try:
        await client.write_gatt_char(CHARACTERISTIC_UUID, command.encode())
        print(f"Command '{command}' sent to {client.address}")
    except Exception as e:
        print(f"Failed to send command: {e}")

async def connect_and_listen(esp32_device):
    async with BleakClient(esp32_device) as client:
        try:
            await client.connect()
            print(f"Connected to {esp32_device.address}")

            # Start notification handler
            await client.start_notify(NOTIFY_CHARACTERISTIC_UUID, handle_notification)

            while True:
                command = input("Enter command (base filename or 'rec') or 'exit' to quit: ")
                if command.lower() == 'exit':
                    break
                await send_command(client, command)

                # Only wait for notification if the command is 'rec'
                if command.lower() == 'rec':
                    print("Waiting for notification...")
                    await notification_received.wait()
                    notification_received.clear()

            # Stop notification handler
            await client.stop_notify(NOTIFY_CHARACTERISTIC_UUID)

        except Exception as e:
            print(f"Failed to connect or communicate: {e}")
        finally:
            await client.disconnect()
            print("Disconnected")

async def main():
    while True:
        print("Scanning for ESP32...")
        devices = await BleakScanner.discover()
        esp32_device = None
        for device in devices:
            if device.name and "ESP32_BLE" in device.name:
                esp32_device = device
                break

        if esp32_device:
            await connect_and_listen(esp32_device)
        else:
            print("ESP32 not found. Retrying...")

        await asyncio.sleep(5)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
