# Env Alias

## Debug Output
Debug output can be easily added to STDERR by adding an optional `-d` argument to the 
`env-alias` command as shown below

```shell
eval $(env-alias my-alias-name -d ~/path-to/my-alias-name-config-file.yml)
```

Which will provides debug output to STDERR similar as shown
```shell
username@computer:~$ my-alias-name
20191201Z072045 - DEBUG - env-alias v0.0.1
20191201Z072045 - DEBUG -  export "local_text_01"="xxxxxxxxxxxxxxxx"
20191201Z072045 - DEBUG -  export "local_text_02"="xxxxxxxxxxxxxxxx"
...
```
