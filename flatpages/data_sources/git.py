from dulwich.repo import Repo
from dulwich.objects import Tree, Blob, Commit, parse_timezone
from dulwich.errors import NotGitRepository

import os
import time

class GitDataSource(object):
    """ A data source that stores all of it's data as a git repository. """

    def create(self, filename, content='', reason='', request=None):
        """ Normally, used to 'create' files before updating. However, this is
        not needed in most cases - and git is one of these cases.

        """

        self.update(filename, content, reason, request)

    def read(self, filename, request=None):
        """ Used to read the entire contents of a new file within our data
        source.

        """

        repository = _get_repository(request)

        try:
            # Basically, we need to get the latest commit in our branch. With
            # this, we have access to our git tree ID - and can then lookup
            # the blob's OID representing this filename in that tree object.
            #
            # Once we have that OID, we can get our blob object and return it's
            # contents as a raw string.

            last_commit = repository[_get_branch(request)]
            tree = repository.get_object(last_commit.tree)
            result = _find_entry_in_tree(repository, filename, tree)

            if result is not None:
                return (result[0].data, result[1])

        except KeyError:
            return None

    def update(self, filename, content, request=None, reason=''):
        """ Updates a file in our data source with the provided content. """

        repository = _get_repository(request)

        _create_file(repository, filename, content, request, reason)

        return True

    def delete(self, filename, reason='', request=None):
        """ Completely deletes the given filename from our data source. """

        repository = _get_repository(request)

        # TODO: Dulwich doesn't document deleting of objects? ARE YOU SRSLY?

def _create_commit(tree, reason='', branch=False, parents=None, request=None):
    """ Creates a new commit based on the provided information. """

    commit = Commit()

    if request and 'flatpages.git.author_name' in request.registry.settings:
        author = request.registry.settings['flatpages.git.author_name']
    else:
        author = 'Anonymous'

    if request and 'flatpages.git.author_email' in request.registry.settings:
        author_email = request.registry.settings['flatpages.git.author_email']
        author = '{0} <{1}>'.format(author, author_email)

    else:
        if request:
            author = '{0} <anonymous@{0}>'.format(request.host)
        else:
            author = '{0} <anonymous@{0}example.com>'


    # TODO: Right now, all times are in UTC time. Even though everything should
    # use UTC time in a perfect world - this isn't the case in the real world.
    commit.commit_timezone = commit.author_timezone = parse_timezone('0000')[0]
    commit.commit_time = commit.author_time = int(time.time())

    commit.author = commit.committer = author

    commit.tree = tree.id
    commit.encoding = 'UTF-8'
    commit.message = reason

    if parents:
        commit.parents = parents

    return commit

def _find_entry_in_tree(repository, identifier, tree):
    """ Finds a nearest-match entry in the given tree. This simply means that
    the file extension can be optionally ignored.

    """

    def is_dir_match(segment, entry, segments):
        """ Used to decide whether or not the given segment matches the current
        tree entry being iterated through git.

        """

        if entry[1] != segment:
            return False

        if len(segments) < 2:
            return False

        # 16384 represents the git attributes for a directory
        if entry[0] != 16384:
            return False

        return True

    def is_file_match(segment, entry, segments):
        """ Used to decide whether the given segment is a file and is a match
        for our current search criteria.

        """

        if len(segments) is not 1:
            return False

        if entry[1] == segment:
            return True

        dot_position = entry[1].rfind('.')

        if dot_position > -1 \
            and entry[1].startswith(segment) \
            and (len(segment)) == dot_position:

            return True

        return False

    def recurse_git_tree(segments, tree, full_path=[]):
        entries = tree.entries()

        for entry in entries:
            if is_dir_match(segments[0], entry, segments):
                full_path.append(segments[0])
                segments = segments[1:]

                return recurse_git_tree(segments,
                                        repository.get_object(entry[2]),
                                        full_path)

                break
 
            if is_file_match(segments[0], entry, segments):
                full_path.append(entry[1])

                full_path = os.sep.join(full_path)

                return (repository.get_object(entry[2]), full_path)

    return recurse_git_tree(identifier.split(os.sep), tree)

def _get_branch(request=None):
    if request and 'flatpages.git.branch' in request.registry.settings:
        branch = request.registry.settings['flatpages.git.branch']
    else:
        branch = 'master'

    return os.sep.join(['refs', 'heads', branch])

