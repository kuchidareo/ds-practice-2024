# Documentation

This folder should contain your documentation, explaining the structure and content of your project. It should also contain your diagrams, explaining the architecture. The recommended writing format is Markdown.

### Here are the rules for fraud detection:
Empty user name
Empty contact number or contact number is a string or contact number is a number less than 7 or more than 15
Card number is string (as in alphanumeric)

### Here are the rules for an invalid transaction
Empty order items and empty user name (I know it overlaps a little with fraud_detection lol)
Card number is less than 10 digits or more than 19
The expiry date has a year that is not between 2024 and 2050
CVV is not 3 or 4 digits

Book suggestions samples randomly


The system uses Token Ring Leader Election to manage order executor replicas. The system demonstrates fault tolerance. If any of the replicas fail, the token seamlessly moves on to the next in line, ensuring uninterrupted operation.
Order queue used a priority Q. The priority is a simple "toy" set up. I decide the priority based on the number of digits in the card. So [essentially len(cardNumber) - 10] + 1 if the order is from Finland. :joy:
The only issue is that replicas are manually created in the docker-compose file, since with the "deploy: replicas" setting, there was no way to get a clear, identifiable ID to communicate with the other replicas.
