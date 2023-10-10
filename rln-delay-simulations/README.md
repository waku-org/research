## rln-delay-simulations

This folder contains a `shadow` configuration to simulate multiple `nwaku` nodes in an end to end setup. Note that `nwaku` requires some minor modifications in the code, that can be found in the `simulations` branch.

## how to run

Get `nwaku` code with the modifications and compile it. See diff of latest commit.

```
https://github.com/waku-org/nwaku.git
cd nwaku
git checkout simulations
make wakunode2
```

Run the simulations:

```
shadow shadow.yaml
```

To ensure everything went allright

* no errors in any stderr: eg: shadow.data/hosts/peer1/wakunode2.1000.stderr
* see msg published: grep -nr '\[TX MSG\]*' shadow.data | wc -l
* grep -nr '\[RX MSG\]*' shadow.data | wc -l


```
TODO
```

Output

```
TODO
```