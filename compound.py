import requests
import subprocess
import json
from tqdm import tqdm

API_ENDPOINT = "https://explorer.nymtech.net/api/v1/mix-node"
MIN_REWARDS_UNYM = 2*10**6


class Compound:

    def getBalance(self):
        cmdBalance = "./nym-cli --config-env-file .env account balance"
        balanceQry = subprocess.run(cmdBalance.split(
        ), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        try:
            balance = float(balanceQry.stdout.split(" ")[0])
            return balance
        except IndexError as e:
            print(f"{balanceQry.stderr}, code {balanceQry.returncode}")
            print(f"error with balance, {e}")
            exit()

    def compound(self, mixnode, blacklist, resultFile):
        num_delegators = set()
        try:
            balance = self.getBalance()
            if balance <= 3:
                print(f"not enough balance {balance} NYM for {mixnode}")
            else:
                print(f"Balance is {balance}. Good to go for {mixnode}")


            s = requests.Session()

            response = s.get(f"{API_ENDPOINT}/{mixnode}/delegations")

            if response.ok:

                cmdCompound = "./nym-cli --config-env-file .env cosmwasm execute n14hj2tavq8fpesdwxxcu44rty3hh90vhujrvcmstl4zr3txmfvw9sjyvg3g ".split()

                for data in tqdm(response.json()):
                    if data['owner']  not in blacklist:

                        try:
                            rewards = s.get(f"https://mixnet.api.explorers.guru/api/accounts/{data['owner']}/balance",timeout=100)

                            waiting=float(rewards.json()['claimableRewards']['amount'])
                            if rewards.ok and waiting <= MIN_REWARDS_UNYM:
                                print(f"no need to compound for {data['owner']}, waiting rewards {waiting/10**6} NYM")
                                continue
                        except (requests.RequestException, KeyError) as e:
                            print(f"error {e} for retrieve balance for {data['owner']}. Continue anyways")

                        
                        num_delegators.add(data['owner'])
                        cmdCompound = "./nym-cli --config-env-file .env cosmwasm execute n14hj2tavq8fpesdwxxcu44rty3hh90vhujrvcmstl4zr3txmfvw9sjyvg3g ".split()

                        compound_reward = {
                            "compound_reward": {
                                "delegator": data['owner'], "mix_identity": mixnode
                            }
                        }

                        cmdCompound.append(json.dumps(compound_reward))

                        output = ""
                        error = ""

                        compoundQry = subprocess.run(
                            cmdCompound, check=False
                            ,capture_output=True, text=True)

                        output = compoundQry.stdout
                        error = compoundQry.stderr
                        

                        res = f"Autocompound {data['owner']} done, code {compoundQry.returncode}\nError: {error} Output: {output}\n"
                        
                        with open(resultFile, "a") as file1:
                            # Writing data to a file
                            file1.write(f"{res}\n")
                            # print(res)
                        

        except requests.RequestException as e:
            print(f"Error on mixnode {mixnode}")
            print(traceback.format_exc())

        return len(num_delegators)
