"""Config file for the Git<->P4 command line automation interface script.

Attributes:
    DEFAULT_REMOTE_NAME (str): The name convention used for the remote if
        different than standard.
    GITIGNORE_FILENAME (string): name of the .gitignore file if different
        than default.
    TRUNK_BRANCH_NAME (str): The name of the branch which is in sync with P4.
    IGNORED_P4_FILE_LIST (list): A list of file paths that should be ignored by
        P4 when building the change lists if they show modifications.
    FORCED_SYNC_WISHLIST (list): A list of file paths containing the files and
        folders we want to forcefully sync via our automation.
    GIT_FILE_WISHLIST (list): A list of file paths containing the files and
        folders we actually want to track in git.
    GIT_FILE_IGNORE_LIST (list): A list of file paths containing the files and
        and folders we want to absolutely ignore in git.

"""
# ----------------------------------
# GLOBALS

# TOKENS
DEFAULT_REMOTE_NAME = 'remotes/origin'

GITIGNORE_FILENAME = ".gitignore"

TRUNK_BRANCH_NAME = "master"

IGNORED_P4_FILE_LIST = [
    ".gitignore",
    "bin/GitterDone/Config.py",
]

FORCED_SYNC_WISHLIST = [
]

"""
    The wishlist:
    Contains a list of directories and files that SHOULD NOT be ignored.
    NOTES:
    - Ensure that there is a comma following every entry.
    - Do not add the trailing slash if the path points to a directory.
    - If you don't want it to track child folders add /* suffix to the entry.
"""
GIT_FILE_WISHLIST = [
    # Example:
    # "source/foo.bar",
    "bin/GitterDone",
    "GitterDone.py",
    "license",
    "readme.md",
]

"""
    List of patterns to ignore based on the following conventions:
        - Entries with trailing slash: DIRECTORY ignore.
        - Entries with wildcard asterisks: Wildcard ignore.
    NOTE: Example below should cover any project using C#, C++ & python
"""
GIT_FILE_IGNORE_LIST = [
    "*$py.class",
    "**/packages/*",
    "*.[Dd][Ss]_[Ss]tore",
    "*.[Pp]ython",
    "*.a",
    "*.abc",
    "*.acm",
    "*.app",
    "*.appxmanifest",
    "*.aps",
    "*.atn",
    "*.bin",
    "*.Cache",
    "*.cachefile",
    "*.com",
    "*.config*",
    "*.cover",
    "*.csproj.user",
    "*.csv",
    "*.d",
    "*.dat",
    "*.dbmdl",
    "*.dll",
    "*.dylib",
    "*.egg",
    "*.egg-info/",
    "*.exe",
    "*.export",
    "*.gch",
    "*.git",
    "*.hkt",
    "*.ilk",
    "*.img",
    "*.jpeg",
    "*.la",
    "*.lai",
    "*.lastbuildstate",
    "*.lib",
    "*.lo",
    "*.log",
    "*.ma",
    "*.manifest",
    "*.mel",
    "*.met",
    "*.meta",
    "*.mo",
    "*.mod",
    "*.mp3",
    "*.mp4",
    "*.ncb",
    "*.nupkg",
    "*.o",
    "*.obj",
    "*.opensdf",
    "*.orig",
    "*.out",
    "*.p7s",
    "*.pch",
    "*.pdb",
    "*.pfx",
    "*.pgc",
    "*.pgd",
    "*.pid",
    "*.pidb",
    "*.png",
    "*.pot",
    "*.pri",
    "*.props",
    "*.psess",
    "*.publishsettings",
    "*.py[cod]",
    "*.rc",
    "*.rsp",
    "*.runsettings",
    "*.sbr",
    "*.scc",
    "*.sdf",
    "*.slo",
    "*.smod",
    "*.so",
    "*.spec",
    "*.sql",
    "*.sqlproj",
    "*.targets",
    "*.tif",
    "*.tlb",
    "*.tlh",
    "*.tli",
    "*.tmp",
    "*.tmp_proj",
    "*.txt",
    "*.user",
    "*.vs*",
    "*.wpr",
    "*.wtl",
    "*.xex",
    "*[Pp]ublish.xml",
    "*[Rr]e[Ss]harper",
    "*_2015.vcxproj*",
    "*_i.c",
    "*_ispc.h",
    "*_p.c"
    "*_p.c",
    "*ipch/",
    "*NuGetPackages*",
    "*SchemaTypeInfo.h",
    "*x64/",
    "*~*",
    ".build",
    ".builds",
    ".cache",
    ".coverage",
    ".coverage.*",
    ".eggs/",
    ".env",
    ".hypothesis/",
    ".installed.cfg",
    ".mypy_cache/",
    ".p4*",
    ".pytest_cache/",
    ".ropeproject",
    ".spyderproject",
    ".spyproject",
    ".tox/",
    ".venv",
    ".vscode/",
    ".webassets-cache",
    "/*.log",
    "/*.txt",
    "/*init.txt",
    "/[Bb]uild*",
    "/Automation*",
    "/deploy*",
    "/site",
    "/temp*",
    "[Dd]ebug/",
    "[Dd]ebug_2015/",
    "[Dd]ebug_2017/",
    "[Oo]bj/",
    "[Rr]elease/",
    "[Rr]elease_2015/",
    "[Rr]elease_2017/",
    "[Ss]tyle[Cc]op.*",
    "_ReSharper*/",
    "coverage.xml",
    "db.sqlite3",
    "Desktop.ini",
    "develop-eggs/",
    "dist/",
    "downloads/",
    "eggs/",
    "ehthumbs.db",
    "env.bak/",
    "env/",
    "error_snapshot",
    "Generated/",
    "GitterDoneLogs",
    "htmlcov/",
    "instance/",
    "lib/",
    "lib64/",
    "local_settings.py",
    "MANIFEST",
    "nosetests.xml",
    "parts/",
    "pip-delete-this-directory.txt",
    "pip-log.txt",
    "reports/",
    "sdist/",
    "Settings.StyleCop",
    "Temp",
    "Thumbs.db",
    "venv.bak/",
    "venv/",
    "x64_v*",
]


