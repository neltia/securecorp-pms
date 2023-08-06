#!/bin/bash

# main directory path
service_name="securecorp-pms"
current_path=`pwd -P`

# current date path
today=$(date "+%Y%m%d")
back_dir="${service_name}_back_${today}"

# is exists path
if [ -d "${back_dir}" ] ; then
  rm -rf "${back_dir}"
fi

mv "${service_name}" "${back_dir}"

git clone https://github.com/neltia/securecorp-pms.git

cd "${service_name}"
cp -r "${current_path}/.config_secret" "${current_path}/${service_name}/app/"
