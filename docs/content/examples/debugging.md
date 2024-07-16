# Debugging

Debug output can be easily added to STDERR by adding an optional `--debug` argument to the 
`env-alias` command as shown below

```shell
source <(env-alias --debug ~/projects/awesome/env-awesome-vars.yml)
```

Which will provides debug output to STDERR similar as shown
```shell
❯ env-awesome-vars
2024-09-21T17:34:24+1000 | DEBUG | env-alias | EnvAliasGenerator.generate()
2024-09-21T17:34:24+1000 | DEBUG | env-alias | EnvAliasConfig.load_definitions(definitions_file='dev/env-foobar.yml')
2024-09-21T17:34:24+1000 | DEBUG | env-alias | Definitions loaded from definitions_file='dev/env-foobar.yml'
2024-09-21T17:34:24+1000 | DEBUG | env-alias | Loaded environment definition for 'EXAMPLE'
2024-09-21T17:34:24+1000 | DEBUG | env-alias | Total 1 definitions in definitions_file=PosixPath('dev/env-foobar.yml')
2024-09-21T17:34:24+1000 | DEBUG | env-alias | EnvAliasGenerator.get_definition_value(definition.name='EXAMPLE', ...)
2024-09-21T17:34:24+1000 | DEBUG | env-alias | EnvAliasContent.local(filename=/proc/cpuinfo)
2024-09-21T17:34:24+1000 | DEBUG | env-alias | EnvAliasContent.local(filename=/proc/cpuinfo) > content_type='text'
2024-09-21T17:34:24+1000 | DEBUG | env-alias | output=' export "EXAMPLE"="model name\t: Intel(R) Core(TM) i5-6300U CPU @ 2.40GHz"'
```
