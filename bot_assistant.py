from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        for val in value:
            if not len(val) != 10 or not val.isdigit():
                raise ValueError("Invalid phone number format")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            day, month, year = value.split('.')
            datetime(int(year), int(month), int(day))
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:
    def __init__(self, name, phone):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

    def add_birthday(self, birthday):
        if self.birthday is None:
            self.birthday = Birthday(birthday)
        else:
            raise ValueError("Birthday already exists")


class AddressBook(UserDict):
    def add_record(self, name, phone):
        self.data[name] = Record(name, phone)

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday is not None:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                if (birthday_date.date() >= datetime.today().date() and
                        birthday_date.date() <= datetime.today().date() + timedelta(days=7)):
                    upcoming_birthdays.append({"name": record.name.value, "birthday": record.birthday.value})
        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"ValueError: {str(e)}"
        except KeyError as e:
            return f"KeyError: {str(e)}"
        except IndexError as e:
            return f"IndexError: {str(e)}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return inner


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."


@input_error
def show_birthday(args, book):
    name = args
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value
    else:
        return "Birthday not set."


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        for birthday in upcoming_birthdays:
            print(f"Name: {birthday['name']}, Birthday: {birthday['birthday']}")
    else:
        print("No upcoming birthdays.")


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            if len(args) != 2:
                print("Invalid input format. Use 'add name phone'.")
                continue
            book.add_record(args[0], args[1])
            print("Contact added.")

        elif command == "change":
            if len(args) != 3:
                print("Invalid input format. Use 'change name old_phone new_phone'.")
                continue
            record = book.find(args)
            if record:
                record.edit_phone(args, args)
                print("Phone changed.")
            else:
                print("Contact not found.")

        elif command == "phone":
            if len(args) != 1:
                print("Invalid input format. Use 'phone name'.")
                continue
            record = book.find(args)
            if record:
                print(record)
            else:
                print("Contact not found.")

        elif command == "all":
            print(book)

        elif command == "add-birthday":
            if len(args) != 2:
                print("Invalid input format. Use 'add-birthday name birthday'.")
                continue
            print(add_birthday(args, book))

        elif command == "show-birthday":
            if len(args) != 1:
                print("Invalid input format. Use 'show-birthday name'.")
                continue
            print(show_birthday(args, book))

        elif command == "birthdays":
            birthdays(args, book)

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
