# Target Governance Artifacts

target repo 應保留的是 instantiated target-repo state，而不是整份 reusable policy。

## Keep in target repo

1. `.agents/specs/SPECS.md`
2. `.agents/specs/NEXT_STEPS.md`
3. `.agents/specs/RTM.md`
4. 各個 spec 目錄
5. target project profile
6. repo-specific service bundle mapping
7. repo-specific blockers、evidence、manual/review/runtime paths

## Do not duplicate into target repo

1. 完整 cross-skill routing policy
2. reusable bootstrap semantics
3. generic UAT iteration lifecycle wording
4. generic UAT-to-demo transition template

## Usage

1. 先用 reusable template 產生 snippet。
2. 再把 target repo 自己的 values 實例化到對應 artifacts。
3. 保持 generic policy 仍由 global skill / repo-owned companion skill 持有。
