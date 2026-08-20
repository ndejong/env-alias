# Multiple EnvAlias Files

Load **many definitions in a single invocation** and get one lazy alias per file. This is the
recommended form when you have several projects, since it collapses many `env-alias` process startups
into one.

## Example

[source](../definition-attributes/source.md){: .feat .f-src}
[parser](../definition-attributes/parser.md){: .feat .f-parser}
[selector](../definition-attributes/selector.md){: .feat .f-selector}

Save this ordinary definition as `~/.config/env-alias/env-project-a.yml`:

```yaml
env-alias:
  SERVICE_A_URL:
    source: "~/.config/project-a/service.json"
    parser: "json"
    selector: ".url"
```

Walkthrough:

1. Create the other project definition files in the same way, then register all of them at shell
   startup with one command:

    ```shell
    source <(env-alias \
      ~/.config/env-alias/env-project-a.yml \
      ~/.config/env-alias/env-project-b.yml \
      ~/.config/env-alias/env-project-c.yml)
    ```

    Or using a file pattern (glob):

    ```shell
    source <(env-alias ~/.config/env-alias/env-*.yml)
    ```

2. One invocation emits **one lazy alias per file**, named from each basename —
   `env-project-a`, `env-project-b`, `env-project-c`.
3. Each alias loads **only its own** file when invoked, so running `env-project-a` reads just
   `SERVICE_A_URL`, and nothing is fetched for a project until you actually use it.
