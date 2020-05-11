RideShare on AmazonAWS
During this semester for the cloud computing course, you will develop the backend for a
cloud based RideShare application, that can be used to pool rides.
The RideShare application allows the users to create a new ride if they are travelling from
point A to point B. The application should be able to
* Add a new user
* Delete an existing user
* Create a new Ride
* Search for an existing ride between a source and a destination
* Join an existing ride
* Delete a ride


The entire application will be deployed on Amazon Web Services using the AWS educate
starter account preloaded with $75 of credit that has been provided to you.
Scope of Assignment 1
For this assignment, you should complete the backend processing of RideShare using REST
APIs on the AWS instance. There is no need to create any Front End.
When creating items on the AWS instance, you can store it in any database of your choice.
This part will be addressed in further assignments. You need not necessarily need to store
it on a database too. It is enough to store this somehow on the filesystem in whatever
format you want.
Deliverables
1. Each one of the APIs given below must be implemented with proper status codes
2. These APIs must be exposed on the public IP address, so that we can run a test
script to test for correctness of the functioning of the API. Hence it is important that
you must stick to the specification. Major focus of the credits must be on this.
3. Please submit a one page report based on the template. (Template will be shared at
a later date)


Marks: 10
Due Date: Feb 1, 2020
Evaluation Criteria
- APIs with proper HTTP status codes (8 marks)
- Deployed on AWS with a static IP on port 80 (1 mark)
- Over and above specification like deploying over a reverse proxy and app server,
automated testing, load testing etc (1 mark)
RideShare: REST API specification
* For each API endpoint, the Response body (sent by you) must be in the corresponding
JSON format
* For each API endpoint, the Request body (sent by testing suite) will be in the
corresponding JSON format
* From the list of relevant HTTP response codes, you must decide which one to send for a
given request body. All response codes given for each endpoint will be tested against by
the suite. Response codes are for both success and failure cases.
* You must implement the APIs using the given endpoints.
* Note that below, {} represents a JSON associate map and [] represents a JSON
array.
* Do not assume a max size for any array, string, number. Use appropriate data structures
in your backend for this. We may test against your APIs with extremely long
strings/numbers.
* The “source” and “destination” fields are enums, corresponding to the different localities
in Bangalore. Hence they will be integers in the HTTP Requests. The enum of the
localities will be shared with you.
* The last two APIs don’t have any strict specification, all the db operations must happen
through those APIs. Do not embed any db operations directly in any other API. This is
needed for further assignments. Use the last two APIs in all the other APIs to perform
any db operation.
* You can use any backend framework in any programming language. Eg. flask, django,
Nodejs, Go, Spring Boot etc.
* You can use any database. Eg PostgreSQL,MySQL, MongoDB, sqlite, etc
* The last two APIs are going to be further expanded in upcoming assignments, for now
ensure that all database requests go through those two queries only
