gh-action-pip-audit
===================

[![CI](https://github.com/trailofbits/gh-action-pip-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/trailofbits/gh-action-pip-audit/actions/workflows/ci.yml)
[![Self-test](https://github.com/trailofbits/gh-action-pip-audit/actions/workflows/selftest.yml/badge.svg)](https://github.com/trailofbits/gh-action-pip-audit/actions/workflows/selftest.yml)

A GitHub Action that uses [`pip-audit`](https://github.com/trailofbits/pip-audit)
to scan Python dependencies for known vulnerabilities.

## Index

* [Usage](#usage)
* [Configuration](#configuration)
  * [⚠️ Internal options ⚠️](#internal-options)
* [Troubleshooting](#troubleshooting)
* [Licensing](#licensing)
* [Code of Conduct](#code-of-conduct)

## Usage

Simply add `trailofbits/gh-action-pip-audit` to one of your workflows:

```yaml
jobs:
  selftest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: install
        run: python -m pip install .
      - uses: trailofbits/gh-action-pip-audit@v1.0.0
```

Or, with a virtual environment:

```yaml
jobs:
  selftest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: install
        run: |
          python -m venv env/
          source env/bin/activate
          python -m pip install .
      - uses: trailofbits/gh-action-pip-audit@v1.0.0
        with:
          virtual-environment: env/
```

By default, `pip-audit` will run in "`pip list` source" mode, meaning that it'll
attempt to collect dependencies from the local environment. See
the [configuration](#configuration) documentation below for more input
and behavioral options.

## Configuration

`gh-action-pip-audit` takes a variety of configuration inputs, all of which are
optional.

### `inputs`

**Default**: Empty, indicating "`pip list` source" mode

The `inputs` setting controls what sources `pip-audit` runs on.

To audit one or more requirements-style inputs:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    inputs: requirements.txt dev-requirements.txt
```

To audit a project that uses `pyproject.toml` for its dependencies:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    # NOTE: this can be `.`, for the current directory
    inputs: path/to/project/
```

### `virtual-environment`

**Default**: Empty, indicating no virtual environment

The `virtual-environment` setting controls the
[virtual environment](https://docs.python.org/3/tutorial/venv.html) that this
action loads to, if specified. The value is the top-level directory for the
virtual environment, which is conventionally named `env` or `venv`.

Depending on your CI and project configuration, you may or may not need this
setting. Specifically, you only need it if you satisfy *all* of the following
conditions:

1. You are auditing an *environment* (**not** a requirements file or other
   project metadata)
2. Your environment is not already "active", i.e. `python -m pip` points to a
   different `pip` than the one that your environment uses

Example: use the virtual environment specified at `env/`, relative to the
current directory:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    virtual-environment: env/
    # Note the absence of `input:`, since we're auditing the environment.
```

### `local`

**Default**: `false`

The `local` setting corresponds to `pip-audit`'s `--local` flag, which controls
whether non-local dependencies are included when auditing in "`pip list` source"
mode.

By default all dependencies are included; with `local: true`, only dependencies
installed directly into the current environment are included.

Example:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    local: true
```

### `vulnerability-service`

**Default**: `PyPI`

**Options**: `PyPI`, `OSV` (case insensitive)

The `vulnerability-service` setting controls which vulnerability service is used for the audit.
It's directly equivalent to `pip-audit --vulnerability-service=...`.

To audit with OSV instead of PyPI:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    vulnerability-service: osv
```

### `require-hashes`

**Default**: `false`

The `require-hashes` setting controls whether strict hash checking is enabled.
It's directly equivalent to `pip-audit --require-hashes ...`.

Example:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    # NOTE: only works with requirements-style inputs
    inputs: requirements.txt
    require-hashes: true
```

### `no-deps`

**Default**: `false`

The `no-deps` setting controls whether dependency resolution is performed.
It's directly equivalent to `pip-audit --no-deps ...`.

Example:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    # NOTE: only works with requirements-style inputs
    inputs: requirements.txt
    no-deps: true
```

### `summary`

**Default**: `true`

The `summary` setting controls whether a GitHub
[job summary](https://github.blog/2022-05-09-supercharging-github-actions-with-job-summaries/)
is rendered at the end of the action.

Example:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    summary: false
  ```

### `index-url`

**Default**: Empty, indicating [PyPI](https://pypi.org)

The `index-url` setting specifies a base URL for an alternative PEP 503-compatible
package index.

**This is probably not want you want.** If your goal is to add *complementary*
indices to search (such as a corporate index with private packages), see
[`extra-index-urls`](#extra-index-urls).

Example:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    index-url: https://example.corporate.local/simple
```

### `extra-index-urls`

**Default**: Empty (no extra indexes are searched by default)

The `extra-index-urls` setting specifies one or more *extra* PEP 503-compatible packages
indexes to search when resolving dependencies. Each URL is whitespace-separated.

Example:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    extra-index-urls: |
      https://example.corporate.local/simple
      https://prod.corporate.local/simple
```

### `ignore-vulns`

**Default**: Empty (no vulnerabilities are ignored)

The `ignore-vulns` setting specifies one or more vulnerability IDs to
ignore (i.e., exclude from the results) if present. Each ID is whitespace-separated.

Example

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    ignore-vulns: |
      GHSA-XXXX-YYYYYY
      PYSEC-AAAA-BBBBB
```

### Internal options
<details>
  <summary>⚠️ Internal options ⚠️</summary>

  Everything below is considered "internal," which means that it
  isn't part of the stable public settings and may be removed or changed at
  any point. **You probably do not need these settings.**

  All internal options are prefixed with `internal-be-careful-`.

  #### `internal-be-careful-allow-failure`

  **Default**: `false`

  The `internal-be-careful-allow-failure` setting allows the job to pass, even
  if the underlying `pip-audit` run fails (e.g. due to vulnerabilities detected).

  Be very careful with this setting! Using it unwittingly will prevent the action
  from failing your CI when `pip-audit` fails, which is probably not what you want.

  Example:

  ```yaml
  - uses: trailofbits/gh-action-pip-audit@v1.0.0
    with:
      internal-be-careful-allow-failure: true
  ```

  #### `internal-be-careful-debug`

  **Default**: `false`

  The `internal-be-careful-debug` setting enables additional debug logs,
  both within `pip-audit` itself and the action's harness code. You can
  use it to debug troublesome configurations.

  Be mindful that `pip-audit`'s own debug logs contain HTTP requests,
  which may or may not be sensitive in your use case.

  Example:

  ```yaml
  - uses: trailofbits/gh-action-pip-audit@v1.0.0
    with:
      internal-be-careful-debug: true
  ```

</details>

## Troubleshooting

This section is still a work in progress. Please help us improve it!

### The action takes longer than I expect!

If you're auditing a requirements file, consider setting `no-deps: true` or
`require-hashes: true`:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    inputs: requirements.txt
    require-hashes: true
```

or:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    inputs: requirements.txt
    no-deps: true
```

See the
["`pip-audit` takes longer than I expect!"](https://github.com/trailofbits/pip-audit#pip-audit-takes-longer-than-i-expect)
troubleshooting for more details.

### The action shows dependencies that aren't in my environment!

In the default ("`pip list` source") configuration, `pip-audit` collects all
dependencies that are visible in the current environment.

Depending on the project or CI's configuration, this can include packages installed
by the host system itself, or other Python projects that happen to be installed.

To minimize external dependencies, you can opt into a virtual environment:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    # must be populated earlier in the CI
    virtual-environment: env/
```

and, more aggressively, specify that only dependencies marked as "local"
in the virtual environment should be included:

```yaml
- uses: trailofbits/gh-action-pip-audit@v1.0.0
  with:
    # must be populated earlier in the CI
    virtual-environment: env/
    local: true
```

## Licensing

`gh-action-pip-audit` is licensed under the Apache 2.0 License.

## Code of Conduct

Everyone interacting with this project is expected to follow the
[PSF Code of Conduct](https://github.com/pypa/.github/blob/main/CODE_OF_CONDUCT.md).
