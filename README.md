# Cloud_Computing_Project2020
Implementing A Rideshare App


Steps To Run:-

Assignment - 1:
 - python setup_db.py
 - python rideshare.py
 - Run "python db_print.py" To see contents of the database

Assignment - 2:
 - sudo docker-compose build
 - sudo docker-compose up

Assignment - 3:
    1. Change the IP Addresses in Code to Coressponding IPs So that Cross-Container Requests Are Successful.
        Current IP:
            Users: 52.3.109.219
            Rides: 54.164.213.19
            Load Balancer: cc-ass-3-678167101.us-east-1.elb.amazonaws.com

    2. In Rides and Users folder (In their VMs):
        - sudo docker-compose build
        - sudo docker-compose up

Final Project:
    1. Change the IP Addresses in Code to Coressponding IPs So that Cross-Container Requests Are Successful.
        Current IP:
            Users: 52.3.109.219
            Rides: 54.164.213.19
            Orchestrator: 54.90.15.252
            Load Balancer: cc-ass-3-678167101.us-east-1.elb.amazonaws.com

    2. In Rides and Users folder (In their VMs):
        - sudo docker-compose build
        - sudo docker-compose up

    3. In Orchestrator folder:
        - sudo docker-compose build
        - sudo docker build -t worker ./worker
        - sudo python3 host.py #In another terminal
        - sudo docker-compose up
_________________________________________

Project Setup:

The Project contains three EC2 instances containing the corresponding containers:
1. Users
    - users container
2. Rides
    - rides container
3. Orchestrator
    - rabbitmq
    - zookeeper
    - orchestrator
    - worker( master )
    - worker( slave )       #Both master and slave have same image.

It also contains a load balancer to distribute incoming requests to Users and Rides VMs.
The Users and Rides VMs send all db-read and db-write requests to the Orchestrator VM which implements a DBaaS.
All db requests are recieved by the orchestrator container which forwards them to master and slave containers using RabbitMQ.

_______________________________________

