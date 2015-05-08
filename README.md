## CS280r_Final_Project
### Title: Designing an Effective Communication and Plan Recommendation Tool for Smokejumpers
### By: Serguei Balanovich, Anastasiya Borys

### To run a simple simulation:
You can run a simple simulation from the terminal by typing
>> firesim area iters freq fire_coords fire_inten ff_coords

Where the arguments are:

area: our simulation always visualized a square plot of land, so area is the height and width of the simulation. For example, if area = 5, you will see a 5x5 simulation

iters: the number of iterations for which you want the simulation to run

freq: the frequency of the state space printouts. freq = 10 means you will see a printout at iter = 0,10,20..up to the indicated iters

fire_coords: the coordinates of where the fire is happening. An input of 0,0,2,1 would mean there is a fire happening in location (0,0) and another in location (2,1)

fire_inten: the coresponding intensities of the above described fires. Intensity varies between 0 and 1 where 1 is the most intense and 0 is a lack of fire. To indicate that the intensity of the fire in square (0,0) is .5 and in square (2,1) is .2 we would type .5, .2

ff_coords: the coordinates where we want to place one or more firefighters. For example, if we wanted to place just 1 firefighter in square (1,1) we would type in 1,1

An example input is: 
>> python firesim.py 5 50 10 0,0,2,1 .5,.2 1,1


### To run the simulation with the visual tool:
Simply run the TestApp.py file with a Kivy batch executor.

Once inside the application, select your parameters from the rigth sidebar and click Generate.

The process takes a while, especially if the selection is a large fire or an optimal configuration.

Drag the slider to see the results!


