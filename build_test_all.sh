pip uninstall datapi -y 
pip install -e . --no-cache-dir
rm -Rf test
datapi init test
cd test
datapi show 
datapi run --all
cd ..
cd datapi/examples
python python_client.py --project_id velascoluis-dev-sandbox --region us-central1 --resource_name sample-resource-projection
python python_client.py --project_id velascoluis-dev-sandbox --region us-central1 --resource_name sample-resource-reduction
python python_client.py --project_id velascoluis-dev-sandbox --region us-central1 --resource_name sample-resource-depends-datapod
cd ../../test
datapi show 
datapi docs generate --all
datapi docs serve