# SCANS
Simple Containerised Analysis for NMR Systems


#TODO



#building your docker image
docker build -t scans -f docker/Dockerfile .

#Running your image in a docker container
#INTERACTIVE
docker run -it -v /Users/James/Code/NMR/SCANS/TestData/600MHz_heliumlogcache.log:/root/scans/logs/helium.log -v /Users/James/Code/NMR/SCANS/TestData/rtshims.log:/root/scans/logs/shim_temp.log -v /Users/James/Code/NMR/SCANS/TestData/field.log:/root/scans/logs/field.log -v /Users/James/Code/NMR/SCANS/TestData/events.log:/root/scans/logs/events.log -v /Users/James/Code/NMR/SCANS/TestData/empty.log:/root/scans/logs/empty.log -v /Users/James/Code/NMR/SCANS/TestData/OUTPUT:/root/scans/logs/OUTPUT scans

#DETACHED
docker run -d -v /Users/James/Code/NMR/SCANS/TestData/600MHz_heliumlogcache.log:/root/scans/logs/helium.log -v /Users/James/Code/NMR/SCANS/TestData/rtshims.log:/root/scans/logs/shim_temp.log -v /Users/James/Code/NMR/SCANS/TestData/field.log:/root/scans/logs/field.log -v /Users/James/Code/NMR/SCANS/TestData/events.log:/root/scans/logs/events.log -v /Users/James/Code/NMR/SCANS/TestData/empty.log:/root/scans/logs/empty.log -v /Users/James/Code/NMR/SCANS/TestData/OUTPUT:/root/scans/logs/OUTPUT scans


#To save an image
docker save scans -o client

