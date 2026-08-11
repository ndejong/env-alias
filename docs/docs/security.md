# Security

## Threat Model

Env Alias is a **local developer tool** — it runs on your machine, in your shell session, to load
environment variables. The primary security consideration is that definition files (YAML) can
instruct env-alias to execute arbitrary shell commands.

### Trust Boundary

| Input | Trusted? | Risk |
|-------|----------|------|
| Definition file you authored | ✅ Yes | None — you wrote it |
| Definition file from team repo | ⚠️ Conditional | Any contributor can inject `exec` commands |
| Definition file from external source | ❌ No | **Arbitrary code execution** |

### Attack Vectors

1. **Malicious `exec` attribute** — The `exec` attribute runs `subprocess.Popen(cmd, shell=True)`.
   A malicious definition file can execute any command on your machine.

2. **Secrets in environment variables** — Values are available in Env Alias's process while generation
   runs. Normal definitions are then exported into the calling shell and inherited by child processes.
   `name: null` avoids that normal caller-shell export, but does not stop Env Alias or a child `exec`
   process from using the value during the run.

3. **Ansible Vault password-file helper** — `ansible_vault_password_file: true` creates or reuses an
   executable script in the system temporary directory with `0o700` permissions. Its path is derived
   from the password, it is not removed automatically, and a generated environment variable containing
   the password is exported so the script can supply it to Ansible.

4. **Debug output can reveal secrets** — Running env-alias with `--debug` (or the `ENVALIAS_DEBUG`
   env var) writes verbose diagnostics to **stderr**, including the source, selectors and, in some
   paths, rendered command lines and resolved values. Secret values are replaced with `<redacted>`
   where they are already known to env-alias, but:
   - very short secrets (`len(value) <= 2`) are **not** redacted, and
   - an `exec:` command line containing a secret after `env:` substitution is logged before that
     secret has been registered for redaction.
   Treat `--debug` output as sensitive — do not paste it into issue trackers or chat.

## Mitigations

* **Never use untrusted definition files.** Do not pipe remote content into env-alias.
* **Review definition files in code review** — treat `exec:` lines with the same scrutiny as
  shell scripts.
* **Prefer ordinary local or HTTP(S) `source` values over `exec`** when you only need data. They do
  not run a user-supplied command.
* **Set restrictive file permissions** on definition files containing sensitive commands.
* **Use `name: null`** for sensitive intermediate values to suppress a normal export to the calling
  shell.
* **Do not use `value_to: <stderr>` for secrets.** STDERR may be captured by terminals, CI, or logs.
* **Be careful with `--debug` / `ENVALIAS_DEBUG`** on shared or captured terminals — stderr may
  contain secret material (see attack vector 4).

## Reporting Security Issues

Do not report vulnerabilities in a public issue. Email
[ndejong@threatpatrols.com](mailto:ndejong@threatpatrols.com) with `security: env-alias` in the subject
and enough detail to reproduce the problem safely.
