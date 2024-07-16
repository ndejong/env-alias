# selector

Selectors make it possible to "pick" a value from the parsed content.  

Structured content formats (ini, yaml, json) support selectors using -
 - slash-notation (eg: `/foo/bar`)
 - dot-notation (eg: `foo.0.bar`)
 - brace-notation (eg: `foo[0]bar`)

Text files support line-number selectors only; by default selector value is one (`1`) for text
content type, thus if omitted the first line only will be selected.

NB: previous versions of env-alias supported a none/null selector that worked in teh same way as a none/null name, this
has been dropped in favour of a name-is-null only mechanism for such functionality. 


### Example - dot-notation
Make a selection from a structured data source using dot-notation

```yaml
env-alias:
    EXAMPLE:
        source: "https://ip-ranges.amazonaws.com/ip-ranges.json"
        selector: ".prefixes[1].ip_prefix"
```


### Example - slash-notation
Make a selection from a structured data source using slash-notation

```yaml
env-alias:
    EXAMPLE:
        source: "https://ip-ranges.amazonaws.com/ip-ranges.json"
        selector: "/prefixes[1]/ip_prefix"
```


### Example - line-number
Make a selection from a flat text file by line number only

```yaml
env-alias:
    EXAMPLE:
        source: "/proc/cpuinfo"
        selector: 5
```