# ----------------------------------
# FUNCTIONS

def get_git_ignore_filename():
    """
    Get the git ignore filename string. (Generated results output).

    Returns:
        str: Name of the git ignore file. (default=".gitignore")

    """
    return GITIGNORE_FILENAME


def get_p4_ignore_wishlist():
    """
    Get a list of files that should be ignored by P4.

    Returns:
        list: List containing patterns to be ignored by P4 when generating
            changelists.

    """
    return IGNORED_P4_FILE_LIST


def get_git_ignore_desired_path_wishlist():
    """
    Get a string list with the paths/files that we want to not ignore in Git.

    Returns:
        list: List containing all the files to include in the gitignore.

    """
    if GITIGNORE_FILENAME in GIT_FILE_WISHLIST:
        return GIT_FILE_WISHLIST

    extended_list = GIT_FILE_WISHLIST
    extended_list.append(GITIGNORE_FILENAME)
    return extended_list


def get_git_ignore_ignored_path_wishlist():
    """
    Get a string list with the pattern tokens that Git should ignore.

    Returns:
        list: List containing all the files to forcefully ignore in git.

    """
    return GIT_FILE_IGNORE_LIST


def get_forced_sync_path_wishlist():
    """
    Get a string list with the patterns that should be forcefully synced in P4.

    Returns:
        list: List containing all the patterns to forcefully sync.

    """
    return FORCED_SYNC_WISHLIST


def get_trunk_branch_name():
    """Get the name of the trunk branch.

    Returns:
        str: The name of the trunk branch.

    """
    return TRUNK_BRANCH_NAME


def get_default_remote_name():
    """Get the default remote name being used.

    Returns:
        str: The name of the remote branch being used.

    """
    return DEFAULT_REMOTE_NAME
