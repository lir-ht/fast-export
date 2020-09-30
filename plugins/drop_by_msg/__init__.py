import sys, re


def build_filter(args):
    return Filter(args)


def log(fmt, *args):
    print(fmt % args, file=sys.stderr)
    sys.stderr.flush()


class Filter:
    def __init__(self, args):
        self.pattern = re.compile(args.encode('ascii', 'strict'))
        self.remapped_parents = {}

    def commit_message_filter(self, commit_data):
        rev = commit_data['revision']
        parent_revs = commit_data['parents']

        if self.pattern.match(commit_data['desc']):
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
