import sys, re


def build_filter(args):
    if re.fullmatch(r"([A-Fa-f0-9]{40}(,|$))+", args):
        return RevisionIdFilter(args.split(","))
    else:
        return DescriptionFilter(args)


def log(fmt, *args):
    print(fmt % args, file=sys.stderr)
    sys.stderr.flush()


# TODO:
#
# * Testa att droppa flera commits i rad.
#   Måste parents skrivas om rekursivt?
#
# * Skriv tester?
#
# * Flytta samtliga borttagna commits till en ny branch?
#   Använd id(Filter) i namnet för unikhet?


class FilterBase:
    def __init__(self):
        self.remapped_parents = {}

    def commit_message_filter(self, commit_data):
        rev = commit_data['revision']
        parent_revs = commit_data['parents']

        if self.should_drop_commit(commit_data):
            log('Dropping revision %i.', rev)

            self.remapped_parents[rev] = parent_revs

            # Head commits cannot be dropped because they have no
            # children, so detach them to a separate branch.
            commit_data['branch'] = b'dropped-hg-head'
            commit_data['parents'] = []

        mapping = self.remapped_parents
        if any(p in mapping for p in parent_revs):
            commit_data['parents'] = [rp for p in parent_revs
                                      for rp in mapping.get(p, [p])]

    def should_drop_commit(self, commit_data):
        return False


class RevisionIdFilter(FilterBase):
    def __init__(self, revision_hash_list):
        super().__init__()
        self.unresolved_hashes = {h.encode('ascii', 'strict')
                                  for h in revision_hash_list}

    def should_drop_commit(self, commit_data):
        return commit_data['hg_hash'] in self.unresolved_hashes


class DescriptionFilter(FilterBase):
    def __init__(self, pattern):
        super().__init__()
        self.pattern = re.compile(pattern.encode('ascii', 'strict'))

    def should_drop_commit(self, commit_data):
        return self.pattern.match(commit_data['desc'])
