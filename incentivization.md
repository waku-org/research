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
- monetary punishment: the server makes a deposit in advance and gets slashed in case of misbehavior;
- reputation reward: the server's reputation increases if it behaves well;
- reputation punishment: the server's reputation decreases if it behaves badly.

Reputation can only work if there are tangible benefits of having a high reputation and drawbacks of having a low reputation.
For example:
- clients are more likely to connect to servers with high reputation;
- clients disconnect from servers with low reputation.

In the presence of monetary rewards, low-reputation servers miss out on potential revenue or lose their deposit.
Without the monetary aspects, low-reputation nodes can't get as much benefit from the network.
Reputation either assumes a repeated interaction (i.e., local reputation), or some amount of trust (centrally managed rankings).

Ideally, monetary motivation should be atomically linked with performance.
A node should be rewarded if and only if it performed the desired action.
Analogously, it should be punished if and only it it misbehaved.
In other words, if the client pays first, the server cannot deny service,
and if the client pays after the fact, it's impossible to default on the obligation.

In blockchain networks, the desired behavior of miners or validators can be automatically verified and rewarded with native tokens (or punished by slashing).
Enforcing atomicity in decentralized data-focused networks can be challenging:
it is non-trivial to prove that a certain piece of data was sent or received.
Therefore, such cases may warrant a combination of monetary and reputation-based approaches.

# Related work

There have been many example of incentivized decentralized systems.

## Early P2P file-sharing

Early P2P file-sharing networks employed reputation-based approaches and sticky defaults.
For instance, in BitTorrent, a peer by default shares pieces of a file before having received it in whole.
At the same time, the bandwidth that a peer can use depends on how much is has shared previously.
This policy rewards nodes who share by allowing them to download file faster.
While this reward is not monetary, it has proven to be sufficient in practice.

## Blockchains

The key innovation of Bitcoin, inherited and built upon by later blockchain networks, is the introduction of native monetary i13 mechanism.
In the case of Bitcoin, miners create new blocks and are automatically rewarded with newly mined coins, as prescribed by the protocol.
An invalid block will be rejected by other nodes and not rewarded, which incentivizes good behavior.
There are no intrinsic monetary punishments in Bitcoin, only rewards.
However, mining nodes are required to expend physical resources for block generation.

Proof-of-stake consensus algorithms introduced intrinsic monetary punishments in the blockchain context.
A validator locks up (stakes) native tokens and gets rewarded for validating new blocks.
In case of misbehavior, the deposit is automatically taken away (i.e., the bad actor is slashed).

## Decentralized storage

Multiple decentralized storage networks have appeared in recent years, including Codex, Storj, Sia, Filecoin, IPFS.
They combine the techniques from early P2P file-sharing and blockchain-inspired reward mechanisms.

# Waku 

