# cargotree2mermaid.py
Convert file created by 'cargo tree' to mermaid-format file.

# mermaid_level_nodes.py
Give the dependency info of the node in mermaid-format file.

# run
```
./cargotree2mermaid.py -h
usage: cargotree2mermaid.py [-h] [-i INPUT] [-b BLACKLIST] [-o OUTPUT] [-w WHITE] [--direction {TD,TB,LR,RL,BT}]
...

./cargotree2mermaid.py -i ./example/crates-dep.txt -b ./example/blacklist.txt -o ./example/crates-dep.mmd -w ./example/whitelist.txt
# You can check the mermaid file ./example/crates-dep.mmd and whitelist file ./example/whitelist.txt
# If -o is not provided, mermaid output will be printed to screen

./mermaid_level_nodes.py -i ./example/crates-dep.mmd -n 2 -u
# Output file defaults to ./example/crates-dep.up.level2.txt
# Each line format: crate  :   dep1, dep2
# If -o is not provided, output will be printed to screen

./mermaid_level_nodes.py -i ./example/crates-dep.mmd -n 2 -d
# Output file defaults to ./example/crates-dep.down.level2.txt
# Each line format: crate  :   dep1, dep2
# If -o is not provided, output will be printed to screen
```
# example
The crates-dep.txt is from https://github.com/Starry-OS/StarryOS

```
git clone git@github.com:Starry-OS/StarryOS.git
cd StarryOS
# setup development env ...

cargo tree >crates-dep.txt

# use cargotree2mermaid.py -i SOME-PATH/crates-dep.txt ...
```

The crates-dep.txt is from https://github.com/arceos-org/arceos-apps

```
git clone git@github.com:arceos-org/arceos-apps.git
cd arceos-apps
# setup development env ...

# riscv64 helloworld
cargo tree -p arceos-helloworld --target riscv64gc-unknown-none-elf --features "axstd/defplat axstd/log-level-info" >crates-dep.txt

# aarch64 helloworld
cargo tree -p arceos-helloworld --target aarch64-unknown-none-softfloat --features "axstd/defplat axstd/log-level-info" >crates-dep.txt

#x86_64 helloworld
cargo tree -p arceos-helloworld --target x86_64-unknown-none --features "axstd/defplat axstd/log-level-info" >crates-dep.txt

#loongarch64 helloworld
cargo tree -p arceos-helloworld --target loongarch64-unknown-none-softfloat --features "axstd/defplat axstd/log-level-info" >crates-dep.txt

# use cargotree2mermaid.py -i SOME-PATH/crates-dep.txt ...
```

## NOTICE
The crates in blacklist.txt(as input file for cargotree2mermaid.py) are not from github repos: rcore-os, arceos-org, Starry-OS, arceos-hypervisor, etc.

The crates in output file(e.g. whitelist.txt) for cargotree2mermaid.py are from  github repos: rcore-os, arceos-org, Starry-OS, arceos-hypervisor, etc.