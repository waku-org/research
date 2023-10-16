## rln-delay-simulations

This folder contains a `shadow` configuration to simulate `1000` `nwaku` nodes in an end to end setup:
* `nwaku` binaries are used, built with `make wakunode2` but with a minor modification, see [simulations](https://github.com/waku-org/nwaku/compare/master...simulations)
* `rln` is used with hardcoded static memberships, to avoid the sepolia node + contract, [see](https://raw.githubusercontent.com/waku-org/nwaku/master/waku/waku_rln_relay/constants.nim).
* Focused on measuring message propagation delays. Each message that is sent, encodes the timestamp when it was created.
* Requires significant resources to run (tested with 256 GB RAM)
* See simulation parameters: latency, bandwidth, amount of nodes, amount of publishers.

## How to run

Get `nwaku` codebase and checkout to [simulations](https://github.com/waku-org/nwaku/tree/simulations) branch, build it and start the [shadow](https://github.com/shadow/shadow) simulation. Ensure `path` points to the `wakunode2` binary and you have enough resources.

```
git clone https://github.com/waku-org/nwaku.git
cd nwaku
git checkout simulations
make wakunode2
shadow shadow.yaml
```

## How to analyze

First check that the simulation finished ok. Check that the numbers match.
```
grep -nr 'ended_simulation' shadow.data | wc -l
# expected: 1000 (simulation finished ok in all nodes)

grep -nr 'tx_msg' shadow.data | wc -l
# expected: 15 (total of published messages)
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