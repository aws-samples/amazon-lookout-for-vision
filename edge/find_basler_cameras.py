from pypylon import pylon


tl_factory = pylon.TlFactory.GetInstance()
devices = tl_factory.EnumerateDevices()
for device in devices:
    print(device.GetFriendlyName())

