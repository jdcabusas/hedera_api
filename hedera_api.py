from hedera import Client, AccountId, PrivateKey, AccountBalanceQuery

# Initialize client for testnet
client = Client.forTestnet()
client.setOperator(AccountId.fromString("0.0.5036759"), PrivateKey.fromString("0x403e1538d2e1e108c59a923c79dd62c784037c521e5884e4da4f0de2a5e34685"))

# Query the account balance to confirm the setup
try:
    balance = AccountBalanceQuery().setAccountId(AccountId.fromString("0.0.5036759")).execute(client)
    print("Account balance:", balance.hbars.toString())  # Print the balance in HBAR
except Exception as e:
    print("An error occurred:", e)

