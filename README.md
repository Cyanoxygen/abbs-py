# abbs-py

This script is under construction.

A simple (wrapper) script that manages AOSC ABBS repository, and its related things such as ciel instances, topics, built packages.

If you are interested, feel free to use, or just submit issues or PRs, or make your own fork.

## Basic usage

```
abbs.py subfunction command [options...] [args...]
```
<!--This command line is not gnu-ish, but it is way more readable. -->

Like apt, you can execute `abbs.py help` or `abbs help subcommand` to get more detailed usage information.

## Functions

- [ ] Manage ABBS Repository e.g. init, update, branches, etc.
- [ ] Manage Ciel instances e.g. init, load-os, update, shell, etc.
- [ ] Manage package specification files e.g. edit(open editor at the directory), etc.
- [ ] Manage built packages or build packages.
- [ ] Manage topics.

## Basic structre

```
           +---------------+
           |     main()    |
           +---------------+
                   |
           <reads conffile>
            <parsing argv>
<determine which subfunction to execute>
         <dispatcher function>
                   |
      +---------------------------+
      | dispatch() of subfunction |
      +---------------------------+
                   |
           <actual execution>
```

### `main()`

Main dispatcher.    
Loads config file, then passes control to dispatch function of respective subfunctions.  
Such subfunction is defined as a class, these classes will be loaded by calling `loadclass()`.

One exception is, if there's no other `argv`s provided or the first `arg` of `argv[]` is not in the loaded subfunctions list, program will just give out the usage information and then exit.

NOTE: if there's no config file under `~/.abbs.yml`, you are forced to config first.

### `_Conf` class

Handles configuration file.  
Loads configuration into self during `__init__()`.
If the configuration file is not found or empty, then user will be directed to setup procedure.  
This behaviour is going to be changed, since the first run should not force user to setup this program.

This object is created by `main()` and made globally accessible.

### `RepoMan`, `CielMan`, `SpecMan`, etc:

Classes which manages different compoments.  
These classes or objects will work together if user want.  

Each class have a `dispatch(self, argv)` method, this is called by `main()` after parsing arguments.

Then action will be executed by `dispatch()` after parsing arguments again.  
Please note that argument list passed to dispatch function is stripped, the first argument is deleted.

For example:

```python
# ./abbs.py ciel init

sys.argv = ['./abbs.py', 'ciel', 'init']

argv_given_by_main = ['ciel', 'init']
```

## License

This script is licensed under MIT License.

## Contribution

If you find something wrong with this script, feel free to file issues or PRs.

## Negative thinkers

Comments, advices and other meaningful things are definitely welcome. But:

If you think this is kind of dumb, I guess you are not going to use this script then. Or you may think this code is a piece of garbage, just close your browser or this tab to prevent further damage to your eyes.

More or less, if you don't like it, just ignore it. Judgement is based on everyone's concept and view, not yours. 
