# TESTS="$(python ./scripts/eachdist.py list --instrumentation)"
TESTS="$(ls instrumentation/)"

TESTS=(${TESTS//|/ })
MATRIX="[{\"test\":\"exporter\"},{\"test\":\"sdkextension\"},{\"test\":\"propagator\"}"
curr=""
for i in "${!TESTS[@]}"; do
    curr="${TESTS[$i]}"
    MATRIX+=",{\"test\":\"$curr\"}"
done
MATRIX+="]}"
echo "::set-output name=matrix::$MATRIX"