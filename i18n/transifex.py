#!/usr/bin/env python
from __future__ import print_function
import sys
from polib import pofile
import argparse

from i18n.config import CONFIGURATION
from i18n.execute import execute
from i18n.extract import EDX_MARKER

TRANSIFEX_HEADER = u'edX community translations have been downloaded from {}'
TRANSIFEX_URL = 'https://www.transifex.com/projects/p/edx-platform/'


def push():
    execute('tx push -s')


def pull():
    print("Pulling languages from transifex...")
    # Pull translations from all languages where there is
    # at least 10% reviewed translations
    execute('tx pull --mode=reviewed --all')
    clean_translated_locales()

def pull_all_ltr():
    print("Pulling all translated LTR languages from transifex...")
    # these languages display right to left
    # LANGUAGES_BIDI = ("en@rtl", "he", "ar", "fa", "fa-ir", "ur")
    rtl_langs = ['he', 'ar', 'fa', 'fa_IR', 'ur']
    ltr_langs = [l for l in CONFIGURATION.translated_locales if l not in rtl_langs]
    for lang in ltr_langs:
        print ('rm -rf conf/locale/' + lang)
        execute('rm -rf conf/locale/' + lang)
        execute('tx pull -l ' + lang)

    clean_translated_locales(langs=ltr_langs)


def clean_translated_locales(langs=None):
    """
    Strips out the warning from all translated po files
    about being an English source file.
    """
    locales = CONFIGURATION.translated_locales
    if langs:
        locales = langs
    for locale in locales:
        clean_locale(locale)


def clean_locale(locale):
    """
    Strips out the warning from all of a locale's translated po files
    about being an English source file.
    Iterates over machine-generated files.
    """
    dirname = CONFIGURATION.get_messages_dir(locale)
    for filename in ('django-partial.po', 'djangojs-partial.po', 'mako.po'):
        clean_file(dirname.joinpath(filename))


def clean_file(filename):
    """
    Strips out the warning from a translated po file about being an English source file.
    Replaces warning with a note about coming from Transifex.
    """
    try:
        po = pofile(filename)
    except Exception as exc:
        # An exception can occur when a language is deleted from Transifex.
        # Don't totally fail here.
        print("Encountered error {} with filename {} - language project may no longer exist on Transifex".format(exc, filename))
        return
    if po.header.find(EDX_MARKER) != -1:
        new_header = get_new_header(po)
        new = po.header.replace(EDX_MARKER, new_header)
        po.header = new
        po.save()


def get_new_header(po):
    team = po.metadata.get('Language-Team', None)
    if not team:
        return TRANSIFEX_HEADER.format(TRANSIFEX_URL)
    else:
        return TRANSIFEX_HEADER.format(team)


if __name__ == '__main__':
    # pylint: disable=invalid-name
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="push or pull")
    parser.add_argument("--verbose", "-v")
    args = parser.parse_args()
    # pylint: enable=invalid-name

    if args.command == "push":
        push()
    elif args.command == "pull":
        pull()
    elif args.command == "ltr":
        pull_all_ltr()
        print("Now generating langugage files...")
        print('python i18n/generate.py')
        execute('python i18n/generate.py')
        print("Committing translations...")
        execute('git clean -fdX conf/locale')
        execute('git add conf/locale')
        execute('git commit --message="Updated LTR translations" --edit')
    else:
        raise Exception("unknown command ({cmd})".format(cmd=args.command))
