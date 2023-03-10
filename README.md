Example of prometheus exporter for monitoring GitHub Actions Cache status.
Exports two metrics: caches count and size in bytes.
Default port is 9095.

Grouping labels are:
* branch -- exact branch name, or branch name pattern (useful for branches such as `refs/pull/<ID>/merge`);
* cache key -- exact cache key name, or key name pattern;
* repository name

'key_patterns' and 'branch_patterns' parameters can be used to group metrics by cache key names and git branch names accordingly using RegEx patterns.
See [config.yaml](config.yaml) for example.
