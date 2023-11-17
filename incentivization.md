Waku is a family of decentralized communication protocols.
The Waku network consists of independent nodes running the corresponding protocols.
Waku needs incentivization (i13n) to ensure proper node behavior in the absence of any centralized coordinator.

In this document, we overview the problem of i13n in decentralized systems.
We classify the possible methods of i13n and give example used in prior successful P2P networks.
We then briefly introduce Waku and outline the unique i13n challenges it presents.

We then go into more detail into one of the Waku's protocols, Store, responsible for archival storage.
We propose an i13n scheme for Store and implement an MVP solution.
We discuss the choices we have made for the MVP version, and what design options may be considered in the future.

# Classification of i13n tools

We can think of incentivization tools as a two-by-two matrix:
- rewards vs punishment;
- monetary vs reputation.

In other words, there are four quadrants:
- monetary reward: the client pays the server;
- monetary punishment: the server makes a deposit and gets slashed if it misbehaves;
- reputation reward: the server's reputation increases if it behaves well;
- reputation punishment: the server's reputation decreases if it behaves badly.

Reputation can only work if there are tangible benefits of having a high reputation.
For example, clients should be more likely to connect to servers with high reputation and disconnect from servers with low reputation.
In the presence of monetary rewards, low-reputation servers miss out on potential revenue or lose their deposit.
Without the monetary aspects, low-reputation nodes can't get as much benefit from the network.
Reputation either assumes a repeated interaction (i.e., local reputation), or some amount of trust (centrally managed rankings).

Monetary motivation should ideally be atomically linked with performance.
If the client pays first, the server cannot deny service,
and if the client pays after the fact, it's impossible to default on this obligation.

In blockchains, the desired behavior of miners or validators can be automatically verified and rewarded with native tokens (or punished by slashing).
Enforcing atomicity in decentralized data-focused networks is challenging:
it is non-trivial to prove that a certain piece of data was sent or received.
Therefore, such cases may warrant a combination of monetary and reputation-based approaches.

# Related work

There have been many example of incentivized decentralized systems.

## Early P2P file-sharing

Early P2P file-sharing networks employed reputation-based approaches and sticky defaults.
For instance, in BitTorrent, a peer by default shares pieces of a file before having received it in whole.
At the same time, the bandwidth that a peer can use depends on how much is has shared previously.
This policy rewards nodes who share by allowing them to download file faster.
While this reward is not monetary, it has proven to be working in practice.

## Blockchains

The key innovation of Bitcoin, inherited and built upon by later blockchains, is native monetary i13.
In Bitcoin, miners create new blocks and are automatically rewarded with newly mined coins.
An invalid block is rejected by other nodes and not rewarded.
There are no intrinsic monetary punishments in Bitcoin, only rewards.
However, mining nodes are required to expend physical resources for block generation.

Proof-of-stake algorithms introduce intrinsic monetary punishments in the blockchain context.
A validator locks up (stakes) native tokens and gets rewarded for validating new blocks and slashed for misbehavior.

## Decentralized storage

Decentralized storage networks, including Codex, Storj, Sia, Filecoin, IPFS, combine the techniques from early P2P file-sharing and blockchain-inspired reward mechanisms to incentivize nodes to store data.

# Waku background

