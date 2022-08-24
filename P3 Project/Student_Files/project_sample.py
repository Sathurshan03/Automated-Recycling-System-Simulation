import sys
sys.path.append('../')
from Common.project_library import *

# Modify the information below according to you setup and uncomment the entire section

# 1. Interface Configuration
project_identifier = 'P3B' # enter a string corresponding to P0, P2A, P2A, P3A, or P3B
ip_address = '169.254.175.14' # enter your computer's IP address
hardware = False # True when working with hardware. False when working in the simulation

# 2. Servo Table configuration
short_tower_angle = 270 # enter the value in degrees for the identification tower 
tall_tower_angle = 0 # enter the value in degrees for the classification tower
drop_tube_angle = 180#270# enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# 3. Qbot Configuration
bot_camera_angle = -21.5 # angle in degrees between -21.5 and 0

# 4. Bin Configuration
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin 

bin1_offset = 0.30 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin2_offset = 0.17
bin2_color = [0,0,1]
bin3_offset = 0.27
bin3_color = [0,1,0]
bin4_offset = 0.23
bin4_color = [0,1,1]

#--------------- DO NOT modify the information below -----------------------------

if project_identifier == 'P0':
    QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
    bot = qbot(0.1,ip_address,QLabs,None,hardware)
    
elif project_identifier in ["P2A","P2B"]:
    QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
    arm = qarm(project_identifier,ip_address,QLabs,hardware)

