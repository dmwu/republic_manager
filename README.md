# republic_manager
Republic: Data Multicast Meets Hybrid Rack-Level Interconnections in Data Center

The project can be imported to IntelliJ IDEA

To compile the project, run the following command.
```
mvn package
```


To run Republic Manager, run ```./src/main/java/edu/rice/bold/server/BcdController.java``` from the IntelliJ IDEA IDE with the following argurments:
```
 -m ${REPUBLIC_MANAGER_PORT} -t ${TOR_PORT} -o ${OCS_PORT} -s -a -c -p
```


To run the EPS controller, run the following command under ```./switch_controller```.
```
ryu-manager ./quanta/ofdpa_broadcast.py ryu.app.ofctl_rest --wsapi-port ${TOR_PORT} --ofp-tcp-listen-port ${OFP_PORT}
```


To run the OCS controller, run the following command under ```./switch_controller```.
```
python ./glimmerglass/glimmerglass_controller.py --api_port ${OCS_PORT}
```