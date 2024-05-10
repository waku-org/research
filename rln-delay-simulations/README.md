# rln-delay-simulations

> All this work was presented as a paper "Message Latency in Waku Relay with Rate Limiting Nullifiers" in DLT2024 conference in Turin, Italy. See the [presentation](TODO) and the [paper](TODO).


This folder contains two methods of simulations, that aim to estimate the latency of waku messages in the network:
* Method 1: Using `shadow`, which allows simulating hundreds of nodes in a single machine, considering network conditions but not CPU. See [report](https://github.com/waku-org/research/issues/42)  
* Method 2: Using Digital Ocean, deploying real nodes in different locations in real machines with real network conditions, but due to cost limited to few nodes.

## Method 1: Shadow

This folder contains a `shadow` configuration to simulate `1000` `nwaku` nodes in an end to end setup:
* `nwaku` binaries are used, built with `make wakunode2` but with a minor modification, see [simulations](https://github.com/waku-org/nwaku/compare/master...simulations)
* `rln` is used with hardcoded static memberships, to avoid the sepolia node + contract, [see](https://raw.githubusercontent.com/waku-org/nwaku/master/waku/waku_rln_relay/constants.nim).
* Focused on measuring message propagation delays. Each message that is sent, encodes the timestamp when it was created.
* Requires significant resources to run (tested with 256 GB RAM)
* See simulation parameters: latency, bandwidth, amount of nodes, amount of publishers.
* Note that due to TCP flow control, when using big messages the first ones to arrive will show a higher delay. Filter them out to not bias the measurements.

### How to run

Get `nwaku` codebase and checkout to [simulations](https://github.com/waku-org/nwaku/tree/simulations) branch, build it and start the [shadow](https://github.com/shadow/shadow) simulation. Ensure `path` points to the `wakunode2` binary and you have enough resources.

```
git clone https://github.com/waku-org/nwaku.git
cd nwaku
git checkout simulations
make wakunode2
shadow shadow.yaml
```

### How to analyze

First check that the simulation finished ok. Check that the numbers match.
```
grep -nr 'ended_simulation' shadow.data | wc -l
# expected: 1000 (simulation finished ok in all nodes)

grep -nr 'tx_msg' shadow.data | wc -l
# expected: 10 (total of published messages)

grep -nr 'rx_msg' shadow.data | wc -l
# expected: 9990 (total rx messages)
```

Get metrics:
```
grep -nr 'rx_msg' shadow.data > latency.txt
grep -nr 'mesh_size' shadow.data > mesh_size.txt
```

Print results:
```
python analyze.py latency.txt "arrival_diff="
python analyze.py mesh_size.txt "mesh_size="
```

## Method 2: Digital Ocean

In this method we deploy real `nwaku` nodes at different locations with [some traces](https://github.com/waku-org/nwaku/compare/master...benchmark-latencies) that allow us to measure the propagation times of a given message across all nodes. For this experiment, 5
locations were selected:
* Frankfurt
* New York
* San Francisco
* Bangalore
* Singapore

Since deploying thousands of nodes would be costly, we connected the nodes in cascade:
`Singapore<->Bangalore<->San Francisco<->New York<->Frankfurt`

This forces a message to travel multiple hops. For example, a message introduced by the `Singapore` instance has to travel via `Bangalore` and `San Francisco` before reaching `New York`. This effectively simulates the existing hops in a real network.
The following commands allow to reproduce the setup. Its assumed that you have 5 different machines at 5 different locations and you can ssh into them:

In every machine, compile `wakunode2`
```
apt-get install build-essential git libpq5
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
git clone https://github.com/waku-org/nwaku.git
cd nwaku
git checkout benchmark-latencies
make wakunode2
```

Start `Singapore` node. Note `rest` api is enabled. Set also the message size that you want. Set `--max-msg-size=600KB` if you want a bigger message size.

```
export MSG_SIZE_KB=100
./build/wakunode2 --rest --rest-address=0.0.0.0 --relay=true --topic=/waku/2/test --rln-relay=true --rln-relay-dynamic=false --rln-relay-membership-index=0 --nodekey=070a6101339f8e03a56bf21127dbbb0110b9b6efdb1e217115ed6d80da7a46d0
```

Connect `Bangalore`<->`Singapore`
```
./build/wakunode2 --relay=true --topic=/waku/2/test --rln-relay=true --rln-relay-dynamic=false --rln-relay-membership-index=1 --nodekey=e9c166557cf6cf1d0fc6a4b1bb98e417a6de6c361b228dea72d54ffe4442a115 --staticnode=/ip4/SINGAPORE_IP/tcp/60000/p2p/16Uiu2HAmU3GnnKHPLJFWDLGMEt1mNDAFmaKWUdkR9gWutaLbk2xx
```


Connect `San Francisco`<->`Bangalore`
```
./build/wakunode2 --relay=true --topic=/waku/2/test --rln-relay=true --rln-relay-dynamic=false --rln-relay-membership-index=2 --nodekey=f9a4f0f889b6dbf55d6b32bb8a85c418df01f013cebcd23efd8a250df65d9337 --staticnode=/ip4/BANGALORE_IP/tcp/60000/p2p/16Uiu2HAmSDAp4VrbKQPStDLg7rc38JJR3zE5mJcFieAGJLBrCFCy

```

Connect `New York`<->`San Francisco`
```
./build/wakunode2 --relay=true --topic=/waku/2/test --rln-relay=true --rln-relay-dynamic=false --rln-relay-membership-index=3 --nodekey=100a04176710aabdec3258e1b6cdfbbdf602af36ea2311415ae7504bddd86cac --staticnode=/ip4/SANFRANCISCO_IP/tcp/60000/p2p/16Uiu2HAm8zWqrWRp6typPSdL7nqBRGbabH87vmkzN6A3McaGDj3C

```

Connect `Frankfurt`<->`NewYork`
```
./build/wakunode2 --relay=true --topic=/waku/2/test --rln-relay=true --rln-relay-dynamic=false --rln-relay-membership-index=4 --nodekey=eb131c2ee17807042f5051b6d7b9fbbbdc83369f28315157d8401fa13bf2b88f --staticnode=/ip4/NEW_YORK_IP/tcp/60000/p2p/16Uiu2HAmJdukvEFU1LhCQHGNcFviWMJh95PU4vMoun2uUvWtaWQL
```


Now you can inject a message via the `rest` API of the node in `Singapore`. This message will travel all the way to `Frankfurt` in 4 hops.
```
curl -X POST "http://SINGAPORE_IP:8645/relay/v1/messages/%2Fwaku%2F2%2Ftest" \
 -H "content-type: application/json" \
 -d '{"payload":"dontcare","contentTopic":"string"}'
```

If you check the logs of every machine, you will find the timestamp of when each node received the message.

Measuring the latency between each node can be interesting. It can be done with the [wakucanary](https://github.com/waku-org/nwaku/tree/master/apps/wakucanary) tool as follows.

Run `nwaku` in one  node:
```
docker run -p 60000:60000 harbor.status.im/wakuorg/nwaku:v0.25.0 --relay=true --nodekey=b03f13c0e075643e39b19ddef9206f868e94b759c7e847383b455f8d1991e695
```

And ping from other node. `REPLACE_IP` by the nodes public ip. The ping in `ms` will be displayed in the logs, measured using the `ping` protocol from `libp2p`.
```
docker run wakucanary:a1d5cbd -a=/ip4/REPLACE_IP/tcp/60000/p2p/16Uiu2HAmBxK6wbHqGtTKgEuYtuCxQCxGRKcu7iZeouEpaUr7ewwK -p=relay --ping
```


