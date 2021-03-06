"""
DB Benchmarking Application
===========================

Tasks.py

This file houses all of the invoke commands for the application.  This makes it
very easy for a user to quickly bring up the necessary vagrant boxes for a module
and then perform benchmarks with that module.

    Usage:
        invoke <command> [args]

"""
from __future__ import absolute_import
from __future__ import print_function

from invoke import task, run

REQUIREMENTS = 'requirements.txt'
CONDA_REQUIREMENTS = 'conda_requirements.txt'


#TODO - make a docs directory


def check_module_naming(name):
    """ Checks to see if the inputted name is in the proper format, and fixes
     it if not before returning it

    :return name: The properly formatted DB module name
    """

    if not name.endswith('db'):
        name += 'db'

    return name


@task(default=True)
def help():
    """ Returns some basic task information, much of which provided by invoke
    """

    run('invoke -l')


@task
def list_mods():
    """ Returns a list of existing modules """

    from .BenchmarkDB.main import retrieve_module_list

    mod_list = retrieve_module_list()

    print(mod_list)


@task
def benchmark(database):
    """ Executes benchmarks with the default settings for a given DB
    Usage: `invoke benchmark <database> """

    database = check_module_naming(database)

    run("python main.py {db}".format(db=database))


@task
def requirements():
    """ Pip installs all requirements, and if db arg is passed, the
    requirements for that module as well """

    run('pip install -r {req}'.format(req=REQUIREMENTS))


@task
def module_requirements(database):
    """ Installs requirements for a specific module """

    database = check_module_naming(database)

    run('cd BenchmarkDB/{db} && pip install -r {req}'.format(
        db=database,
        req=REQUIREMENTS,
    ))


def report_viewer_app():
    """ Starts the Flask app to view benchmark reports """

    cmd = 'cd BenchmarkDB && python app.py'

    run(cmd)