Waku is a family of protocols (see [architecture](https://waku.org/about/architect)) for a modular decentralized censorship-resistant P2P communications network.
The backbone of Waku is the Relay protocol (and its spam-protected version [RLN-Relay](https://rfc.vac.dev/spec/17/)).
Additionally, there are three light (or client-server, or request-response) protocols: Filter, Store, and Lightpush.

There is no strict definition of a full node vs a light node in Waku (see [discussion](https://github.com/waku-org/research/issues/28)).
In this document, we refer to a node that is running Relay and Store (server-side) as a full node or a server, and to a node that is running a client-side of any of the light protocols as a light node or a client.

In light protocols, a client sends a request to a server.
A server (a Relay node) performs some actions and returns a response, in particular:
- [[Filter]]: the server will relay (only) messages that pass a filter to the client;
- [[Store]]: the server responds with messages that had been broadcast within the specified time frame;
- [[Lightpush]]: the server publishes the client's message to the Relay network.

## Waku i13n challenges

As a communication protocol, Waku lacks consensus or a native token.
These properties bring Waku closer to purely reputation-incentivized file-sharing systems.
Our goal nevertheless is to combine monetary and reputation-based incentives.
The rationale is that monetary incentives have demonstrated their robustness in blockchains,
and are well-suited for a network designed to scale well beyond the initial phase when it's mainly maintained by enthusiasts for altruistic reasons.
Currently, Waku only operates under reputation-based rewards and punishments.
While [RLN-Relay](https://rfc.vac.dev/spec/17/) adds monetary punishments for spammers, slashing is yet to be activated.

## Waku Store

In this document, we focus on i13n for Waku Store.

Store is a client-server protocol that currently works as follows:
1. the client sends a `HistoryQuery` to the server;
2. the server sends a `HistoryResponse` to the client.

The response may be split into multiple parts, as specified by pagination parameters in `PagingInfo`.

Let us define a relevant message as a message that has been broadcast via Relay within the time frame and matching the filter criteria that the client specified.
The desired functionality of Store can be described as following:

- the server responds quickly;
- all relevant messages are in the response;
- the response contains only relevant messages.

# Waku Store incentivization MVP

In this section, we aim to define the simplest viable i13n modification to the Store protocol.

We propose to add the following aspects to the protocol:
1. pricing:
	1. cost calculation
	2. price advertisement
	3. price negotiation
2. payment:
	1. payment itself
	2. proof of payment
3. reputation
4. results cross-checking

The MVP version of the protocol has no price advertisement, no price negotiation, and no results cross-checking.
Other elements are present in a minimal version.

## Pricing

For MVP, we assume a constant price per hour of history.
After the client sends a `HistoryQuery` to the server:
1. The server internally calculates the offer price and sends it to the client.
2. If the client agrees, it pays and sends a proof of payment to the server.
3. If the client does not agree, it sends a rejection message to the server.
4. If the server receives a valid payment before a certain timeout, it sends the response to the client.
5. If the server receives a rejection message, or receives no message before a timeout, the server assumes that the client has rejected the offer.

### Future work

- DoS protection: a client can overwhelm a server with requests and not proceed to payment. Countermeasure: ignore requests from the same client if they come too often; generalize a reputation system to servers ranking clients.
- Cost calculation - see https://github.com/waku-org/research/issues/35
- Price advertisement - see https://github.com/waku-org/research/issues/51
- Price negotiation - see https://github.com/waku-org/research/issues/52

## Payment

If the client agrees to the price, it sends a _proof of payment_ to the server.
For the MVP, each request is paid for with a separate transaction.
The transaction hash (`txid`) acts as a proof of payment.

Note that client gives proof of payment before it receives the response.
Other options could be:
1. the client pays after the fact;
2. the client pays partly upfront and partly after the fact;
3. an escrow (a centralized trusted third party, or a semi-trusted entity like a smart contract) ensures atomicity .

Our design considerations are:
- the MVP protocol should be simple;
- servers are more "permanent" entities and are more likely to have long-lived identities;
- it is more important to protect the clients's privacy than the server's privacy.

In light of these criteria, we suggest that the client pays first: this is simpler than splitting the payment, more secure than trusting a third party, and (arguably) more privacy-preserving for the client than the alternative where the client pays after the fact (that would encourage servers to deanonymize clients to prevent fraud).

### Future work

- Add more payment methods - see https://github.com/waku-org/research/issues/58
- Design a subscription model with service credentials - see https://github.com/waku-org/research/issues/59
- Add privacy to service credentials - see https://github.com/waku-org/research/issues/60

## Reputation

We use reputation to discourage the server from taking the payment and not responding.
The client keeps track of the server's reputation:
- all servers start with zero reputation;
- if the server honors the request, it gets +1;
- if the server does not respond before the payment, it gets -1;
- if the server does not respond after the payment and before a timeout, the client will never query it again.

Potential issues:
- An attacker can establish new server identities and continue running away with clients' money. Countermeasures:
	- a client only queries "trusted" servers (which however leads to centralization);
	- when querying a new server, a client first sends a small (i.e. cheap) request as a test.
- The ban mechanism can theoretically be abused. For instance, a competitor may attack the victim server and cause the clients who were awaiting the response to ban that server. Countermeasure: prevent DoS-attacks.
- Servers may also farm reputation by running clients and querying their own server.

### Future work

Design a more comprehensive reputation system:
- local reputation - see https://github.com/waku-org/research/issues/48
- global reputation - see https://github.com/waku-org/research/issues/49

Reputation may also be use to rank clients to prevent DoS attacks when a client overwhelms the server with requests.
While rate limiting stops such attack, the server would need to link requests coming from one client, threatening its privacy.

## Results cross-checking

Cross-checking is absent in MVP but should be considered later.
We can separate it into two questions: the client want to ensure that servers are a) not censoring real messages; b) not injecting fake messages into history.

- Cross-checking the results against censorship - see https://github.com/waku-org/research/issues/57
- Use RLN to limit fake message insertion - see https://github.com/waku-org/research/issues/38

# Evaluation

We should think about what the success metrics for an incentivized protocol are, and how to measure them both in simulated settings, as well as in a live network.

# Longer-term future work

- Analyze privacy issues - see https://github.com/waku-org/research/issues/61
- Analyze decentralized storage protocols and their relevance e.g. as back-end storage for Store servers - see https://github.com/waku-org/research/issues/34
- Analyze the role of message senders, in particular, whether they should pay for sending non-ephemeral messages - see https://github.com/waku-org/research/issues/32
- Generalize incentivization protocol to other Waku light protocols: Lightpush and Filter.