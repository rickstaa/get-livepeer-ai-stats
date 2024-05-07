"""Fetches the AI fees from the hosted Subgraph and prints them to the console."""

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

KNOWN_AI_BROADCASTERS = [
    "0x012345dE92B630C065dFc0caBE4eB34f74f7FC85",
    "0x87d4396204035736422c2c6dfce423bba6daa776",
    "0x491F5F5664f11a1e0Ba6902A8cA37C09150bE0DB",
]


def fetch_data_for_broadcaster(url, query, broadcaster):
    # Define the transport
    transport = RequestsHTTPTransport(url=url)

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # The query to fetch the winning ticket events for a specific broadcaster
    broadcaster_query = gql(query.format(broadcaster=broadcaster))

    # Fetch the data from the Subgraph
    result = client.execute(broadcaster_query)

    # Extract the winning ticket events
    winning_ticket_events = result["winningTicketRedeemedEvents"]

    return winning_ticket_events


# The URL of the hosted Subgraph
url = "https://dca-graph-node.livepeer.fun/subgraphs/name/livepeer"

# The query to fetch the winning ticket events for a specific broadcaster
WINNING_TICKET_QUERY = """
  query {{
    winningTicketRedeemedEvents(
      orderBy: timestamp
      orderDirection: desc
      where: {{sender: "{broadcaster}"}}
    ) {{
      id
      recipient {{
        id
        serviceURI
      }}
      winProb
      faceValueUSD
      faceValue
      timestamp
      sender {{
        id
        deposit
      }}
    }}
  }}
"""

# Fetch data for each broadcaster.
total_tickets = 0
total_face_value = 0
total_face_value_USD = 0
broadcasters = [broadcaster.lower() for broadcaster in KNOWN_AI_BROADCASTERS]
for broadcaster in broadcasters:
    data = fetch_data_for_broadcaster(url, WINNING_TICKET_QUERY, broadcaster)
    print(f"Data for broadcaster {broadcaster}: {data}")
    total_tickets += len(data)
    total_face_value += sum([float(event["faceValue"]) for event in data])
    total_face_value_USD += sum([float(event["faceValueUSD"]) for event in data])

# Print the total number of tickets and total face value in USD.
print(f"Total tickets: {total_tickets}")
print(f"Total face value: {total_face_value}")
print(f"Total face value in USD: {total_face_value_USD}")
