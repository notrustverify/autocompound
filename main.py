from compound import Compound
import time


if __name__ == '__main__':
    autocompound = Compound()

    balancePast = autocompound.getBalance()
 
    mixnodes = ['APxUbCmGp4K9qDzvwVADJFNu8S3JV1AJBw7q6bS5KN9E','4yRfauFzZnejJhG2FACTVQ7UnYEcFUYw3HzXrmuwLMaR','B63yxdf92RdjwEeUFouxU4x5gRpWXKorT51px8EbpQvJ']

    delegators = 0
    with open("data/blacklist", "r+") as file1:
        blacklist = file1.read().splitlines()

    resultFile = f"data/result_{time.time()}.txt"
    for mixnode in mixnodes:
        delegators += autocompound.compound(mixnode,blacklist,resultFile)

    balanceNow = autocompound.getBalance()
    print(f"")
    print(f"Final balance: {balanceNow}, used {balancePast-balanceNow} NYM, Number of delegators {delegators}")