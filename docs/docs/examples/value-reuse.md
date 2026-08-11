# Reuse Variables

Pull a credential or configuration value from a single source once, then expose it under multiple
environment-variable names so different tools can each find what they expect.

## Example

[source](../definition-attributes/source.md){: .feat .f-src}
[parser](../definition-attributes/parser.md){: .feat .f-parser}
[selector](../definition-attributes/selector.md){: .feat .f-selector}
[value](../definition-attributes/value.md){: .feat .f-value}

```yaml
env-alias:

  STORAGE_ACCESS_KEY_ID:
    source: "~/.config/backup/storage-credentials.ini"
    parser: "ini"
    selector: "default.accessKeyId"

  STORAGE_ACCESS_KEY:
    source: "~/.config/backup/storage-credentials.ini"
    parser: "ini"
    selector: "default.accessKey"

  BACKUP_S3_ACCESS_KEY_ID:
    value: "env:STORAGE_ACCESS_KEY_ID"

  BACKUP_S3_ACCESS_KEY:
    value: "env:STORAGE_ACCESS_KEY"

  BACKUP_REPOSITORY:
    value: "s3:personal-backups:monthly"
```

Walkthrough:

1. `STORAGE_ACCESS_KEY_ID` and `STORAGE_ACCESS_KEY` are read once from an INI credentials file using
   `parser: ini` and a `section.field` selector.
2. `BACKUP_S3_ACCESS_KEY_ID` and `BACKUP_S3_ACCESS_KEY` copy those resolved values whole via
   `value: 'env:...'`. The backup tool sees the naming it expects while the key is still sourced from a
   single, authoritative place.
3. `BACKUP_REPOSITORY` is a plain `value` that does not depend on any credential.

Use this when one secret must satisfy several tools, or when you want a stable canonical source with
convenience aliases — change the credential once in the source and every alias picks it up.
