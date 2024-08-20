from Disk import Disk
from Storage import Storage
import os

class RAID:
    def __init__(self, storage, num_disks=3, message_size=10):
        self.num_disks = num_disks
        self.message_size = message_size
        self.disks = [Disk(disk_id, storage, self) for disk_id in range(num_disks)]
        self.used_addresses = {}
        print("RAID initialized with", self.num_disks, "disks.")

    def add_flags(self, data):
        return 'D-' + data

    def remove_flags(self, data):
        return data[2:] if data.startswith('D-') else data

    def read(self, address):
        data_blocks = []
        missing_disk_ids = []
        for i in range(self.num_disks):
            disk_id = (address + i) % self.num_disks
            data = self.disks[disk_id].read(address)
            if data == "-":
                print(f"Address {address} is empty.")
            elif data is None:
                missing_disk_ids.append(disk_id)
                print(f"Disk {disk_id} is missing. Recovering...")
                self.recover_disk(disk_id)
                data = self.disks[disk_id].read(address)
                if data is None:
                    print(f"Failed to recover data for address {address} on disk {disk_id}.")
                    continue
                else:
                    print(f"Data successfully recovered for address {address} on disk {disk_id}.")
            if not data.startswith('P-'):
                data_blocks.append(self.remove_flags(data))
        if len(data_blocks) == 0:
            print(f"No usable data found at address {address}.")
        return ''.join(data_blocks), missing_disk_ids

    def write(self, address, data):
        try:
            int(data, 16)
        except ValueError:
            print("Данные должны быть в шестнадцатеричном формате.")
            return

        if len(data) != 10:
            print("Данные должны быть длиной 10 шестнадцатеричных символов.")
            return

        for i in range(self.num_disks):
            try:
                self.disks[i].read(address)
            except FileNotFoundError:
                print(f"Disk {i} is missing. Recovering...")
                self.recover_disk(i)

        mid = (len(data) + 1) // 2
        data_blocks = [self.add_flags(block) for block in [data[:mid], data[mid:]]]
        print("Data blocks:", data_blocks)

        parity_block = 'P-' + self.calculate_parity_block([self.remove_flags(block) for block in data_blocks])
        print("Parity block:", parity_block)

        for i in range(self.num_disks - 1):
            disk_id = (address + i) % self.num_disks
            self.disks[disk_id].write(data_blocks[i], address)
            print("Wrote data block to disk", disk_id)

        parity_disk_id = (address + self.num_disks - 1) % self.num_disks
        self.disks[parity_disk_id].write(parity_block, address)
        print("Wrote parity block to disk", parity_disk_id)

        self.used_addresses[address] = True
        print("Данные успешно записаны.")

    def recover_data(self, data_blocks):
        recovered_data = 0
        for block in data_blocks:
            recovered_data ^= int(block[2:], 16)
        recovered_data = hex(recovered_data)[2:]
        # Дополняем нулями до пяти символов
        recovered_data = recovered_data.zfill(5)
        print("Recovered data:", recovered_data)
        return recovered_data

    def calculate_parity_block(self, data_blocks):
        parity = 0
        for block in data_blocks:
            parity ^= int(block, 16)
        parity_block = hex(parity)[2:]
        print("Calculated parity block:", parity_block)
        return parity_block

    def clear_disk(self, disk_id):
        self.disks[disk_id].storage.clear(disk_id)
        print(f"Disk {disk_id} has been cleared.")

    def recover_disk(self, disk_id):
        filename = self.disks[disk_id].storage._get_filename(disk_id)

        # Создаем новый файл и заполняем его символами "-"
        with open(filename, 'w') as file:
            for _ in range(64):
                file.write("-\n")
        print(f"Disk {disk_id} has been cleared and initialized with 64 empty lines.")

        # Читаем данные с остальных дисков и восстанавливаем их на текущий диск
        for address in range(64):
            data_blocks = [self.disks[i].read(address) for i in range(self.num_disks) if i != disk_id]

            # Если все данные на остальных дисках равны "-", пропускаем этот адрес
            if all(data == "-" for data in data_blocks):
                continue

            # Определяем флаги для текущего адреса
            if (address + 1) % self.num_disks == disk_id:
                # Данные на текущем диске и на следующем
                data_flags = 'DD'
                parity_flag = 'P'
            elif address % self.num_disks == disk_id:
                # Данные на предыдущем диске и блок избыточности на текущем
                data_flags = 'DP'
                parity_flag = 'D'
            else:
                # Блоки данных на двух предыдущих дисках
                data_flags = 'PP'
                parity_flag = 'D'

            # Определяем тип блока на основе флагов
            if 'D' in data_flags:
                # Если есть флаги данных, то восстанавливаемый блок также считается данными
                recovered_data_with_flags = self.add_flags(self.recover_data(data_blocks))
            elif 'P' in data_flags:
                # Если есть флаги блока избыточности, то восстанавливаемый блок также считается блоком избыточности
                recovered_data_with_flags = 'P-' + self.recover_data(data_blocks)

            # Удаляем лишние символы новой строки и пробелы перед записью на диск
            recovered_data_with_flags = recovered_data_with_flags.strip()

            # Записываем восстановленные данные на текущий диск
            self.disks[disk_id].write(recovered_data_with_flags, address)

        print(f"Recovered data written to disk {disk_id}.")











