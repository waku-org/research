Our goal is to add an incentivization scheme to Waku to make it (more) incentive compatible.
In what follows, we abbreviate incentivization as i13n.

We aim to answer the following questions:

1. what is the structure of the protocols in question?
2. what is the desired behavior of protocol participants?
3. what deviations from the desired behavior occur without incentivization?
4. what incentivization tools do we have?
5. what tools are appropriate for our purpose?
6. what parameters can we chose? what are our restrictions?
7. suggest a concrete i13n architecture.
8. how do we check if we've solved the problem?

# Overview

Waku implements a modular decentralized censorship resistant P2P communications protocol.
Waku consists of multiple protocols (see [architecture](https://waku.org/about/architect)).
We focus on the main four are Relay (a P2P protocol), and three light protocols: Filter, Store, and Lightpush, which have a client-server architecture (aka request-response).

A Waku node is a node that runs at least one of the Waku protocols.
A full Waku node is a node that runs Relay.
A light Waku node as a node that only runs client-side of one of the light protocols.
See also: https://github.com/waku-org/research/issues/28

In light protocols, a client sends a request to a server.
A server (a Relay node) performs some actions and returns a response, in particular:
- [[Filter]]: the server will relay (only) messages that pass a filter to the client;
- [[Store]]: the server responds with messages broadcast within the specified time frame;
- [[Lightpush]]: the server publishes the client's message to the Relay network.

Waku aims to function on widely available hardware.
Hardware requirements for light nodes are lower than for full nodes.
In particular, bandwidth consumption should be limited (estimated at 10 Mbps).
See also: https://github.com/waku-org/research/issues/31

# Store protocol

We first focus on i13n of the Store protocol.
Similar techniques may be later applied to other protocols.

Store is a client-server protocol.
A client asks the node to respond with relevant messages previously relayed through the Relay protocol.
A relevant message is a message that has been broadcast via Relay within the specified time frame.
The response may be split into multiple parts, as specified by pagination parameters.

TODO: Strictly speaking, the definition of relevant is inconsistent because there is no consensus over messages. A message may be broadcast but not received by some nodes. Does this happen often? Can and should we do something about it?

## Desired behavior

The desired behavior of a Store-server node is to store all non-ephemeral messages forever.

TODO: address the obvious concern that storing everything forever is unsustainable. Should there be some cut-off time after which old messages are no longer stored?

Let's say, a client issues a request to the server.
We want the following to happen:

- the server responds quickly;
- all the messages in the response are relevant;
- the response contains only relevant messages.

TODO: is this the full definition of the desired behavior?

### RLN as a proxy metric of message relevance

RLN (rate limiting nullifiers) is a method of spam prevention in Relay.
The message sender generates a proof of enrollment in some membership set.
Multiple proofs generated within one epoch lead to punishment.
This technique limits the message rate from each node to at most one message per epoch.
See also: https://rfc.vac.dev/spec/17/

In the i13n context, we can't prove whether a message has indeed been broadcast in the past.
Instead, we use RLN proofs as a proxy metric.
A valid RLN proof signifies that the message has been generated by a node with an active membership during a particular eposh.
TODO: make sure the above is correct: what exactly does RLN prove?

## Deviations from the desired behavior

There are multiple ways for a node to deviate from the desired behavior.
TODO: are we talking only about the server here, or should also discuss client (e.g., DoS)?
### Slow response
The server takes too long to respond.
Possible reasons:
- the server is offline accidentally;
- the request describes too many relevant messages (the server is overwhelmed);
- the server is malicious and deliberately delays the response;
- the server doesn't have some of the relevant messages and tries to request them from other nodes.

### Incomplete response
A relevant message is missing from the response.
Possible explanations:
- the server didn't receive the message when it was broadcast;
- the server deliberately withholds the message.

Contrary to blockchains, Relay doesn't have consensus over relayed messages.
Therefore, it's impossible to distinguish between the two scenarios above.
TODO: given this fact, what's the best we can aim for?

### Irrelevant response
The response contains a message that is not relevant.
There are two scenarios here depending on whether RLN proofs are enforced.
If RLN is not enforced, a server may insert any number or irrelevant messages into the response.
If RLN is enforced, a server can only do so as long as it has a valid membership to generate the respective proofs.
This doesn't eliminate the attackbut limits its consequences.

TODO: what are the powers of a malicious server when it comes to generating proofs for irrelevant messages? Can the server generate proofs for past epochs?

## Privacy considerations

Light protocols, in general, have weaker privacy properties than P2P protocols.
In a client-server exchange, a client wants to selectively interact with the network.
By doing so, it often reveals what it is interested in (e.g., subscribes to particular topics).

A malicious Store server can spy on a client in the following ways:
- track what time frames a client is interested in;
- analyze the timing of requests;
- link requests done by the same client.

TODO: expand in the context of an incentivized protocol.


# Cost-benefit analysis
The goal of i13n is to make nodes more likely to exhibit the desired behavior.
An incentive scheme links the payoffs to whether nodes follow the protocol or not.
Good behavior should be rewarded, bad behavior punished.

An incentive scheme should balance the costs and benefits for a node.
Rewards should compensate the cost of good behavior.
Punishments should offset the benefits that bad behavior may bring.

Let us analyze the costs and benefit of a server that are specific to the Store protocol:
- storage;
- bandwidth;
- computation.

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

TODO: write this down mathematically.

Storage is likely the dominating cost.
Storage costs is proportional to the amount of information stored and the time it is stored for.
A cumulative cost of storing a single message grows linearly with time.
Assuming a constant stream of new messages, the total storage cost is quadratic in time.

The number of messages in a response may be approximated by the length of the time frame requested.
This assumes that messages are broadcast in the Relay network at a constant rate.

Computation: the server spends computing cycles while handling requests.
This costs likely depends not only on the computation itself, but also at the database structure.
For example, retrieving old or rarely requested messages from the local database may be more expensive than fresh or popular ones due to caching.

TODO: In file storage, I store a file and I pay for the ability to query it later. In Store, Alice relays a message, a server stores is, and later Bob queries it (and pays for it under an i13n scheme). Is there a mismatch between who incurs costs and who pays for it? Shall we think of ways to make Alice incur some costs too? See: https://github.com/waku-org/research/issues/32

# Incentivization tools

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
Assuming there is a monetary aspect too, low-reputation servers miss out on potential revenue or lose their deposit.
Reputation, however, assumes ether a repeated interaction (i.e., local reputation), or some amount of trust / centralization (centrally managed rankings).

Monetary i13n tools, in turn, pose a key question: how to ensure atomicity between performance and reward or punishment?
In other words, if the client pays first, the server may take the money and not provide the servers.
Analogously, if the payment is due after the fact, the client can refuse to pay.
Linking payments with behavior involves a certain amount of trust as well.

This issue is somewhat linked to the problem of Lightning watchtower incentivization (see https://www.talaia.watch/).

A general observation: if monetary flows are dependent on events in the past, and there is no consensus on what exactly happened in the past, the scheme can be exploited.
TODO: can we use some on-chain component here as a semi-trusted arbiter?

## Payment methods

What we want from a payment method (order of priority to be discussed):
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

# Related work

Decentralized storage is not a new idea. What is relevant for us?

1. Federated real-time messaging (IRC, mailing lists). There is no "sync" in IRC; there are simply logs of prior conversations optionally hosted wherever.
2. Centralized file storage (FTP, later Dropbox). Requires trust in availability, but not necessarily confidentiality: content can be encrypted (modulo metadata).
3. P2P file-sharing: Napster, BitTorrent, eDonkey. The power of defaults, local reputation.
4. Decentralized storage in the blockchain age: Storj, Sia, Filecoin, IPFS, Codex...

# Future work

How to generalize i13n for Store to other Waku protocols?