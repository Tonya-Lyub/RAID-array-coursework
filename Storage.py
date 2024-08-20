import os

class Storage:
    def __init__(self, num_disks=3, disk_directory="disks"):
        self.num_disks = num_disks
        self.disk_directory = disk_directory

        if not os.path.exists(self.disk_directory):
            os.makedirs(self.disk_directory)

        for disk_id in range(self.num_disks):
            filename = self._get_filename(disk_id)
            with open(filename, 'w') as file:
                for _ in range(64):
                    file.write("-\n")

    def read(self, disk_id, address=None):
        filename = self._get_filename(disk_id)
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
                if address is None:
                    return [line.strip() for line in lines]
                elif address < len(lines):
                    data = lines[address].strip()
                    return data if data != "-" else "-"
                else:
                    print(f"Address {address} is out of range.")
                    return None
        except FileNotFoundError:
            raise FileNotFoundError(f"File {filename} does not exist.")

    def write(self, disk_id, data, address):
        filename = self._get_filename(disk_id)
        try:
            with open(filename, "r") as file:
                lines = file.readlines()
            if address < len(lines):
                lines[address] = data + '\n'
                with open(filename, "w") as file:
                    file.writelines(lines)
            else:
                print(f"Address {address} is out of range.")
        except IOError as e:
            print(f"Ошибка при записи на диск {disk_id}: {e}")

    def clear(self, disk_id):
        filename = self._get_filename(disk_id)
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

    def clear_all(self):
        for filename in os.listdir(self.disk_directory):
            os.remove(os.path.join(self.disk_directory, filename))

    def _get_filename(self, disk_id):
        return os.path.join(self.disk_directory, f"disk{disk_id}")
