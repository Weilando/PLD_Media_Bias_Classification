# DKE 2021 Home Project

This repository contains the home project for the Data and Knowledge Engineering class 2021 at Heinrich Heine University.  
The project exercise can be completed at home, using the expertise and skill sets acquired in the DKE 2021 lectures.  
Use this repository to prepare your solution. 

A grade improvement of 0.3 is given when the following criteria are met:
* You provided a working solution to the problem and your results are reproducible. 
* You submitted the solution in time and in the specified format. 
* Your classification algorithm yields a reasonable performance on the classification task. Score to beat: 0.545 accuracy 
* You presented your approach to the class during the DKE 2021 lecture on 29.06.



## Topic: PLD Media Bias Classification
The home project deals with the classification of media bias of PLDs linked in tweets. I.e. given a link to e.g. a news outlet in a tweet, is this news outlet left-biased or right-biased? For this project, we will use the tweets and their metadata for classification. 

## Timeline: 
We will release the test set and evaluation script on **16.06., 11am** CEST time zone.  
Provide the source code and generated output via your Git repository **by 19.06., 3:00pm** CEST time zone.  
Present your solution (approach, results) to the class during the DKE2021 lecture on **29.06.2021** (detailed arrangements about presentations will be announced later in the lecture).

## Folder Structure:
* **input_data**:  contains the training data: one CSV file listing all PLDs with left vs. right bias classification, respectively. The test data will be added to this folder. 
* **output_data**: folder that must be populated with the results of the home project. Please export all PLDs your algorithm classifies as left-biased to a file called 'left.csv' and all PLDs it classifies as right-biased to 'right.csv'. Please refer to the task description in the assignment folder for information on the format.  
* **src**: add your code here in the suitable subfolder(s) (depending on whether you use Java or Python).
* **assignment**: contains a more detailed description of the task and the required output. 


