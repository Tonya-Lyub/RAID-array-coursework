from RAID import RAID
from Storage import Storage


def main():
    storage = Storage()
    raid = RAID(storage)
    while True:
        print("\nМеню операций:")
        print("1. Чтение данных")
        print("2. Запись данных")
        print("3. Восстановление данных при выходе из строя одного диска")
        print("4. Очистка данных с диска")
        print("5. Выход")

        choice = input("Выберите операцию (1/2/3/4/5): ")

        if choice == "1":
            try:
                address = int(input("Введите адрес для чтения данных: "))
                if not 0 <= address <= 63:
                    print("Адрес должен быть в диапазоне от 0 до 63.")
                    continue
                data, _ = raid.read(address)
                print(f"Данные по адресу {address}: {data}")
            except ValueError:
                print("Некорректный ввод. Попробуйте снова.")
        elif choice == "2":
            try:
                address = int(input("Введите адрес для записи данных: "))
                if not 0 <= address <= 63:
                    print("Адрес должен быть в диапазоне от 0 до 63.")
                    continue
                data = input("Введите данные для записи (10 символов в шестнадцатеричном формате): ")
                raid.write(address, data)
            except ValueError:
                print("Некорректный ввод. Попробуйте снова.")
        elif choice == "3":
            try:
                disk_id = int(input("Введите номер диска для восстановления: "))
                raid.recover_disk(disk_id)
                print("Данные успешно восстановлены.")
            except ValueError:
                print("Некорректный ввод. Попробуйте снова.")
        elif choice == "4":
            try:
                disk_id = int(input("Введите номер диска для очистки данных: "))
                raid.clear_disk(disk_id)
                print(f"Данные на диске {disk_id} успешно удалены.")
            except ValueError:
                print("Некорректный ввод. Попробуйте снова.")
        elif choice == "5":
            print("Выход из программы.")
            break
        else:
            print("Некорректный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
