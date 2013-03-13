#!/bin/bash

oicdir=$(dirname $0)

while getopts "m:" OPTION
do
	case "$OPTION" in
		m)
			modules="-m ${OPTARG}"
			;;
	esac
done

shift $((OPTIND - 1))

tmp_file=$(mktemp --tmpdir="${oicdir}" tmp-XXXXX.json)
if [ -z "${tmp_file}" ]; then
	exit 255
fi

trap "{ rm -f \"${tmp_file}\"; }" EXIT
trap "{ echo 'Test aborted'; exit 255; }" SIGHUP SIGTERM

python "${oicdir}"/test/oauth2/server_test.py > "${tmp_file}"

"${oicdir}"/path_run.sh python ${modules} "${oicdir}"/script/oauth2c.py -J "${tmp_file}" $@
