# 简介
本仓库提供三个小工具，用于把 `cargo tree` 输出转换为 Mermaid 依赖图，并进一步进行依赖分析。所有脚本都支持：

- 从文件输入（`-i FILE`）
- 从 stdin 输入（省略 `-i` 或 `-i -`），便于用管道串联
- 输出到文件（`-o FILE`）或直接打印到屏幕

## cargotree2mermaid.py
将 `cargo tree` 的文本输出转换为 Mermaid 依赖图（`graph TD`/`LR` 等）。

### 主要参数
- `-i, --input`：输入文件路径；省略或 `-i -` 表示从 stdin 读取
- `-b, --blacklist`：黑名单文件，按逗号或空白分隔 crate 名称
- `-o, --output`：Mermaid 输出文件；不提供则输出到屏幕
- `-w, --white`：输出白名单文件（实际出现在依赖图中的 crate）
- `--direction`：Mermaid 方向（`TD/TB/LR/RL/BT`）

### 用法示例
从文件读取并生成 Mermaid + whitelist：
```
./cargotree2mermaid.py -i ./example/crates-dep.txt -b ./example/blacklist.txt -o ./example/crates-dep.mmd -w ./example/whitelist.txt
```

使用管道（stdin）：
```
cargo tree | ./cargotree2mermaid.py > crates-dep.mmd
```

生成图片（可选）：
```
mmdc -s 4 -i crates-dep.mmd -o crates-dep.png
# 若无 mmdc: npm install -g @mermaid-js/mermaid-cli
feh crates-dep.png
# 若无 feh: sudo apt install feh -y
```

## mermaid_level_nodes.py
从 Mermaid 依赖图中提取某一“层级”的节点列表，并列出其直接依赖。

### 主要参数
- `-i, --input`：Mermaid 文件；省略或 `-i -` 表示从 stdin 读取
- `-n, --level`：依赖层级（`NUM >= 0`）
- `-u, --up`：向上依赖（默认方向）
- `-d, --down`：向下依赖（反向方向）
- `-o, --output`：输出文件；不提供则输出到屏幕

### 用法示例
从文件读取并输出到屏幕：
```
./mermaid_level_nodes.py -i ./example/crates-dep.mmd -n 2 -u
```

指定输出文件：
```
./mermaid_level_nodes.py -i ./example/crates-dep.mmd -n 2 -d -o ./example/level2.down.txt
```

使用管道（stdin）：
```
cat ./example/crates-dep.mmd | ./mermaid_level_nodes.py -n 2 -u
```

## 组合使用（管道）
典型场景：直接从 `cargo tree` 输出生成特定层级依赖列表：
```
cargo tree | ./cargotree2mermaid.py | ./mermaid_level_nodes.py -n 2 -u
```

## nodedeps.py
从 Mermaid 依赖图中提取指定节点的所有直接或递归依赖关系，输出子图。

### 主要参数
- `-i, --input`：Mermaid 文件；省略或 `-i -` 表示从 stdin 读取
- `-n, --node`：要查询的节点名称（crate 名称，不需要版本号）
- `-u, --up`：查询向上依赖（即哪些节点依赖这个节点）
- `-d, --down`：查询向下依赖（即这个节点依赖哪些节点）
- `-l, --level`：最大依赖层级深度（可选，不设置则无限制）
- `-o, --output`：输出文件；不提供则输出到屏幕

### 用法示例
查询节点的向下依赖（这个节点依赖了什么），仅限1层深度：
```
./nodedeps.py -i ./example/crates-dep.mmd -d -n kernel-alloc -l 1
```

查询节点的向下依赖（无深度限制）：
```
./nodedeps.py -i ./example/crates-dep.mmd -d -n kernel-alloc
```

输出类似：
```
graph TD
    kernel_alloc_v0_1_0[kernel-alloc v0.1.0] --> customizable_buddy_v0_0_3[customizable-buddy v0.0.3]
    kernel_alloc_v0_1_0[kernel-alloc v0.1.0] --> page_table_v0_0_6[page-table v0.0.6]
```

查询节点的向上依赖（什么节点依赖了这个节点），仅限1层深度：
```
./nodedeps.py -i ./example/crates-dep.mmd -u -n kernel-alloc -l 1
```

使用管道和输出到文件，限制深度为2层：
```
cat ./example/crates-dep.mmd | ./nodedeps.py -d -n kernel-alloc -l 2 -o /tmp/kernel-alloc-deps.mmd
```

## 综合示例：从 cargo tree 到依赖分析
```
# 方案一：生成完整依赖图，然后查询特定节点
cargo tree | ./cargotree2mermaid.py -o deps.mmd
./nodedeps.py -i deps.mmd -d -n kernel-alloc

# 方案二：一行命令（使用管道）
cargo tree | ./cargotree2mermaid.py | ./nodedeps.py -d -n kernel-alloc
```

# example

```
# Produce crates-dep.txt is from https://github.com/Starry-OS/StarryOS
# setup rust/c development env for rust os, rust/c app...

git clone git@github.com:Starry-OS/StarryOS.git
cd StarryOS
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