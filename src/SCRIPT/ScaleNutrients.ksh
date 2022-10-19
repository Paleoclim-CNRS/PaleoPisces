#!/bin/bash
#
set -x

dir=
file_prefix=

# Part 1 = Create your files for a reference/Modern budget of nutrients

ncks -A -v nav_lon,nav_lat,NO3 ${dir}/${file_prefix}_ptrc_T.nc ${dir}/${file_prefix}_NO3.nc
ncks -A -v nav_lon,nav_lat,PO4 ${dir}/${file_prefix}_ptrc_T.nc ${dir}/${file_prefix}_PO4.nc
ncks -A -v nav_lon,nav_lat,Si ${dir}/${file_prefix}_ptrc_T.nc ${dir}/${file_prefix}_Si.nc
ncks -A -v nav_lon,nav_lat,DIC ${dir}/${file_prefix}_ptrc_T.nc ${dir}/${file_prefix}_DIC.nc
ncks -A -v nav_lon,nav_lat,Alkalini ${dir}/${file_prefix}_ptrc_T.nc ${dir}/${file_prefix}_Alk.nc
ncks -A -v nav_lon,nav_lat,DOC ${dir}/${file_prefix}_ptrc_T.nc ${dir}/${file_prefix}_DOC.nc
ncks -A -v nav_lon,nav_lat,Fer ${dir}/${file_prefix}_ptrc_T.nc ${dir}/${file_prefix}_Fer.nc
ncks -A -v nav_lon,nav_lat,O2 ${dir}/${file_prefix}_ptrc_T.nc ${dir}/${file_prefix}_O2.nc
ncap2 -s 'O2=O2/44.66' ${dir}/${file_prefix}_O2.nc ${dir}/${file_prefix}_O2_Unit.nc

