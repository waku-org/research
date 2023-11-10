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
Similar techniques may be later applied to other Waku light protocols.

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
1. price offer;
2. proof of payment;
3. reputation accounting.

### Price offer

After the client sends a `HistoryQuery` to the server:
1. The server internally calculates the offer price  and sends it to the client.
2. If the client agrees, it pays and sends a proof of payment to the server.
3. If the client does not agree, it sends a rejection message to the server.
4. If the server receives a valid proof of payment before a certain timeout, it sends the response to the client.
5. If the server receives a rejection message, or receives no message before a timeout, the server assumes that the client has rejected the offer.

Potential issues:
- The client overwhelms a server with requests but doesn't proceed with payment. Countermeasure: ignore requests from the same client if they come too often.
- The server and the client have no means to negotiate the price - see a later section on price negotiation.

### Proof of payment

If the client agrees to the price, it sends a _proof of payment_ to the server.
The nature of such proof depends on the means of payment.
Assuming the payment takes place on a blockchain, it could simply be a transaction hash (`txid`).

It's unclear whether we need to ensure that a given `txid` is linked to a particular request.
Including request ID into the payment (a-la "memo field") threatens privacy.
Not including it could lead to the server's confusion regarding which received payments correspond to which requests.

#### Who pays first?

We have to make a design decision: who pays first?
Our options are:
1. the client pays first;
2. the client pays after the fac;
3. the client pays partly upfront and partly after the fact;
4. a third party (escrow) ensures atomicity (it may be a centralized trusted third party or a semi-trusted entity like a smart contract).

Our design considerations are:
- the MVP protocol should be simple;
- servers are more "permanent" entities and are more likely to have a long-lived identities;
- it is more important to protect the clients's privacy than the server's privacy: a client knows what server it queries, while the server ideally shouldn't know who the client is.

With that in mind, we suggest that the client pays first.
It is simpler than splitting the payment, which would involve a) two payments, and b) negotiating the split.
It is also simpler than a trusted third party (the centralized flavor of which we want to avoid).

Comparing to "client pays after the fact", we observe that there is a balance between risk and privacy.
If the server "pays first", it assumes risk, which should be decreased or paid for.
Decreasing the risk means that the client keeps track of the clients' reputation, which endangers privacy.
Paying for the risk means higher prices (well-behaved clients pay for free-riders).

We propose that the client assumes the risk and pays for it because:
- the server is more likely to be professionalized, so dropping paid requests would sabotage its business;
- the client pays for their privacy by assuming risk, which is acceptable (risk is "anonymous", reputation is not).

### Reputation accounting

We use reputation to discourage the server from taking the payment and not responding.
The client keeps track of the server's reputation:
- all servers start with zero reputation;
- if the server honors the request, it gets +1;
- if the server does not respond to the initial request, it gets -1;
- if the server takes the money and does not respond before a timeout, the client will never query it again.

Potential issues:
- An attacker can establish new server identities and continue running away with clients' money. Countermeasures:
	- a client only queries "trusted" servers (which however leads to centralization);
	- when querying a new server, a client first sends a small (i.e. cheap) request as a test.
- The ban mechanism can theoretically be abused. For instance, a competitor may attack the victim server and cause the clients who were awaiting the response to ban that server. Countermeasure: prevent DoS-attacks.

# Payment methods

The MVP protocol is agnostic to payment methods.
A payment method should generally have the following properties:
- wide distribution;
- good liquidity;
- low latency;
- good privacy;
- high security.

Let's list all decentralized payment options:
- ETH;
- a token on Ethereum (ERC20);
- a token on another EVM-based blockchain or a rollup;
- a token on a non-EVM blockchain (such as BTC / Lightning).

Note also that there may be different market models that may motivate the choice of the payment method.
One model assumes that each client pays for its own requests.
Another model includes (centralized?) entities (i.e., developers of Waku-based apps) that pay for their users in bulk.

We also note that:
- eventually the protocol may support multiple payment methods;
- however, the MVP version should be simple, which likely means supporting just one payment method;
- if the initially supported payment method is an ERC-20 token, it should be easy to add other ERC-20 tokens later, including a potential WAKU token.

# Evaluation

We should think about what the success metrics for an incentivized protocol are, and how to measure them both in simulated settings, as well as in a live network.

# Future work

Let us now outline some of the open questions beyond MVP.
## Price discovery

To offer a reasonable price, a server should understand its costs.
The costs of a Store server are storage, bandwidth, and computation.
A Store server does two things: it stores messages, and serves messages to clients.

The cost of storing messages is composed of:
- storage:
	- storage costs of all older messages: proportional to cumulative (message size x time stored);
	- the cost for I/O operations for storing new messages (roughly constant per unit time, though may fluctuate due to caching, disk fragmentation, etc.);
- bandwidth (download) for receiving new messages;
- computational costs.

The cost of serving messages to clients, per unit time, is composed of:
- bandwidth
	- upload: proportional to (number of clients) x (length of time frame requested) x (message size);
	- download: proportional to the number of requests;
