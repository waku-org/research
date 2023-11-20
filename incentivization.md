Waku is a family of decentralized communication protocols.
The Waku Network (TWN) consists of independent nodes running Waku protocols.
TWN needs incentivization (shortened to i13n) to ensure proper node behavior.

The goal of this document is to outline and contextualize our approach to TWN i13n.
After providing an overview of Waku and relevant prior work,
we focus on Waku Store - a client-server protocol for quer
We then introduce a minimal viable addition to Store to enable i13n, and list research directions for future work.

# Incentivization in decentralized networks
## Incentivization tools

We can think of incentivization tools as a two-by-two matrix:
- rewards vs punishment;
- monetary vs reputation.

In other words, there are four quadrants:
- monetary reward: the node gets rewarded;
- monetary punishment: the nodes deposits funds that are taken away (slashed) if it misbehaves;
- reputation reward: the node's reputation increases if it behaves well;
- reputation punishment: the node's reputation decreases if it behaves badly.

Reputation only works if high reputation brings tangible benefits.
For example, if nodes chose neighbors based on reputation, low-reputation nodes may miss out on potential revenue.
Reputation scores may be local (a node assigns scores to its neighbors) or global (each node gets a uniform score).
Global reputation in its simplest implementation involves a trusted third party,
although decentralized approaches are also possible.

## Prior work

We may split incentivized decentralized networks into early file-sharing, blockchains, and decentralized storage.

### Early P2P file-sharing

Early P2P file-sharing networks employed reputation-based approaches and sticky defaults.
For instance, in BitTorrent, a peer by default shares pieces of a file before having received it in whole.
At the same time, the bandwidth that a peer can use depends on how much is has shared previously.
This policy rewards nodes who share by allowing them to download file faster.
While this reward is not monetary, it has proven to be working in practice.

### Blockchains

Bitcoin has introduced native monetary i13n in a P2P network with proof-of-work (PoW).
PoW miners are automatically rewarded with newly mined coins for generating blocks.
There are no intrinsic monetary punishments in Bitcoin.
However, miners must expend physical resources before claiming the reward.
Proof-of-stake (PoS) algorithms introduce intrinsic monetary punishments.
PoS validators lock up (stake) native tokens to get rewarded for validating blocks or slashed for misbehavior.

### Decentralized storage

Post-Bitcoin decentralized storage networks include Codex, Storj, Sia, Filecoin, IPFS.
Their i13n methods combine techniques from early P2P file-sharing with blockchain-inspired reward mechanisms.

# Waku background

Waku is a family of protocols (see [architecture](https://waku.org/about/architect)) for a modular decentralized censorship-resistant P2P communications network.
The backbone of Waku is the Relay protocol (and its spam-protected version [RLN-Relay](https://rfc.vac.dev/spec/17/)).
Additionally, there are light protocols: Filter, Store, and Lightpush.
Light protocols are also referred to as client-server protocols and request-response protocols.

A server is a node running Relay and Store (server-side).
A client is a node running a client-side of any of the light protocols as a light node or a client.
A server may sometimes be referred to as a full node, and a client as a light node.
There is no strict definition of a full node vs a light node in Waku (see [discussion](https://github.com/waku-org/research/issues/28)).

In light protocols, a client sends a request to a server, and a server performs some actions and returns a response:
- [[Filter]]: the server will relay (only) messages that pass a filter to the client;
- [[Store]]: the server responds with messages broadcast earlier within the specified time frame;
- [[Lightpush]]: the server publishes the client's message to the Relay network.

## Waku i13n challenges

Waku lacks consensus or a native token, which brings it closer to reputation-incentivized file-sharing systems.
Indeed, currently Waku only operates under reputation-based rewards and punishments.
While [RLN-Relay](https://rfc.vac.dev/spec/17/) adds monetary punishments for spammers, slashing is yet to be activated.

Monetary rewards and punishments should ideally be atomically linked with performance.
A benefit of blockchains in this respect is that the desired behavior of miners or validators can be verified on-chain.
Enforcing atomicity in decentralized data-focused networks is more challenging:
it is non-trivial to prove that a certain piece of data was sent or received.

Our goal is to combine monetary and reputation-based incentives for Waku.
Monetary incentives have demonstrated their robustness in blockchains.
We think they are necessary to scale the network beyond the initial phase when it's maintained altruistically.

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

In this document, we define the simplest viable i13n modification to the Store protocol (MVP).
The MVP protocol has no price advertisement, no price negotiation, and no results cross-checking.
Other elements are present in a minimal version.
In further subsections, we list the potential direction for future work towards a fully-fledged i13n protocol.

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
For the MVP, each request is paid for with a separate blockchain transaction.
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
We can separate it into two tasks for the client: ensure that servers are a) not censoring real messages; b) not injecting fake messages into history.

- Cross-checking the results against censorship - see https://github.com/waku-org/research/issues/57
- Use RLN to limit fake message insertion - see https://github.com/waku-org/research/issues/38

# Evaluation

We should think about what the success metrics for an incentivized protocol are, and how to measure them both in simulated settings, as well as in a live network.

# Longer-term future work

- Analyze privacy issues - see https://github.com/waku-org/research/issues/61
- Analyze decentralized storage protocols and their relevance e.g. as back-end storage for Store servers - see https://github.com/waku-org/research/issues/34
- Analyze the role of message senders, in particular, whether they should pay for sending non-ephemeral messages - see https://github.com/waku-org/research/issues/32
- Generalize incentivization protocol to other Waku light protocols: Lightpush and Filter.