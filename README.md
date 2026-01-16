# cargotree2mermaid
Convert file created by 'cargo tree' to mermaid-format file.

# run
```
./cargotree2mermaid.py -h
usage: cargotree2mermaid.py [-h] [-i INPUT] [-b BLACKLIST] [-o OUTPUT] [-w WHITE] [--direction {TD,TB,LR,RL,BT}]
...

./cargotree2mermaid.py -i ./example/crates-dep.txt -b ./example/blacklist.txt -o ./example/crates-dep.mmd -w ./example/whitelist.txt
# You can check the mermaid file ./example/crates-dep.mmd and whitelist file ./example/whitelist.txt
```
# example
The crates-dep.txt is from https://github.com/Starry-OS/StarryOS

```
git clone git@github.com:Starry-OS/StarryOS.git
cd StarryOS
cargo tree >crates-dep.txt
```

The crates in black.list.txt are not from rcore-os, arceos-org, Starry-OS, arceos-hypervisor github repos.