def _create_file(repository, filename, contents, request=None, reason=''):
    """ Creates a new blob containing 'contents' within 'repository'. """

    branch = _get_branch(request)
    blob = Blob.from_string(contents)

    try:
        last_commit = repository.get_object(repository.refs[branch])
        tree = repository.get_object(last_commit.tree)
        
        commit_parents = [repository.refs[branch]]
    except KeyError:
        tree = Tree()
        commit_parents = None

    # TODO: The dulwich documentation puts these arguments in the wrong order.
    # I should probably tell someone about this. Example here by 'tree.add':
    # http://samba.org/~jelmer/dulwich/docs/tutorial/object-store.html
    tree.add(0100644, filename, blob.id)

    commit = _create_commit(tree, reason, True, request)

    repository.refs[branch] = commit.id

    # Add our blob, followed by our tree, and finally our commit.
    for object in [blob, tree, commit]:
        repository.object_store.add_object(object)

def _populate_repository(repository, request=None):
    """ When someone creates a new repository, this goes ahead and populates it
    with any default files that exist inside of our current flatpage default
    pages directory.

    """

    # TODO: We shouldn't really use _create_file here. This generates a new
    # commit for every single file in the defaults. It would make more sense
    # for us to commit them all at once, and then tag this commit as the initial
    # commit.
    def recursively_create_files(path_suffix=''):
        """ Loops through a base path commiting any non-hidden files found
        within it or within it's subdirectories.

        """

        search_directory = os.sep.join([
            initial_page_directory,
            path_suffix
        ])

        for filename in os.listdir(search_directory):
            relative_path_to_filename = os.sep.join([
                initial_page_directory,
                path_suffix,
                filename
            ])

            if os.path.isdir(relative_path_to_filename):
                if path_suffix == '':
                    next_path_suffix = filename
                else:
                    next_path_suffix = os.sep.join([
                        path_suffix,
                        filename
                    ])

                recursively_create_files(next_path_suffix)
            else:
                create_kwargs = {}

                if path_suffix == '':
                    create_kwargs['filename'] = filename
                else:
                    create_kwargs['filename'] = os.sep.join([
                        path_suffix,
                        filename
                    ])

                file_descriptor = open(relative_path_to_filename)
                create_kwargs['contents'] = file_descriptor.read()
                file_descriptor.close()

                _create_file(repository, request=request, **create_kwargs)

    if request and 'initial_pages_directory' in request.registry.settings:
        initial_page_directory = request.registry.settings['initial_pages_directory']
    else:
        initial_page_directory = './flatpages/defaults'

    if os.path.exists(initial_page_directory):
        recursively_create_files()

def _create_repository(repository_path, request=None, bare=True):
    """ Receives a path to a (preferably non-existant) directory, and turns it
    into a git repository.
    
    """

    os.makedirs(repository_path)

    # Dulwich uses a separate method for bare instead of working repositories,
    # so we need to decide which method to use here.
    if bare: 
        init_method = Repo.init_bare
    else:
        init_method = Repo.init

    repository = init_method(repository_path)

    _populate_repository(repository, request)

    # TODO: Log entry, new repository created: {repository_path}

    return repository

def _get_repository(request=None):
    """ Gets a reference to the repository which is related to the given
    request. If a request is not provided, then it uses settings or default
    values to get the repository path.

    If the path does not exist, then this asks _create_repository to do it's
    job and then returns the result of that function instead.

    """

    # First, get the directory which will act as the parent of this repository
    if request and 'repository_root' in request.registry.settings:
        repository_root = request.registry.settings['repository_root']
    else:
        repository_root = './flatpages/git'

    # Next, get the path for this specific repository
    if request:

        if 'repository_path' in request.registry.settings:
            repository_path = request.registry.settings['repository_path']
        else:
            repository_path = request.host

    else:
        repository_path = 'default'

    # Converts repository path into: <repository_root>/<repository_path>.git
    #             Assuming '/' is the value of os.sep ^
    repository_path = os.sep.join([
        repository_root,
        repository_path + '.git',
    ])

    if not os.path.exists(repository_path):
        return _create_repository(repository_path, request)
    else:
        # We are going to try and open a repository here. If it's not a
        # a repository, then we are going to recreate the repository after
        # backing up whatever is already there.
        try:
            return Repo(repository_path)
        except NotGitRepository:
            # TODO: Renaming should probably check for overwrites.
            os.rename(repository_path, '{0}.bkp'.format(repository_path))

            return _create_repository(repository_path, request)