- computational cost of handling requests.

Storage is likely the dominating cost.
Storage costs is proportional to the amount of information stored and the time it is stored for.
A cumulative cost of storing a single message grows linearly with time.
The number of messages in a response may be approximated by the length of the time frame requested.

Computation: the server spends computing cycles while handling requests.
This costs likely depends not only on the computation itself, but also at the database structure.
For example, retrieving old or rarely requested messages from the local database may be more expensive than fresh or popular ones due to caching.

More formal calculations should be done, under certain assumptions about message flow (i.e., that it is constant).

## Price negotiation

If the server offers the price that is too high for the client, the client has no means to make a counter-offer.
This results in wasted bandwidth on requests that don't result in responses.
We could introduce a price negotiation step in the protocol, where the client and the server would exchange messages naming their acceptable prices until they agree of one of them decides to stop the negotiation.
We should make sure that price negotiation does not become a DoS vector (i.e., a client initiates a lengthy negotiation but ultimately rejects, wasting the server's resources).

## Results cross-checking

> Never go to sea with two chronometers; take one or three.

The client wants to receive all relevant messages and only them.
Without consensus, it's impossible to check if a message is relevant.
In non security-critical settings, a client may accept the risk that some messages may be missing.
For more certainty, the client may query 3 independent servers and compare the results.
Messages returned by 3/3 or 2/3 are considered relevant.

The servers' reputation may then be adjusted, but it's not completely obvious how.
Let A, B, C be the three servers.
Imagine there is a message that only A's response contains.
From the client's standpoint, this message is not relevant.

How should A's reputation be adjusted?
Should A be punished for inserting a fake message into history?
Or should A be rewarded for providing a "rare" message that B and C have either missed or are intentionally censoring?

## Preventing DoS attacks

The client can overwhelm the server in at least two ways:
- sending many requests;
- sending a request that covers a very long time frame.

The former can be prevented with rate limiting: the server would disconnect from such clients.
The latter can be mitigated economically, if the price depends on the length of the requested time frame.

## Heuristics of relevance

In the absence of consensus, we can't prove whether a message has indeed been broadcast in the past.
Instead, we use RLN proofs as a proxy metric.
RLN (rate limiting nullifiers) is a method of spam prevention in Relay ([RLN-Relay](https://rfc.vac.dev/spec/17/)).
The message sender generates a proof of enrollment in a membership set.
Multiple proofs generated and revealed within one epoch lead to punishment.
A valid RLN proof signifies that the message has been generated by a node with an active membership during a particular epoch.
Note that a malicious node with a valid membership can generate messages but not broadcast them.
Such messages would not be known to other nodes, but they would satisfy the RLN-based heuristic.
We may later look into other ways for the client to check message relevance.

## Privacy considerations

Light protocols, in general, have weaker privacy properties than P2P protocols.
In a client-server exchange, a client wants to selectively interact with the network.
By doing so, it often reveals what it is interested in (e.g., subscribes to particular topics).

A malicious Store server can spy on a client in the following ways:
- track the topics the client is interested in;
- analyze the periods of history interesting for the client;
- analyze the timing of requests;
- link requests made by the same client.

Citing the [Store specification](https://rfc.vac.dev/spec/13/):
> The main security consideration ... is that a querying node have to reveal their content filters of interest to the queried node, hence potentially compromising their privacy.

### Service credentials

Service credentials break the link between paying for the service and the service itself.
Such scheme may be explored in the context of payment methods for higher user privacy.

In a credential-based scheme:
1. the client deposits funds into an on-chain pool;
2. the client generates a credential that proves the transfer in zero-knowledge;
3. the client sends the credential to the server;
4. the server uses the credential to pull funds from the pool.

Further reading: [one](https://forum.vac.dev/t/vac-sustainability-and-business-workshop/116), [two](https://github.com/vacp2p/research/issues/99), [three](https://github.com/vacp2p/research/issues/135).

## Relation to long-term storage solutions

Decentralized file storage networks, such as Codex, could (and perhaps should) be the backend for Store servers.
Alternatives to Codex include IPFS, Filecoin, Sia, and Storj.
We should explore this landscape and understand its relevance for Store i13n.

## Should message senders pay?

To ensure protocol sustainability, we should analyze its game theoretic properties.
Note that there are in fact more than two party to the Store protocol:
- the server;
- the client;
- the sender of the message.

In particular, it is the _sender_ who imposes major costs on the server: the more messages the sender (or, indeed, multiple senders) broadcast, the higher are the Store server's storage costs.
However, it is the Store client who pays for fetching messages.
Is it fair / sustainable that the client pays for costs that the sender causes?
Would it be desired or possible to make the sender pay as well (see [issue](https://github.com/waku-org/research/issues/32))?

## Generalization for other Waku protocols

Think about how to generalize Store i13n to other Waku light protocols: Lightpush and Filter.
