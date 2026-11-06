while True:
    print("FundFacts Menu")
    print("1. About FundFacts")
    print("2. Sample Questions")
    print("3. Risk Check")
    print("0. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        print("FundFacts teaches mutual fund basics.")

    elif choice == "2":
        print("1. What is SIP?")
        print("2. What is NAV?")
        print("3. What is KYC?")
        print("4. What is Riskometer?")

    elif choice == "3":
        risk = input("Enter risk (Low/Moderate/High): ").lower()

        if risk == "low":
            print("Low risk selected.")

        elif risk == "moderate":
            print("Moderate risk selected.")

        elif risk == "high":
            print("High risk selected.")

        else:
            print("Invalid risk!")

    elif choice == "0":
        print("Thank you!")
        break

    else:
        print("Invalid choice!")