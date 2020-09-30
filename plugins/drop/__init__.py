import sys


def build_filter(args):
    return Filter(args)


def log(fmt, *args):
    print(fmt % args, file=sys.stderr)
    sys.stderr.flush()


class Filter:
    def __init__(self, args):
        self.unresolved_hashes = {arg.encode('ascii', 'strict')
                                  for arg in args.split(',')}
        self.remapped_parents = {}
        self.processed_parents = set()

    def commit_message_filter(self, commit_data):
        hg_hash = commit_data['hg_hash']
        rev = commit_data['revision']
        parent_revs = commit_data['parents']

        if hg_hash in self.unresolved_hashes:
            if rev in self.processed_parents:
                raise Exception('Processed %i before resolving hash' % rev)
            self.remapped_parents[rev] = parent_revs
            self.unresolved_hashes.remove(hg_hash)
            log('Resolved hash to drop: %s -> %i', hg_hash, rev)

        self.processed_parents.update(parent_revs)

        mapping = self.remapped_parents
        parent_revs = [rp for p in parent_revs for rp in mapping.get(p, [p])]
        commit_data['parents'] = parent_revs
