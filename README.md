# GitterDone
Need to accelerate your development but are stuck using a centralized source control system like P4? Look no further!

---

**gitter_done** is a set of helper scripts that allow you to interface with centralized source control systems such as Perforce, permitting you to continue following lightweight branch practices by leveraging git on top. I have been personally developing this system for the last 3 years across several projects.

**gitter_done** is better leveraged on existing P4 repositories but it can be configured when starting a repository from scratch. Refer to the correct approach in the setup steps below.

# Requirements

1. Python 3.+
2. Git 2.18+ (If you wish to apply the provided webhooks for commit compliance)

# gitter_done Setup

#### Step #1: Sync your existing source control solution to the specific CL Number you wish to start from.
If you are using Perforce follow the instruction to sync to a specific CL rather than syncing "latest" so you know your starting point.

#### Step #1: Clone the repository.
The location of the output is not important as we will move the files to an existing repository within your P4 repository.

#### Step #2: Copy the contents of the cloned repository to the root level of your project branch.
Copying to the root is highly suggested as it allows seamless integration with the repository. e.g. Lets assume the structure below is your current repository:

```
\\Root\
├── art
├── bin
│   ├── binFileA.py
│   └──  binFileB.py
├── config
├── source
├── fileA.txt
├── fileB.py
├── fileC.py
└── test
```
You should place the files so that resulting structure is as follows:
```
\\Root\
├── art
├── bin
│   ├── gitter_done
│   │   ├── GitHooks
│   │   │   └── pre-commit
│   │   ├── unit_tests
│   │   │   ├── __init__.py
│   │   │   └── test_string_utility.py
│   │   ├── __init__.py
│   │   ├── arg_parser_utility.py
│   │   ├── config.py
│   │   ├── console_utility.py
│   │   ├── external_process_utility.py
│   │   ├── ile_utility.py
│   │   ├── git_utility.pyf
│   │   ├── logging_utility.py
│   │   ├── p4_utility.py
│   │   ├── project_utility.py
│   │   ├── python_utility.py
│   │   └── string_utility.py
│   ├── binFileA.py
│   ├── binFileB.py
│   └── .pylintrc
├── .pylintrc
├── config
├── source
├── gitter_done.py
├── fileA.txt
├── fileB.py
├── fileC.py
└── test
```

#### Step #3: Populate `bin\gitter_done\config.py` with your environment details.
It is important that the following is populated accordingly:

#### Step #4: Generate a new `.gitignore` through `gitter_done.py`
After populating the Config.py with the file patterns to track and ignore you can trigger the command `py gitter_done.py -g` to auto generate a `.gitignore` file in case you prefer to track specific parts of the source. Specially helpful if your existing repository has art source and source code mixed together.

#### Step #5: Do your first commit!
All commit messages on the master branch must follow the convention: "CL _[CURRENT CL NUMBER]_" where you will populate _[CURRENT CL NUMBER]_ with the value you wrote down in Step #1.

This completes the setup steps. Now you can proceed with a normal git-flow workflow.

# Workflows
Below outlines the basic workflow myself and teams I've been part of that uses GitterDone follow to develop on a daily basis.

### Starting a new vein of work
All work starts from a new branch based off the latest version of the _master_ branch following a git-flow approach. As an example I will outline the steps we follow as if we are writing a new feature:

1. Step 1: We create a new branch via `git checkout -b feature/NameOfFeature`
2. Step 2: We modify / add the source files as we develop the feature. Committing changes as often as desired.
3. Step 3: Once we are ready to submit our changes to P4 we first
    - Check if we are up to date with master via `git fetch -a`
    - If we are behind we trigger the automated update process via `py gitter_done.py -u`
    - If we are not behind but want to update master with a new CL from P4 we trigger the automated process via `py gitter_done.py -u [RAW CL NUMBER]` e.g. `py gitter_done.py -u 123456789`
    - We merge the latest version of the master branch into our feature usually by first doing `git checkout [feature branch name]` followed by `git merge master`
    - We resolve any conflicts and commit them to the feature branch. The code is now ready to be extracted into an isolated changelist on P4 as outlined in the section below.

### Extracting changes to P4

While on the feature branch we want to get the changes out of, run `py gitter_done.py -cl` so that it extracts all the modified, added, deleted or renamed files into the default P4 changelist. Behind the scenes it goes through the git log output and parses the operations that occurred. It performs the equivalent operation on P4.

# Suggested Reading

- [Git-flow cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/#getting_started) is an excellent visual primer on what a git-flow workflow is. It is what we follow with some caveats:
    - We manually create branches following git flow naming conventions:
        - features start with `feature/`
        - bug fixes start with `bugfix/`
        - release branches we name `deliverable/[YEAR]W[WEEK#]`
    - We never merge anything INTO master. We rely on new commits via the automation for this.
    - We leave branches around as leafs. Although if you want to clean up after yourself once the chances have made it to master, go ahead.





