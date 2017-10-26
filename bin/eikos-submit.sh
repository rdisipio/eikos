#!/bin/bash

SUBMISSION_TIMESTAMP=$(date +"%Y%m%d%H%M%S")

WORKDIR=${PWD}
OUTPUTDIR=${PWD}/output

jobdir=${WORKDIR}/jobs
logdir=${WORKDIR}/logs

if [[ -z ${OUTPUTDIR} ]]
then
   outdir=${WORKDIR}/output
else
   outdir=${OUTPUTDIR}
fi

queue=8nh #CERN LXPLUS
backend=lsf #options are: lsf pbs
dryrun=0

jobname=""
configfile=UNSET

while [ $# -gt 0 ] ; do
case $1 in
    -b) backend=$2             ; shift 2;;
    -c) configfile=$2          ; shift 2;;
    -q) queue=$2               ; shift 2;;
    -j) jobname=$2             ; shift 2;;
    -d) dryrun=$2              ; shift 2;;
esac
done

if [ "$jobname" == "" ]
then
   tag=$(echo ${configfile} | rev | cut -d'/' -f1 | rev | cut -d'.' -f1 | sed -e 's/input\_//')
   jobname=eikos_${tag}
fi

# determine which backend to use
if [ "$backend" == "lsf" ]
then
   exe="bsub"
   logopts="-oe -oo"
   jobnameopts="-J"
else
   exe="qsub -V"
   logopts="-j oe -o"
   jobnameopts="-N"
fi

test -d $jobdir || mkdir -p $jobdir
test -d $logdir || mkdir -p $logdir
test -d $outdir || mkdir -p $outdir

jobfile=$jobdir/${jobname}.job.sh
logfile=$logdir/${jobname}.log

rm -fr $logfile
rm -fr $logfile.ok
rm -fr $logfile.fail

## NOW CREATE ON-THE-FLY THE SCRIPT TO BE SUBMITTED
echo job file: ${jobfile}

cat > ${jobfile} <<EOF
#!/bin/bash
echo Running on \$HOSTNAME
echo Shell: \$SHELL
echo Timestamp: $(date)

cd ${WORKDIR}

time eikos.py ${configfile}

echo "End of run"
date

EOF

# OK NOW SUBMIT THE JOB

chmod +x $jobfile

if [[ "${dryrun}" == "0" ]] 
then
  ${exe} -q $queue ${logopts} $logfile ${jobnameopts} $jobname $jobfile #${skipwn}
else
  echo "Dry run. See ${jobfile}"
fi

job_return_code=$?
if [ $job_return_code -ne 0 ]
then
  touch $logdir/${jobname}.fail
  echo Job command has failed with code=$job_return_code - quit job now...
  exit $job_return_code
else
  touch $logdir/${jobname}.ok
fi

