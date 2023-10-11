## rln-delay-simulations

This folder contains a `shadow` configuration to simulate `1000` `nwaku` nodes in an end to end setup:
* `nwaku` binaries are used, built with `make wakunode2`
* Minor changes in `nwaku` are required, to timestamp messages and connect the peers without discovery. See [simulations](https://github.com/waku-org/nwaku/tree/simulations) branch.
* `rln` is used with hardcoded memberships, to avoid the sepolia node + contract, [see](https://raw.githubusercontent.com/waku-org/nwaku/master/waku/waku_rln_relay/constants.nim).
* Focused on measuring message propagation delays. Each message that is sent, encodes the timestamp when it was created.
* Same setup can be reused with different parameters, configured either via flags (see `shadow.yaml`) or modifying the code (see [simulations](https://github.com/waku-org/nwaku/tree/simulations)).
* Requires significant resources to run (tested with 256 GB RAM)
* Uses `100ms` of latency and `10Mbit` connection per node.

## How to run

Get `nwaku` code with the modifications and compile it. See diff of latest commit.

Get the [simulations](https://github.com/waku-org/nwaku/tree/simulations) branch, build it and start the [shadow](https://github.com/shadow/shadow) simulation. Ensure `path` points to the `wakunode2` binary and you have enough resources.

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

Print metrics:
```
grep -nr 'rx_msg' shadow.data > latency.txt
grep -nr 'mesh_size' shadow.data > mesh_size.txt
```

```
python analyze.py latency.txt "arrival_diff="
python analyze.py mesh_size.txt "mesh_size="

no msg payload is added
Config: file: latency.txt field: arrival_diff=
number_samples=14985
Percentiles. P75=401.0 P95=502.0
Statistics. mode_value=400 mode_count=1521 mean=320.76176176176176 max=701 min=100

this is wrong. was generating the random bytes inside the timer.
Config: file: latency.txt field: arrival_diff=
number_samples=14985
Percentiles. P75=456.0 P95=583.7999999999993
Statistics. mode_value=412 mode_count=84 mean=365.7955288621955 max=873 min=100

run 1
Config: file: latency.txt field: arrival_diff=
number_samples=14985
Percentiles. P75=451.0 P95=578.0
Statistics. mode_value=318 mode_count=84 mean=362.09422756089424 max=778 min=100

Config: file: latency.txt field: arrival_diff=
number_samples=14985
Percentiles. P75=452.0 P95=587.0
Statistics. mode_value=313 mode_count=77 mean=360.5741741741742 max=868 min=100

10 Mb data
Config: file: latency.txt field: arrival_diff=
number_samples=14985
Percentiles. P75=741.0 P95=901.0
Statistics. mode_value=596 mode_count=108 mean=615.3937937937937 max=1227 min=107

```



# TODO: remove
Amount of samples: 14985
percentile 75:  300.0
percentile 25:  201.0
mode : ModeResult(mode=300, count=4650)
worst:  401
best:  100



file:  latency.txt
parse start:  diff:   parse end:   milliseconds
[301 400 400 ... 300 502 601]
Amount of samples: 14985
percentile 75:  402.0
percentile 25:  202.0
mode : ModeResult(mode=400, count=1542)
worst:  1300
best:  100

```

mesh
```
grep -nr 'mesh size' shadow.data > mesh.txt
python metrics.py mesh.txt "mesh size: " " of topic"

Amount of samples: 1000
percentile 75:  7.0
percentile 25:  5.0
mode : ModeResult(mode=5, count=248)
worst:  12
best:  4

Amount of samples: 1000
percentile 75:  3.0
percentile 25:  2.0
mode : ModeResult(mode=2, count=469)
worst:  5
best:  2
```


```
Amount of samples: 14985
percentile 75:  300.0
percentile 25:  201.0
mode : ModeResult(mode=300, count=4650)
worst:  401
best:  100
```