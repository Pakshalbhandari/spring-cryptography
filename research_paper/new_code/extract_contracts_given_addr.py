import requests

# Replace with your Etherscan API key
api_key = 'YOUR_KEY'

import csv

c = 0
with open('dataset.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # Assuming the address is in the second column (index 1)
        contract_address = row[1]
        print(contract_address)



# # Replace with the Ethereum contract address you want to get the bytecode for

        # Etherscan API URL
        url = f'https://api.etherscan.io/api?module=proxy&action=eth_getCode&address={contract_address}&tag=latest&apikey={api_key}'

        try:
            # Send a GET request to the Etherscan API
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                c += 1 
                data = response.json()

                # Check if the API call was successful
                print(data)
                if "result" in data.keys():
                    # Get the bytecode
                    bytecode = data['result']
                    print(f'Contract Bytecode: {bytecode}')
                    f = open(f"new_contracts/extract_contract_byte_{c}.code","w")
                    f.write(bytecode[2:])
                    f.close()
                    print(c)
                else:
                    print('API call failed. Check your API key and contract address.')
            else:
                print('Request to Etherscan API failed. Please check your network connection or try again later.')
        except Exception as e:
            print(f'An error occurred: {str(e)}')