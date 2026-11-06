
from app.records import load_records, search, count_by, get_by_id


def display_record(record):
    print("\n" + "=" * 50)
    print("ID:", record["id"])
    print("Concept:", record["concept"])
    print("Category:", record["category"])
    print("Definition:", record["plain_definition"])
    print("Example:", record["example"])
    print("Chapter:", record["module_chapter"])
    print("Risk Warning:", record["risk_warning"])
    print("Source:", record["source_url"])
    print("=" * 50)


def main():

    while True:

        print("\n========== FUNFACTS ==========")
        print("1. Display all records")
        print("2. Search by keyword")
        print("3. Count by category")
        print("4. Find record by ID")
        print("0. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":

            all_records = load_records()

            for record in all_records:
                display_record(record)

            print("\nTotal records:", len(all_records))

        elif choice == "2":

            keyword = input("Enter keyword: ")
            results = search(keyword)

            if results:
                for record in results:
                    display_record(record)
                print("Results found:", len(results))
            else:
                print("No matching records found.")

        elif choice == "3":

            print("\n1. Module 3")
            print("2. Module 4")
            print("3. Glossary")

            category_choice = input("Choose category: ").strip()

            categories = {
                "1": "module_3",
                "2": "module_4",
                "3": "glossary"
            }

            if category_choice in categories:
                category = categories[category_choice]
                print("Total", category, "records:", count_by(category))
            else:
                print("Invalid category.")

        elif choice == "4":

            record_id = input("Enter record ID: ").strip().upper()
            record = get_by_id(record_id)

            if record:
                display_record(record)
            else:
                print("Record not found.")

        elif choice == "0":
            print("Thank you for using FundFacts!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
