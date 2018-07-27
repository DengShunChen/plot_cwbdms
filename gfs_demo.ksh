#!/bin/ksh

#dtg=2018072100
dtg=`date -u --date="6 hours ago" +%Y%m%d%H`

local_path="/nwpr/gfs/xb80/data2/projects/python_plot/plot_dms"
python="/nwpr/gfs/xb80/data2/Anaconda/bin/python"

levlist='500 850'
varlist='000 100'
taulist='0 6 12 18 24 30 36 42 48 54 60 66 72 78 84 90 96 102 108 114 120 126 132 138 144 150 156 162 168 174 180 186 192' 

cd ${local_path}

for lev in ${levlist} ; do 
for var in ${varlist} ; do
  ${python} ${local_path}/plot_dms.py -x NWPDB -b ${dtg} -v ${var} -k  ${lev}  -t ${taulist} -a /nwp/ncsagfs/.DMSDATA
  convert -delay 30 -loop 0 NWPDB_${lev}${var}_f*.png NWPDB_${lev}${var}.gif
  scp ${local_path}/NWPDB_${lev}${var}.gif rdc25:/home/xb80/web/html
done
done

var='010'
lev='SSL'

taulist1={0..24}
taulist2={25..48}
taulist3={49..72}
taulist4={73..96}
taulist5={97..120}
taulist6={121..144}
taulist7={145..168}

${python} ${local_path}/plot_slp.py -x NWPDB -b ${dtg} -v ${var} -k  ${lev}  -t ${taulist1} -a /nwp/ncsagfs/.DMSDATA &
${python} ${local_path}/plot_slp.py -x NWPDB -b ${dtg} -v ${var} -k  ${lev}  -t ${taulist2} -a /nwp/ncsagfs/.DMSDATA &
${python} ${local_path}/plot_slp.py -x NWPDB -b ${dtg} -v ${var} -k  ${lev}  -t ${taulist3} -a /nwp/ncsagfs/.DMSDATA &
${python} ${local_path}/plot_slp.py -x NWPDB -b ${dtg} -v ${var} -k  ${lev}  -t ${taulist4} -a /nwp/ncsagfs/.DMSDATA &
${python} ${local_path}/plot_slp.py -x NWPDB -b ${dtg} -v ${var} -k  ${lev}  -t ${taulist5} -a /nwp/ncsagfs/.DMSDATA &
${python} ${local_path}/plot_slp.py -x NWPDB -b ${dtg} -v ${var} -k  ${lev}  -t ${taulist6} -a /nwp/ncsagfs/.DMSDATA &
${python} ${local_path}/plot_slp.py -x NWPDB -b ${dtg} -v ${var} -k  ${lev}  -t ${taulist7} -a /nwp/ncsagfs/.DMSDATA &

waiting=999
while [[  ${waiting} -gt 1 ]] ; do
  sleep 5
  waiting=`/bin/ps -F | grep plot_slp | wc -l`
  echo "Waiting : ${waiting}"
done

/usr/bin/convert -delay 10 -loop 0 NWPDB_${lev}${var}_f*.png NWPDB_${lev}${var}.gif
/usr/bin/scp ${local_path}/NWPDB_${lev}${var}.gif rdc25:/home/xb80/web/html