Waku is a family of protocols (see [architecture](https://waku.org/about/architect)) for a modular decentralized censorship-resistant P2P communications network.
The backbone of Waku is the Relay protocol ([RLN-Relay](https://rfc.vac.dev/spec/17/) is an spam-protected version of the protocol).
Additionally, there are three light (client-server, request-response) protocols: Filter, Store, and Lightpush.

There is no strict definition of a full node vs a light node in Waku (see https://github.com/waku-org/research/issues/28).
In this document, we may refer to a node that is running Relay and Store (server-side) as a full node, and to a node that is running a client-side of any of the light protocols as a light node.

In light protocols, a client sends a request to a server.
A server (a Relay node) performs some actions and returns a response, in particular:
- [[Filter]]: the server will relay (only) messages that pass a filter to the client;
- [[Store]]: the server responds with messages broadcast within the specified time frame;
- [[Lightpush]]: the server publishes the client's message to the Relay network.

## Waku i13n challenges

As a communication protocol, Waku lacks consensus or a native token.
These properties bring Waku closer to purely reputation-incentivized file-sharing systems.
Our goal nevertheless is to combine monetary and reputation-based incentives in Waku.
The rationale for that is that monetary incentives have demonstrated their robustness in blockchain networks,
and are well-suited for a network designed to scale well beyond the initial phase when it's mainly maintained by enthusiasts for altruistic reasons.

In our i13n framework, currently Waku only operates under reputation-based rewards and punishments.
While [RLN-Relay](https://rfc.vac.dev/spec/17/) adds monetary punishments for spammers, slashing is yet to be activated.


# Waku Store

In this section, we design a monetary-based i13n scheme for Waku Store.
Similar techniques may be later applied to other protocols.

Store is a client-server protocol.
A client asks the node to respond with relevant messages previously relayed through the Relay protocol.
A relevant message is a message that has been broadcast via Relay within the specified time frame.
The response may be split into multiple parts, as specified by pagination parameters.

Let's say, a client issues a request to the server.
We want the following to happen:

- the server responds quickly;
- all the messages in the response are relevant;
- the response contains only relevant messages.

From a security standpoint, each Store node should enforce limits on requests as to not be DoS-ed.

As Waku doesn't intent to establish consensus over past messages,
we can only rely on heuristics to determine whether a message had been relayed earlier.
To decrease the chance of missing some messages, a client may query multiple servers and combine their replies (union of all messages; messages reported by some majority of servers, etc).

# Store i13n MVP

We propose Store-i13n-MVP - the simplest version of i13n in Store.

## Current protocol

As currently defined, the Store protocol works as follows:
1. the client sends a `HistoryQuery` to the server;
2. the server sends a `HistoryResponse` to the client.

A response may come in multiple parts (pagination).
Pagination parameters are defined in `PagingInfo` message inside both the `HistoryQuery` and a ``HistoryResponse``.
Let us ignore the pagination considerations for now (assume it just works).

## Proposed modification

We proposes modification consists of three parts:
1. price negotiation;
2. reputation accounting;
3. results cross-checking.

### Price negotiation

Upon receiving a `HistoryQuery`, the server does the following:
1. Internally calculate the price it wants to charge.
2. Send a message to the client: "I can serve your request for N tokens".
3. If the client agrees, it pays and sends a proof of payment to the server.
4. The server sends the response.

Price discovery to be discussed in a later section.
In particular, we will reason about which message properties (age, size, etc) should contribute to the price.

Potential issues:
- A malicious client overwhelms a server with requests and doesn't follow through. A countermeasure: ignore requests from the same client if they come too often.
- (other attacks?)

### Proof of payment

If the client agrees to the price, it sends a _proof of payment_ to the server.
The nature of such proof depends on the means of payment.
Assuming the payment takes place on a blockchain, it could simply be a transaction hash.

It's unclear if we need to ensure that a particular txid is linked to a particular request.
Including request ID into the payment (a-la "memo field") threatens privacy.
Not including it looks fine though, assuming the server keeps track which transactions it had received correspond to which requests (and responses).

TODO: explore the idea of service credentials:
- [https://forum.vac.dev/t/vac-sustainability-and-business-workshop/116](https://forum.vac.dev/t/vac-sustainability-and-business-workshop/116 "https://forum.vac.dev/t/vac-sustainability-and-business-workshop/116")
- [https://github.com/vacp2p/research/issues/99](https://github.com/vacp2p/research/issues/99 "https://github.com/vacp2p/research/issues/99") 
- [https://github.com/vacp2p/research/issues/135](https://github.com/vacp2p/research/issues/135 "https://github.com/vacp2p/research/issues/135")

#### Who pays first?

We have to make a design decision: who pays first?
Our options are:
1. the client pays first and trust the server to deliver;
2. the client pays after the fact: the server trusts the client;
3. the client pays partly upfront and partly after the fact;
4. there is a third party (escrow) that ensures atomicity (a trusted third party or a semi-trusted, semi-automated entity like a smart contract).

Here are our design considerations:
- the MVP protocol should be simple;
- servers are considered to be a more "permanent" entities, that are more likely to have a long-lived ID;
- it is more important to protect the clients's privacy than the server's privacy: a client knows what server it queries in any case, while ideally the server shouldn't know who the client is. (This isn't entirely rigorous, think about it.)

With that in mind, we suggest the scheme where the client pays first.
It is simpler than splitting the payment, which would involve a) two payments, and b) negotiating the split.
It is also simpler than a trusted third party (the centralized flavor of which we want to avoid anyway).
Comparing to "client pays after the fact", we observe that there is a balance between risk and privacy.
If the server "pays first", it assumes risk.
This risk should be decreased or paid for.
Decreasing the risk means keeping track of the clients' reputation from the server's standpoint, which may endanger clients' privacy.
Paying for the risk means increasing prices (i.e., well-behaved clients in aggregate pay for free-riders).
We suggest that the preferable design is the opposite: the client assumes the risk.
Why this is better:
- it's more likely that the server is professionalized: serving data is its business which it wouldn't want to sabotage;
- the client keeps their privacy, essentially paying for privacy with taking on more risk - this is OK, as risk is "anonymous", and reputation is not.

### Reputation accounting

Our protocol assumes that the client trusts the server.
In particular, the client pays first, and then hopes that the server sends back the response.
A server may technically take the money and do nothing.
To discourage this behavior, we use reputation: a client keeps track of the server's behavior.

The MVP version could be:
- all servers start with zero reputation
- if the server honors the request, it gets +1;
- if the server does not respond after the initial query, it gets -1;
- if the server takes the money and _then_ does not respond, it gets banned (this client will never query it again).

Potential issues:
- An attacker can establish new server identities and continually run away with clients' money.
	- countermeasures:
		- a client only queries "trusted" servers (centralization);
		- when querying a new server, a client first sends a small (i.e. cheap) request to not risk too much.
- Think about how the ban mechanism can be abused. Can an attacker "frame" competitors' servers so that many clients ban them?

### Results cross-checking

> Never go to sea with two chronometers; take one or three.

The client not only wants to receive _some_ response, it wants to receive all relevant messages and only them.
We don't have consensus over history, so it's impossible to know for sure if a message is relevant.
In non security-critical settings, a client may just accept the risk that some messages may be missing.
For more certainty, the client may query 3 independent servers and compare the results.
Only messages returned by 3/3 or 2/3 are considered relevant.

Servers' reputation may then be adjusted, but it's not completely obvious how:
- imagine a server whose response has a message that no other response has.
	- should we punish it for inserting a fake message into history? or
	- should we reward it for providing the data that other are (perhaps intentionally) hiding?
- Same with a server that _misses_ some message that others have delivered: we don't know what the ground truth is anyway.

However, in the absence of a better mechanism, we can _define_ 2/3 as a validity criteria.
Then, it follows that a server that does _not_ have the "2/3" message is either malicious (censors) or badly managed (went offline when this message was propagated).
In any case, its reputation should be decreased.

Note: the cross-checking part is optional and may be considered to be out of scope for the MVP protocol.

# Evaluation

We measure the performance of our i13-ed Store protocol by the following metrics...

TODO: how do we check if we've solved the problem?

# Future work

Store-i13n-MVP is the simplest protocol we can start with.
Let us now outline the design choices to be made if we were to go beyond MVP.

## Price discovery

An incentive scheme should balance the costs and benefits for a node.
Rewards should compensate the cost of good behavior.
Punishments should offset the benefits that bad behavior may bring.

In the MVP i13n protocol, clients and servers establish a free market by negotiating prices.
A server should understand its true costs to negotiate effectively.
The costs of a Store server are storage, bandwidth, and computation.

Let us assume a constant flow of messages per epoch and a constant flow of requests for older messages.
There are two processes: storing incoming messages, and serving old messages to clients.

The cost of storing incoming messages for one epoch is composed of:
- storage:
	- storage costs of all older messages: proportional to cumulative (message size x time stored);
	- storage costs of newly arrived messages: proportional to message size;
	- a constant cost for I/O operations (storing new messages);
- bandwidth (download) for receiving new messages: proportional to the total size of incoming messages per epoch;
- computational costs of receiving and storing new messages.

(Strictly speaking, the I/O cost may not always be constant due to caching, disk fragmentation, etc.)

The cost of storing messages to clients, per epoch, is composed of:
- storage: none (it's accounted for as storing cost);
- bandwidth
	- upload: proportional to (number of clients) x (length of time frame requested) x (message size);
	- download: proportional to the number of requests;
- computational cost of handling requests.

Storage is likely the dominating cost.
Storage costs is proportional to the amount of information stored and the time it is stored for.
A cumulative cost of storing a single message grows linearly with time.
Assuming a constant stream of new messages, the total storage cost is quadratic in time.

The number of messages in a response may be approximated by the length of the time frame requested.
This assumes that messages are broadcast in the Relay network at a constant rate.

Computation: the server spends computing cycles while handling requests.
This costs likely depends not only on the computation itself, but also at the database structure.
For example, retrieving old or rarely requested messages from the local database may be more expensive than fresh or popular ones due to caching.

## RLN as a proxy for message relevance

RLN (rate limiting nullifiers) is a method of spam prevention in Relay ([RLN-Relay](https://rfc.vac.dev/spec/17/)).
The message sender generates a proof of enrollment in some membership set.
Multiple proofs generated within one epoch lead to punishment.
This technique limits the message rate from each node to at most one message per epoch.

In the i13n context, we can't prove whether a message has indeed been broadcast in the past.
Instead, we use RLN proofs as a proxy metric.
A valid RLN proof signifies that the message has been generated by a node with an active membership during a particular epoch.
Note that a malicious node with a valid membership can generate messages but not broadcast them.
Such messages would not be "relevant" (i.e., other nodes would be unaware of them), but they would satisfy the RLN-based heuristic.

Ideally, we would like to punish a server that omits relevant messages.
But as this can't be proven, we resort to reputation in this case.
In other words: if a client is dissatisfied with the response, it simply won't query this server anymore.
A way for the client to know (with some certainty) whether relevant messages have been omitted is to query another server.

## Privacy considerations

Light protocols, in general, have weaker privacy properties than P2P protocols.
In a client-server exchange, a client wants to selectively interact with the network.
By doing so, it often reveals what it is interested in (e.g., subscribes to particular topics).

A malicious Store server can spy on a client in the following ways:
- track what time frames a client is interested in;
- analyze the timing of requests;
- link requests done by the same client.

Also, citing the [Store specification](https://rfc.vac.dev/spec/13/):
> The main security consideration ... is that a querying node have to reveal their content filters of interest to the queried node, hence potentially compromising their privacy.

## Payment methods

The MVP protocol is agnostic to payment methods.
However, some payment methods may be more suitable than others.

What we want from a payment method:
- wide distribution (many people already have it);
- high liquidity (i.e., easy to buy or sell at a reasonable exchange rate);
- low latency;
- high security.

Let's list all (decentralized) payment options that we have:
- proof-of-work: outsource-able, unavailable for consumer hardware - or is it? (Equihash etc)
- proof-of-X (storage, etc)
- cryptocurrency:
	- ETH
	- a token on Ethereum (ERC20)
	- a token on another EVM blockchain
	- a token on an EVM-based rollup
	- a token on a non-EVM blockchain (BTC / Lightning?)

Note also that there may be different market models.
One model is that each client pays for its requests.
Another model assumes that (centralized) applications built on top of Waku buy "credits" in bulk for their users, for whom using the application (which may involve querying Store servers under the hood) is free of charge.

## Incentive compatibility

In file storage, I store a file and I pay for the ability to query it later. In Store, Alice relays a message, a server stores is, and later Bob queries it (and pays for it under an i13n scheme). Is there a mismatch between who incurs costs and who pays for it? Shall we think of ways to make Alice incur some costs too? See: https://github.com/waku-org/research/issues/32

## Generalization for other Waku protocols

We plan to generalize i13n for Store to other Waku protocols, in particular, to light protocols (Lightpush and Filter).

# Appendix: Deviations from the desired behavior

There are multiple ways for a node to deviate from the desired behavior.
We look at potential misbehavior from the server side and from the client side separately.
### Server: Slow response
The server takes too long to respond.
Possible reasons:
- the server is offline accidentally;
- the request describes too many relevant messages (the server is overwhelmed);
- the server is malicious and deliberately delays the response;
- the server doesn't have some of the relevant messages and tries to request them from other nodes.

### Server: Incomplete response
A relevant message is missing from the response.
Possible explanations:
- the server didn't receive the message when it was broadcast;
- the server deliberately withholds the message.

Contrary to blockchains, Relay doesn't have consensтus over relayed messages.
Therefore, it's impossible to distinguish between the two scenarios above.

### Server: Irrelevant response
The response contains a message that is not relevant.
There are two scenarios here depending on whether RLN proofs are enforced.
If RLN is not enforced, a server may insert any number or irrelevant messages into the response.
If RLN is enforced, a server can only do so as long as it has a valid membership to generate the respective proofs.
This doesn't eliminate the attack but limits its consequences.

### Client: Too many requests
The client sends many request to the server within a short period of time.
This may be seen as a DoS attack.

### Client: Request is too large
The client sends a response that incurs excessive expenses on the server.
For example, the request covers a very long period in history, or, more generically,
a period that contains many messages.
This may also be seen as a DoS attack.