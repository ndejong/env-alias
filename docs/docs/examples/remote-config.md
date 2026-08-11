# Remote Configuration

Fetch live values directly from an HTTP(S) endpoint and pick a single item out of the response — no
shell, no scripts, no temporary files.

## Example

[source](../definition-attributes/source.md){: .feat .f-src}
[parser](../definition-attributes/parser.md){: .feat .f-parser}
[selector](../definition-attributes/selector.md){: .feat .f-selector}

```yaml
env-alias:

  REPOSITORY_DEFAULT_BRANCH:
    source: "https://api.github.com/repos/threatpatrols/env-alias"
    parser: "json"
    selector: ".default_branch"
```

Walkthrough:

1. `source:` is an HTTP(S) URL, so env-alias performs a `GET` request to fetch it — no curl, no shell.
2. `parser: json` deserialises the response.
3. `selector: ".default_branch"` pulls out a stable scalar value instead of depending on the order of
   a live list.
