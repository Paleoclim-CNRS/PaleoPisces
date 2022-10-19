#!/bin/bash

set -x

dir=
file_w=
meshfile=

chmod -R u+rw ${dir}/${file_w}

cp ${dir}/${file_w} ${dir}/tmp1.nc 
rm -f ${dir}/${file_w}

ncks -A -v e1t,e2t ${dir}/${meshfile} ${dir}/tmp1.nc

ncwa -O -a t ${dir}/tmp1.nc ${dir}/tmp2.nc
rm -f ${dir}/tmp1.nc

ncap2 -s 'wocetr_eff=e1t*e2t*wo' ${dir}/tmp2.nc ${dir}/tmp1.nc
rm -f ${dir}/tmp2.nc

ncks -x -v e1t,e2t ${dir}/tmp1.nc ${dir}/tmp2.nc
rm -f ${dir}/tmp1.nc

ncap2 -s 'wocetr_eff=float(wocetr_eff)' ${dir}/tmp2.nc ${dir}/${file_w}
rm -f ${dir}/tmp2.nc

ncatted -Oh -a units,wocetr_eff,c,c,"m3/s" \
            -a long_name,wocetr_eff,c,c,"effective ocean vertical transport" \
            -a online_operation,wocetr_eff,c,c,"Recalculated from mesh_mask variables e1t and e2t and grid_W variable wo. See OPA_SRC/TRA/traadv.F90" \
            -a missing_value,wocetr_eff,c,f,1.e+20 \
            -a coordinates,wocetr_eff,c,c,"time_counter depthw nav_lat nav_lon" \
            ${dir}/${file_w}

