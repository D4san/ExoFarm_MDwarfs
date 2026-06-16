# Repository Review, Organization, and Cleanup Workflow

**Adopted:** 2026-06-16

Use this workflow when the user asks to review, organize, clean, depurar, or
tidy the repository. The goal is to make the project clearer without erasing
scientific evidence by accident.

## Trigger phrases

Apply this workflow when the request says things like:

- "revisemos el repo"
- "organicemos el repo"
- "depuremos el repo"
- "hay codigo basura?"
- "borremos experimentos fallidos"
- "limpiemos outputs temporales"

## Working principle

Cleanup is a scientific curation task, not just file deletion. A generated file
can be disposable, but the reasoning, configuration, logs, and final evidence
must remain understandable to a colleague.

## Step 1: Inspect before changing

Start with read-only checks:

```bash
git status --short
Get-ChildItem <target> -Force
Get-ChildItem <target> -Recurse -Directory -Force
Get-ChildItem <target> -Recurse -File -Force
rg -n "TODO|FIXME|HACK|debug|legacy|temp|copy|deprecated" <target>
```

For generated products, also summarize size and whether files are tracked:

```bash
git ls-files <target>
Get-ChildItem <target> -Recurse -File | Measure-Object Length -Sum
```

## Step 2: Classify findings

Report findings before deleting. Use these categories:

| Category | Meaning | Default action |
| --- | --- | --- |
| Canonical evidence | Current inputs, scripts, reports, `.vul` outputs, profiles, spectra, or figures used by the active argument. | Keep. |
| Audit evidence | Manifests, configuration snapshots, comparison CSVs, logs or reports needed to reproduce a decision. | Keep unless a better report preserves the same evidence. |
| Legacy evidence | Superseded but scientifically interpretable material, such as old sensitivity matrices. | Keep or move under a clearly labelled legacy path. |
| Temporary execution residue | `temp_run_*`, caches, copied workspaces, failed scratch outputs, build products. | Delete after confirming canonical products/logs are preserved. |
| Ambiguous product | File whose provenance or use is unclear. | Do not delete; document the question. |

## Step 3: Ask before destructive cleanup

For deletion, propose exact targets and wait for approval unless the user has
already explicitly approved those targets in the same turn.

Prefer wording like:

```text
I found 8 untracked temp_run_* folders, 660 MB total. They duplicate VULCAN
workspaces and each canonical .vul already exists in Results/Outputs. Do you
want me to delete only those temp folders?
```

Do not delete:

- the only copy of an input, configuration, log, or report;
- canonical `.vul`, profile, synthetic-data, retrieval, or figure products;
- legacy products that still explain a scientific branch;
- files with unclear provenance.

## Step 4: Delete narrowly and verify

After approved deletion, remove only the approved paths. Then verify:

```bash
Get-ChildItem <target> -Force
git status --short -- <target>
```

Summarize what was removed and what was intentionally left unchanged.

## Step 5: Record durable decisions

If the cleanup changes repository policy or scientific interpretation, update
one of these:

- `AGENTS.md` for rules future agents must follow;
- `docs/README.md` for new reports;
- `docs/repository_structure.md` for canonical locations;
- `experiments/README.md` for campaign status;
- `experiments/cleanup.md` for deletion candidates and completed cleanup.

Keep this lightweight. Do not recreate a large registry unless the project
outgrows these simple Markdown records.
