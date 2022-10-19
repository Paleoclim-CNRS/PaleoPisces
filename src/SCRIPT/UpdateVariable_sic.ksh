#!/bin/bash

set -x

dir=
file_t=
file_icemod=

chmod -R u+rw ${dir}/${file_t}

ncrename -v siconc,old_siconc ${dir}/${file_t}
ncks -A -v sic ${dir}/${file_icemod} ${dir}/${file_t}
ncrename -v sic,siconc ${dir}/${file_t}
