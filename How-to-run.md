By Zak Micallef:

Ideally should be run on Linux. Mac seems to introduce random issues. 

On UPISAS
 - Create local venv
 - pip install requirments.txt -> Optuna was added

For SWITCH
 - docker-compose build backend
 - docker-compose up -d

In order to run an experiment: 
 1. Make sure that at least frontend, elasticsearch and kibana are running on docker. 
 2. In the UPISAS root folder run 'sh run.sh'
 3. Make sure the backend is fully up and no longer "waiting for Kibana server".
 3. Go to http://localhost:3000/ and hit refresh to load the models.
 4. Press the Enter key when prompted to do so and the experiment should start

 - This will deploy the backend docker container, connect it to the elk network, upload the dataset found under the upload folder and start monitering metrics of switch
 - Once the run is done, a run.csv file is created on the root directory with all the values. 
 - If you want to run the baseline, update the run.sh and uncomment the previous command. 

