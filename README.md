# agol_pub_livexyz

Publish [LiveXYZ](https://www.livexyz.com/) data to the NYCMaps ArcGIS Online organization.

### You will need

1. ArcGIS Pro 3.5+ installed (ie python _import_ _arcgis_)
2. API key to [LiveXYZ](https://www.livexyz.com/)
3. To publish, authentication to an ArcGIS Online organization 
4. The [agol_pub](https://github.com/mattyschell/agol_pub) repository

### Download LiveXYZ Data

We fetch all data, including historical records, and sort them into views when when publishing. 

#### Download All

1. Copy sample-fetchlivexyz-all.bat to a new name.  
2. Get a key from [LiveXYZ](https://directory.livexyz.com/places).  
3. Update the environmentals at the top of the script.

#### Download A Sample

The full dataset can be a lot to deal with. To fetch a smaller chunk of data:

1. Copy sample-fetchlivexyz-specimen.bat to a new name
2. Get a key from [LiveXYZ](https://directory.livexyz.com/places).
3. Update the environmentals LINESPERPAGE and TOTALPAGES to control the specimen size. For example 5 and 5 respectively will yield 25 rows.
4. Update the other environmentals

### ArcGIS Online: The Tentative Plan

![ArcGIS Online tentative plan](doc/sketch.png)





