## Drop commits from output

To use the plugin, add the command line flag `--plugin drop=<spec>`.
The flag can be given multiple times to drop more than one commit.

The <spec> value can be either

 - a hg hash in the full form (40 hexadecimal characters) to drop a
   the corresponding changeset, or

 - a regular expression pattern to drop all matching changesets.
