#!/usr/bin/env bash
ADDRESS='aai@antavr.ru'
COPYRIGHT=''
VERSION=$(git rev-list --count HEAD).$(git rev-parse --short HEAD)
DOMAIN='aai2'
CODE='UTF-8'

DIR_SRC='src'
DIR_PO='po'
DIR_LOCALE='locale'
DIR_LOCALE="${DIR_SRC}/${DIR_LOCALE}"
FILE_POT="${DIR_PO}/${DOMAIN}.pot"

LANGS=('ru')

po2mo() {
    local FILE_PO
    local FILE_MO
    local DIR_MO

    for FILE_PO in $(find "${DIR_PO}" -maxdepth 1 -iname '*.po')
    do
        FILE_MO=$(basename "${FILE_PO}")
        DIR_MO="${DIR_LOCALE}/$(cut -d '.' -f 2 <<< "${FILE_MO}")/LC_MESSAGES"

        if [ ! -d "${DIR_MO}" ]
        then
            mkdir -p "${DIR_MO}"
        fi
        FILE_MO="${DIR_MO}/$(cut -d '.' -f 1 <<< "${FILE_MO}").mo"
        echo "make '${FILE_MO}'"
        msgfmt --output-file="${FILE_MO}" "${FILE_PO}"
    done
}

gen_pot() {
    local TEMP_FILE="$(mktemp)"

    if [ ! -d "${DIR_PO}" ]
    then
        mkdir -p "${DIR_PO}"
    fi

    find "${DIR_SRC}" -iname '*.py' >> "${TEMP_FILE}"
    echo '/usr/lib/python3.6/argparse.py' >> "${TEMP_FILE}"

    echo "make '${FILE_POT}'"
    xgettext --sort-output --default-domain="${DOMAIN}"\
            --package-name="${DOMAIN}" --package-version="${VERSION}"\
            --msgid-bugs-address="${ADDRESS}" --copyright-holder="${COPYRIGHT}"\
            --files-from="${TEMP_FILE}" --from-code="${CODE}"\
            --output="${FILE_POT}"

    rm "${TEMP_FILE}"
}

pot2po() {
    local FILE_PO
    local LANGU

    for LANGU in ${LANGS[*]}
    do
        FILE_PO="${DIR_PO}/${DOMAIN}.${LANGU}.${CODE}.po"
        if [ -f "${FILE_PO}" ]
        then
            echo "merge '${FILE_PO}'"
            msgmerge --sort-output --update --multi-domain --previous --backup=off "${FILE_PO}" "${FILE_POT}"
        else
            echo "make '${FILE_PO}'"
            msginit --no-translator --locale="${LANGU}" --input="${FILE_POT}" --output-file="${FILE_PO}"
        fi

    done
}

NO_MAKE_PO=''

while getopts m OPTION
do
    case "${OPTION}" in
        'm')
            NO_MAKE_PO='True'
            ;;
        '?')
            exit 1
            ;;
    esac
done

if [[ ! "${NO_MAKE_PO}" ]]
then
    gen_pot
    pot2po
fi

po2mo
