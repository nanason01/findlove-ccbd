FindLove in CCBD

Build specs / Autodeploy from source:
    These are setup to run the buildspec for each directory in a consistent manner
    If you'd like something to deploy from source, add a subdir to keep it in and a buildspec.yml in that subdir
    Then add a phase in the root buildspec.yml for that, but keep this consistent with other phases.
    Do anything unique in the buildspec.yml in your directory.
