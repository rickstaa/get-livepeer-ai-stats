"""Fetches the number of AI orchestrators on the network by sending RPC requests to the
AI ServiceRegistry contract.
"""

import json
import os
from web3 import Web3

INFURA_API_KEY = os.getenv("INFURA_API_KEY")
if not INFURA_API_KEY:
    raise ValueError("Please set the INFURA_API_KEY environment variable")
RCP_URI = f"https://arbitrum-mainnet.infura.io/v3/{INFURA_API_KEY}"

BONDING_MANAGER_ADDRESS = "0x35Bcf3c30594191d53231E4FF333E8A770453e40"
with open("abis/BondingManager.json") as f:
    BONDING_MANAGER_ABI = json.load(f)["result"]

AI_SERVICE_REGISTRY_ADDRESS = "0x04C0b249740175999E5BF5c9ac1dA92431EF34C5"
with open("abis/AIServiceRegistry.json") as f:
    AI_SERVICE_REGISTRY_ABI = json.loads(json.load(f)["result"])

NULL_ADDRESS = Web3.to_checksum_address('0x' + '0' * 40)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_transcoder_pool(bonding_manager):
    """Get the list of transcoders in the pool.

    Args:
        bonding_manager: The BondingManager contract instance.

    Returns:
        A list of transcoder addresses.
    """
    try:
        current_transcoder_addr = bonding_manager.functions.getFirstTranscoderInPool().call()
        transcoders = [current_transcoder_addr]
        while True:
            next_transcoder_addr = bonding_manager.functions.getNextTranscoderInPool(
                current_transcoder_addr
            ).call()
            if next_transcoder_addr == NULL_ADDRESS:
                break
            transcoders.append(next_transcoder_addr)
            current_transcoder_addr = next_transcoder_addr
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return transcoders


def get_ai_orchestrators_uris(service_registry, orchestrators):
    """Get the list of AI orchestrators URIs.

    Args:
        service_registry: The AIServiceRegistry contract instance.
        orchestrators: The list of orchestrator addresses.

    Returns:
        A dictionary of orchestrator addresses and their corresponding AI orchestrator URIs.
    """
    ai_orchestrators_uris = {}
    for orchestrator in orchestrators:
        try:
            ai_orchestrator_uri = service_registry.functions.getServiceURI(orchestrator).call()
            if ai_orchestrator_uri:
                ai_orchestrators_uris[orchestrator] = ai_orchestrator_uri
                print(f"Orchestrator: {orchestrator}, AI Orchestrator URI: {ai_orchestrator_uri}")
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    return ai_orchestrators_uris


if __name__ == "__main__":
    # Connect to the RPC endpoint and instantiate the contracts.
    w3 = Web3(Web3.HTTPProvider(RCP_URI))
    bonding_manager = w3.eth.contract(
        address=Web3.to_checksum_address(BONDING_MANAGER_ADDRESS),
        abi=BONDING_MANAGER_ABI,
    )
    service_registry = w3.eth.contract(
        address=Web3.to_checksum_address(AI_SERVICE_REGISTRY_ADDRESS),
        abi=AI_SERVICE_REGISTRY_ABI,
    )

    print("Fetching mainnet Orchestrators...")
    orchestrators = get_transcoder_pool(bonding_manager)

    print(f"Store the mainnet Orchestrators in {OUTPUT_DIR}/main_orchestrators.txt")
    with open(os.path.join(OUTPUT_DIR, "main_orchestrators.txt"), "w") as f:
        for orchestrator in orchestrators:
            f.write(f"{orchestrator}\n")

    print("Fetching AI Orchestrators...")
    ai_orchestrators_uris = get_ai_orchestrators_uris(service_registry, orchestrators)

    print(f"Store the AI Orchestrators in {OUTPUT_DIR}/ai_orchestrators.txt")
    with open(os.path.join(OUTPUT_DIR, "ai_orchestrators.txt"), "w") as f:
        for orchestrator, ai_orchestrator in ai_orchestrators_uris.items():
            f.write(f"{orchestrator} {ai_orchestrator}\n")

    print(f"Total number of AI Orchestrators: {len(ai_orchestrators_uris)}")