elif project_identifier == 'P3A':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration,None, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    
elif project_identifier == 'P3B':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    qbot_configuration = [bot_camera_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color]]
    configuration_information = [table_configuration,qbot_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bins = bins(bin_configuration)
    bot = qbot(0.1,ip_address,QLabs,bins,hardware)
    

#---------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------

import math

#Global Constants
#Bin info layout: [bin colour, bin relative distance to qbot, bin position, bin number]
BIN_ONE = [bin1_color,0.21,1,1]
BIN_TWO = [bin2_color,0.06,0,2]
BIN_THREE = [bin3_color,0.19,0,3]
BIN_FOUR = [bin4_color,0.14,1.05,4]
BIN_ATTRIBUTES = [BIN_ONE,BIN_TWO,BIN_THREE,BIN_FOUR]

#Locations constants
PICK_UP_LOCATION =[0.644,0.000,0.247]
DROP_OFF_LOCATION_1 = [0.012,-0.57,0.534]
DROP_OFF_LOCATION_2 = [0.012,-0.52,0.485]
DROP_OFF_LOCATION_3 = [0.012,-0.44,0.465]
DROP_OFF_LOCATION = [DROP_OFF_LOCATION_1, DROP_OFF_LOCATION_2, DROP_OFF_LOCATION_3]

#Wheel speed constants
WHEEL_FORWARD_SPEED = 0.15
WHEEL_FAST_SPEED = 0.03
WHEEL_SLOW_SPEED = 0.015

#IR sensor constants
BOTH_IR_DETECT = [1,1]
LEFT_IR_DETECT = [1,0]
RIGHT_IR_DETECT = [0,1]
NO_IR_DETECT = [0,0]

#Q-bot home position constants
NEAR_HOME_X_UPPER = 1.6
NEAR_HOME_X_LOWER = 1.4
NEAR_HOME_Y_UPPER = 0.1
NEAR_HOME_Y_LOWER = -0.1
X_HOME_POSITION = 1.5
Y_HOME_POSITION = -0.03

#holds info of bin that is currently on turntable while Q-bot is in motion
turntable_container = []

def dispense_container():
    #This function is to dispense the container on turtable
    #By: Tsz Wo
    
    #radomly dispense a container
    container_number = random.randint(1,6)
    container_properties = table.dispense_container(container_number,True)

    #organize the container info
    container_material = container_properties[0]
    container_mass = container_properties[1]
    container_destination = container_properties[2]

    if container_destination == "Bin01":
        bin_number = 1
    elif container_destination == "Bin02":
        bin_number = 2
    elif container_destination == "Bin03":
        bin_number = 3
    elif container_destination == "Bin04":
        bin_number = 4

    #display the results
    print("The container is made from", container_material)
    print("The container is", container_mass, "grams")
    print("The container destination bin is", container_destination)
    
    #return the container's material, mass, destination and bin number
    return container_material, container_mass, container_destination, bin_number

def load_container(containers_loaded, bin_info,is_sorting_station):
    #This function will load the containers onto the Q-bot if it meets certain criteria
    #By: Sathurshan
    #variables
    total_mass = 0
    total_containers = len(containers_loaded)

    #Add container if there are no containers on Q-bot
    if total_containers == 0:
        qarm_load(total_containers)
        containers_loaded.append(bin_info) #Add bin_info to containers_loaded to indicate container is on Q-bot
    elif total_containers < 3:
        #determine if destination bin is same as container on Q-bot
        destination_bin_container = bin_info[2]
        destination_bin_qbot = containers_loaded[0][2]
        
        if destination_bin_container == destination_bin_qbot:
            #calculates total mass
            total_mass += bin_info[1]
            for i in range (total_containers):
                total_mass += containers_loaded[i][1]

            #Load container based on if total mass less than 90 grams
            if total_mass <= 90:
                qarm_load(total_containers)
                containers_loaded.append(bin_info)
            else:
                #Total container mass exceeds 90 grams and container can not be loaded onto Q-bot
                print("Total Mass is above 90 grams")
                is_sorting_station = False
        else:
            #Container is destined to a different bin and thus can not be loaded on Q-bot
            print("This container is destined for", destination_bin_container, "Q-arm will not be loading")
            is_sorting_station = False
    else:
        #There is already 3 containers on Q-bot, thus container can not be loaded on Q-bot
        print("There is no space on Q-bot, Q-arm will not be loading")
        is_sorting_station = False

    #spacing for output
    print("\n")
    
    #Return if more containers can be loaded and a list of containers currently on Q-bot    
    return is_sorting_station,containers_loaded
            
def qarm_load(total_containers):
    #This function will control the Q-bot to load the container on the Q-bot
    #By: Tsz Wo

    print("Loading container onto Q-bot")
    
    #determine drop-off location on Q-bot based on how many containers already on Q-bot
    container_drop_off_location = DROP_OFF_LOCATION[total_containers]

    #Move Q-arm to pick up location
    time.sleep(1)
    arm.move_arm(PICK_UP_LOCATION[0],PICK_UP_LOCATION[1],PICK_UP_LOCATION[2])
    time.sleep(2)

    #GQ-arm grab the container
    arm.control_gripper(35)
    time.sleep(2)
    
    #Get Qarm out of the way of the chute
    arm.rotate_shoulder(-10)
    time.sleep(1)
    arm.rotate_elbow(15)
    time.sleep(1)
    arm.rotate_shoulder(-80)
    time.sleep(1)
    arm.rotate_base(-90)
    time.sleep(1)
    
    #drop the container off at its drop-off location on the Qbot
    arm.move_arm(container_drop_off_location[0],container_drop_off_location[1],\
                 container_drop_off_location[2])
    time.sleep(2)
    #release container and return Q-arm back to home position
    arm.control_gripper(-35)
    time.sleep(1)
    arm.rotate_shoulder(-60)
    time.sleep(1)
    arm.home()
    time.sleep(2)
    
def transfer_container(destination_bin):
    #This function will move the Q-bot until it has reached the location of the correct drop-off bin
    #By: Sathurshan
    
    #Organize destination bin's attributes
    #Destination bin index number for lists
    destination_index = destination_bin - 1
    #Destination bin distance from yellow line 
    bin_distance_lower_offset = BIN_ATTRIBUTES[destination_index][1]-0.02
    bin_distance_upper_offset = BIN_ATTRIBUTES[destination_index][1]+0.02
    #Destination bin colour
    bin_colour = BIN_ATTRIBUTES[destination_index][0]
    #Destination bin position on coordinate system
    bin_x_position_lower = BIN_ATTRIBUTES[destination_index][2] - 0.05
    bin_x_position_upper = BIN_ATTRIBUTES[destination_index][2] + 0.05
    #keeps track if bin has been found
    bin_found = False
    #Lists that holds position of bot to fix accuracy of angle
    bot_initial_position = []
    bot_finial_position =[]

    #Activate sensors
    bot.activate_ultrasonic_sensor()
    bot.activate_color_sensor()

    #Follow yellow line until destination bin has been found
    while(True):
        #Control the Q-bot to follow the yellow line until right bin is found
        #Right bing is found when the colour sensors senses the correct color of the bin and
        #the ultrasonic sensors confirms that the bin is correct by evaluating the distance of
        #bin from Qbot
        
        follow_trajectory()
        
        if bin_found == False:
            #Determine if the correct bin is located using colour sensor data
            colour_data = bot.read_color_sensor()
            
            if colour_data[0] == bin_colour:
                #Double check if correct bin is found using ultrasonic sensor
                ultrasonic_data = bot.read_ultrasonic_sensor()
                
                if ultrasonic_data >= bin_distance_lower_offset and ultrasonic_data <= bin_distance_upper_offset:
                    #bin is found if both sensors agree that it identified the bin's attributes
                    bin_found = True
                    bot_initial_position = bot.position()
        else:
            #when bin is found, accurately set the Q-bot to allign with middle of the bin
            #retrieve current x position of bot
            bot_current_position = bot.position()[0]
            
            if bot_current_position >= bin_x_position_lower and bot_current_position <= bin_x_position_upper:
                #Stop the Q-bot once it reaches the approx position
                bot.stop()
                bot_finial_position = bot.position()
                break

    #reallign the Q-bot to be parallel to yellow line
    fix_angle = allign_qbot(bot_initial_position,bot_finial_position)
    bot.rotate(-fix_angle)
    time.sleep(2)
            
    #Deactivate Sensors
    bot.deactivate_ultrasonic_sensor()
    bot.deactivate_color_sensor()
    print("Ultrasonic and Color Sensors are deactivated")

    #Return the distance Q-bot is away from bin 
    return ultrasonic_data

def follow_trajectory():
    #This function is responsible for controlling the Qbot to follow the yellow line
    #By: Tsz Wo

    #Collect data from following IR sensors
    line_following_ir_sensor = bot.line_following_sensors()
        
    #Compare IR sensors to determine which direction Q-bot should go
    if line_following_ir_sensor == BOTH_IR_DETECT:
        #if both sensors read yellow, Q-bot go forward
        bot.set_wheel_speed([WHEEL_FORWARD_SPEED,WHEEL_FORWARD_SPEED])
        
    elif line_following_ir_sensor == LEFT_IR_DETECT:
        #if only left sensors read yellow, Q-bot slows left wheel 
        bot.set_wheel_speed([WHEEL_SLOW_SPEED,WHEEL_FAST_SPEED])
        
    elif line_following_ir_sensor == RIGHT_IR_DETECT:
        #if only right sensors read yellow, Q-bot slows right wheel 
        bot.set_wheel_speed([WHEEL_FAST_SPEED,WHEEL_SLOW_SPEED])
        
    else:
        #line is lost
        print("The Q-bot has lost the line")
        
        #Attempt to find the line, if Q-bot loses line, it would not be too far from it
        #rotation of Q-bot would find the line
        angle_stepper = -2

        #Rotate Q-bot until yellow found
        while bot.line_following_sensors() != NO_IR_DETECT:
            bot.rotate(angle_stepper)
            
        print("The Q-bot has found the line")

def allign_qbot(initial_position, final_position):
    #This function will determine the angle that the q-bot is off from being perpendicular to area vector of bin surface area
    #By: Sathurshan
    
    #Retreive specific initial and final positions in x and y direction
    x_initial_position = initial_position[0]
    y_initial_position = initial_position[1]
    x_final_position = final_position[0]
    y_final_position = final_position[1]

    #calculate change in position in x and y direction
    change_in_x_position = x_final_position - x_initial_position
    change_in_y_position = y_final_position - y_initial_position

    #calculate the angle that the q-bot is off
    angle_rad = math.atan(change_in_y_position/change_in_x_position)
    angle_degrees = math.degrees(angle_rad)

    return angle_degrees

def deposit_container(distance):
    #This function will deposit the container into the bin
    #By: Sathurshan

    #variables for this function
    bin_distance = distance
    fix_distance = 0.03
    bin_depth_distance = 0.13
    angle_stepper = 10
    angle_rotate = 95.5
    angle_find_stepper = -2
    minimum_distance = 0.08

    if bin_distance <= minimum_distance:
        #if the Q-bot is close enough to the bin just deposit containers
        rotate_hopper(angle_stepper)
    else:
        #if the qbot is not close enough to the bin, it needs to get closer before depositing the containers
        bot.rotate(-angle_rotate)
        time.sleep(1)

        #measure how far Q-bot is from bin
        intial_depth = bot.depth()
        
        #Qbot goes up to bin_depth_distance m away from bin
        bot.travel_forward(bin_depth_distance)
        
        #Move Q-bot by fix distance to get even closer
        bot.forward_distance(fix_distance)

        #measure how far Q-bot is from bin
        final_depth = bot.depth()
        time.sleep(2)

        #rotate Q-bot and deposit containers into bin
        bot.rotate(angle_rotate)
        time.sleep(1)
        rotate_hopper(angle_stepper)
        
        #return back to yellow line
        bot.rotate(angle_rotate)
        bot.forward_distance(intial_depth + fix_distance - final_depth)
        bot.rotate(-angle_rotate + 15) #+15 to underestimate the angle, and let the algorythm below accurately find the line
        
        #Algorythm to find yellow line once Q-bot is in near yellow line
        while True:
            line_following_ir_sensor = bot.line_following_sensors()
            if line_following_ir_sensor == BOTH_IR_DETECT:
                #Q-bot found yellow line 
                break
            else:
                #rotate until the line is found
                bot.rotate(angle_find_stepper)
                
        
def rotate_hopper(angle_stepper):
    #This function will rotate the hopper that will dispense containers into bins without missing
    #By: Sathurshan
    
    bot.activate_stepper_motor()
    max_angle = 90
    angle = 0

    #Rotate the hopper by a angle stepper each time until max angle is reached
    for angle in range (0,max_angle,angle_stepper):
        bot.rotate_hopper(angle + 10)
        time.sleep(1)

    #return hopper to home position
    bot.rotate_hopper(0)
    bot.deactivate_stepper_motor()
            
def return_home():
    #This function will return the qbot back to the home position
    #By: Sathurshan
    
    angle = 96
    
    #follow trajectory until relatively near by home position
    while(True):
        follow_trajectory()
        bot_current_position = bot.position()
        if bot_current_position[0] >= NEAR_HOME_X_LOWER and bot_current_position[0] <= NEAR_HOME_X_UPPER and\
           bot_current_position[1] >= NEAR_HOME_Y_LOWER and bot_current_position[1] <= NEAR_HOME_Y_UPPER:
            #Q-bot is very near home position
            break

    #Reallign Q-bot to be parallel with yellow line
    bot.forward_distance(0.02) #move forward by a little to grab final position to calculate angle
    bot_finial_position = bot.position()
    fixed_angle = 90 - (allign_qbot(bot_current_position, bot_finial_position))
    bot.rotate(fixed_angle)
    time.sleep(2)

    #Exact home position is [1.5,0]
    #Fix home y positioning to be accurate
    if bot_current_position[1] < Y_HOME_POSITION:
        #calculate y distance it is away from exact home position
        distance = abs(Y_HOME_POSITION - bot_current_position[1])
        bot.forward_distance(distance)

    if bot_current_position[0] < X_HOME_POSITION:
        bot.rotate(-angle)
        time.sleep(1)
        #calculate x distance it is away from exact home position
        distance = abs(X_HOME_POSITION - bot_current_position[0])
        bot.forward_distance(distance)
        time.sleep(2)
        bot_current_position = bot.position()
        bot.rotate(angle+1)
        time.sleep(1)

def system_exit():
    #After one cycle, determines if user wants to end program or continue
    #By: Tsz Wo
    
    while True:
        command = input("Please enter command: ")

        #For ending program
        if command == "command_exit":
            print("Stopping System")
            sys.exit()

        #for continuing program
        elif command == "command_continue":
            print("Running system for another round")
            break

        #for invalid input
        else:
            print("Sorry, invlaid command, please try again")

def main(container_turntable):
    #This is the main function that calls all the necessary functions to run the whole system
    #By: Sathurshan
    #spacing in output
    print("\n")

    #Containers_loaded will keep track of containers that are currently on Q-bot
    containers_loaded = []
    bin_info = []
    container_on_turntable = []
    is_sorting_station = True

    #This will load the container if there is initially a container on turntable before dispensing. This is used for after
    #first cycle as there will always be a container on the turntable after the Q-bot leaves to dump containers in the
    #first cycle
    if len(container_turntable) != 0:
        #load container onto Q-bot 
        is_sorting_station,containers_loaded = load_container(containers_loaded,container_turntable[0],is_sorting_station)
        container_turntable.clear()

    #dispense containers and load onto Q-bot if conditions are met
    while is_sorting_station:
        #dispense a container and retreive the container's info
        material,mass,destination,bin_number = dispense_container()
        
        #organize container's info into a list 
        bin_info = [material, mass, destination, bin_number]

        #Load container onto Q-bot if conditions are met, return variable (is_sorting_station) determines if 
        #more containers can be placed onto Q-bot and returns a list of containers currently on Q-bot
        is_sorting_station,containers_loaded = load_container(containers_loaded,bin_info,is_sorting_station)

    #Put the container currently on turntable onto a temporary list
    container_on_turntable.append(bin_info)

    #transfer Q-bot to destination bin, return's bin distance from the Q-bot
    destination_bin = containers_loaded[0][3]
    bin_distance = transfer_container(destination_bin)

    #Deposit the containers into the bin
    deposit_container(bin_distance)

    #return back to home position
    return_home()

    system_exit()

    return container_on_turntable

while True:
    #runs one cycle of the system, return value is container info on the turntable
    turntable_container = main(turntable_container)


#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------

