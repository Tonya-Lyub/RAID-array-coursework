class Disk:
    def __init__(self, disk_id, storage, raid):
        self.disk_id = disk_id
        self.storage = storage
        self.raid = raid

    def read(self, address=None):
        try:
            return self.storage.read(self.disk_id, address)
        except FileNotFoundError:
            print(f"File disks\\disk{self.disk_id} does not exist, starting recovery...")
            self.raid.recover_disk(self.disk_id)
            return self.storage.read(self.disk_id, address)

    def write(self, data, address):
        self.storage.write(self.disk_id, data, address)
