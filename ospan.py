# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 10:28:46 2019

@author: linda
"""

from __future__ import division

# Import libraries
import expyriment
import os
import shutil
import sys
import random as rnd
import re

# SET BEFORE THE EXPERIMENT
#------------------------------------------------------------------------------
TESTING = 0 # 1 or 0

# Settings
WHICH_RUN = sys.argv[1] #argument via terminal [example: ospan.py run1]
REFRESH_RATE = 60  # In Hz
WINDOW_SIZE = 1280,1040
frame = 1000 / REFRESH_RATE
font_size=30
text_pos=-200

# TESTING
#------------------------------------------------------------------------------
# When testing
if TESTING == 1:
    expyriment.control.set_develop_mode()                                       # create small screen
    speedup = 1                                                                 # if set at 1 it is normal duration
else:    
    speedup = 1 

# TASK SETTINGS
#------------------------------------------------------------------------------

# Create experimental task
task = expyriment.design.Experiment(name= "Operation Span Task", background_colour = (125,125,125))  

# Initialize screen
expyriment.control.initialize(task)

# Name log events
task.add_data_variable_names([WHICH_RUN,"Presentation","time","operation","solution","response","correct","RT"])

# Keyboard settings
keys = expyriment.io.Keyboard()
keys.set_quit_key(expyriment.misc.constants.K_ESCAPE)#with esc you can quit
experimenterkey=expyriment.misc.constants.K_5
responsekeys = [expyriment.misc.constants.K_LEFT,expyriment.misc.constants.K_RIGHT]

# Create operations
frst_operations=[]
operations=[]
frst_solution=[]
scnd_solution=[]
scnd_wrong=[]
notgreater=16

# Loop over all possible operations
for c_sig in ["/","*"]:
    
    for c_val1 in range(1,10):
        
        for c_val2 in range(1,10):  
            
            getoperation=True
            
            #only whole numbers
            if (float(eval(str(c_val1)+c_sig+str(c_val2)))).is_integer()==False:
                getoperation=False
           
            #not greater than 16
            if float(eval(str(c_val1)+c_sig+str(c_val2)))>notgreater:
                getoperation=False
            
            #no ones...?
            if c_val2==1 and c_sig=="*":
                getoperation=False
            
            #form the operations
            if getoperation:
                
                #create first part
                frst_operations.append("(" + str(c_val1) + c_sig + str(c_val2)+ ")")
                
                #get solution
                frst_solution.append(float(eval(str(c_val1)+c_sig+str(c_val2))))
                
#create second part
for c_o in frst_operations:
    
    for c_sig in ["-","+"]:
    
        for c_val1 in range(1,10):
            
            getoperation=True
            
            #not negative or zero
            if eval(c_o + c_sig + str(c_val1))<=0:
                getoperation=False

            #form the operations
            if getoperation==True:
                
                #create second part
                operations.append(c_o + " " + c_sig + " " + str(c_val1))
                
                #get solution
                scnd_solution.append(eval(c_o + c_sig + str(c_val1)))
rnd.shuffle(operations)

#letters only shuffle in the loop below
letters=["F","P","Q","J","H","K","T","S","N","R","Y","L"]
o_dur=10000
d_dur=800

#determine the "span" of the block, and shuffel these each time
nblocks=[3,4,5,6,7,8,9] 
rnd.shuffle(nblocks)


# START [so you can give exp input]
#------------------------------------------------------------------------------
# Start
expyriment.control.start(skip_ready_screen=True)

#subject codes 101,201,301 etc are run as 001 [according to the counterbalancing sheet]
if task.subject < 10:
    SUBJ_CODE = "SUBJ00" + str(task.subject)
elif task.subject < 100:
    SUBJ_CODE = "SUBJ0" + str(task.subject)
else:
    SUBJ_CODE = "SUBJ0" + str(task.subject)[1:]
    
# DESIGN [experiment/task, blocks, trials, stimuli]
#------------------------------------------------------------------------------
# Create design (blocks and trials)
# Create stimuli (and put them into trials)
# Create input/output devices (like button boxes etc.)

# Loop over blocks 
for c_blocks in nblocks:    
    
    block = expyriment.design.Block("Block"+str(c_blocks))
    
    #shuffel letters each block
    rnd.shuffle(letters)    

    # Create Design, Loop over trials
    for c_trials in range(c_blocks):
                    
        #trial [define properties]
        trial =  expyriment.design.Trial()
        
        #load letter as a stimulus
        trial.set_factor("letters",letters[c_trials]) 
        d_stim = expyriment.stimuli.TextLine(text=str(letters[c_trials]),text_colour=[0,0,0],text_size=font_size)    
        d_stim.preload()
            
        #randomly determine the answer correct/incorrect of the operation
        corr=rnd.randint(0,1)
        if corr == 1:
            trial.set_factor("solution",1) 
            completeoperation=operations[0] + " = " + str(int(eval(operations[0])))
        
        elif corr == 0:
            trial.set_factor("solution",0) 
            
            #create wrong solution
            newsolution=0
            while newsolution<=0:
                newsolution=int(eval(operations[0]))+rnd.randint(-9,9)

            completeoperation=operations[0] + " = " +str(newsolution)   
        
        trial.set_factor("operation",completeoperation)

        #load operation as a stimulus
        o_stim = expyriment.stimuli.TextScreen("",text=completeoperation+"\n \n <Incorrect>                       <Correct>",
                                               text_colour=[0,0,0],text_size=font_size,position=(0,text_pos))
        o_stim.preload()
        
        #remove it from the list [never use same operation twice]
        operations.remove(operations[0]) 
        
        # Add stim to trial and trial to block
        trial.add_stimulus(o_stim)
        trial.add_stimulus(d_stim)
        block.add_trial(trial)
    
    # Add block to task
    task.add_block(block)

# Other stimuli
fixcross = expyriment.stimuli.FixCross(colour=(0,0,0))                      # default fixation cross
fixcross.preload()
blank = expyriment.stimuli.BlankScreen()                                        # blankscreen
blank.preload()

# Function waits for a duration while logging key presses
def wait(dur):
    task.keyboard.clear()
    task.clock.reset_stopwatch()
    while task.clock.stopwatch_time < int(frame * int(round((dur) / frame, 5))) - 2:
        task.keyboard.check(keys=responsekeys)


# Instructions
instructionspractice=[]
instructionspractice.append(" \n \
In this experiment you will try to memorize letters you see on the screen while  \n \
you also solve simple math problems. In the next few minutes, you will have some  \n \
practice to get you familiar with how the experiment works. We will begin by  \n \
practicing the letter part of the experiment.  \n \
\n \
When you have typed all the letters, and they are in the correct order, hit the ENTER \n \
If you make a mistake, you can use the BACKSPACE button to correct your answer. \n \
\n \
Remember, it is very important to get the letters in the same order as you see \n \
them.  \n \
Please ask the experimenter any questions you may have at this time. \n \
")

instructionspractice.append(" \n \
Now you will practice doing the math part of the experiment. \n \
A math problem will appear on the screen, like this: \n \
\n \
(6/2)+1=4 > is a correct solution \n \
(8/2)+1=4 > is an incorrect solution \n \
\n \
When you think the solution is correct use the [RIGHT] arrow \n \
When you think the solution is incorrect use the [LEFT] arrow \n \
\n \
As soon as you see the math problem, you should compute the correct answer and \n \
give your response . \n \
\n \
It is very important that you get the math problems correct.  It is also important \n \
that you try and solve the problem as quickly as you can. \n \
Please ask the experimenter any questions you may have at this time. \n \
")

instructionspractice.append(" \n \
Now you will practice doing both parts of the experiment at the same time. \n \
In the next practice set, you will be given one of the math problems.  Once \n \
you make your decision about the math problem, a letter will appear on the screen.  \n \
Try and remember the letter. \n \
\n \
After the letter goes away, another math problem will appear, and then another \n \
letter. At the end of each set of letters and math problems, a recall screen will \n \
appear. Try your best to get the letters in the correct order. \n \
\n \
It is important to work quickly and accurately on the math.  Make sure you know the\n \
answer to the math problem before responding.  \n \
You will not be told if your answer to the math problem is correct. \n \
After the recall screen, you will be given feedback about your performance \n \
regarding both the number of letters recalled and the percent correct on \n \
the math problems. This will only happen for the practice session not during the \n \
task. Please ask the experimenter any questions you may have at this time. \n \
")
instructions=[]
instructions.append(" \n \
That is the end of the practice. \n \
The real trials will look like the practice trials you just completed. \n \
First you will get a math problem to solve, then a letter to remember.  \n \
When you see the recall screen, type the letters in the order presented.   \n \
You can \n \
always correct your answer with BACKSPACE. \n \
\n \
Some sets will have more math problems and letters than others. \n \
It is important that you do your best on both the math problems and the letter \n \
recall parts of this experiment. \n \
Remember on the math you must work as quickly and accuractly as possible. \n \
If you have any questions, you can ask them now. \n \
")

# RUN
#------------------------------------------------------------------------------

# Check subject code
expyriment.stimuli.TextLine(text="You are running: " + str(task.subject) + " " + WHICH_RUN, 
                            text_colour=[0,0,0]).present()
task.keyboard.wait(experimenterkey)

#practise
letterspractice=["F","P","Q","J","H","K","T","S","N","R","Y","L","F","P"]
operationspractice=[
"(1*2) + 1 =  3",
"(2/1) - 1 =  2",
"(7*3) - 3 =  18",
"(4*3) + 4 =  18",
"(3/3) + 2 =  6",
"(2*6) - 4 =  8",
"(4*5) - 5 =  12",
"(4*2) + 6 =  14",
"(4/4) + 7 =  8",
"(8*2) - 8 =  10",
"(2*9) - 9 =  9",
"(8/2) + 9 =  13",
"(6/3) + 1 =  3", 
"(9/3) - 2 =  1"]
blockspractice=[4,4,4,3,3]
practicephases=['letters','operations','both','both','both']

# INSTRUCTIONS ONLY THE FIRST RUN
#-----------------------------------------------------------------------------
dopractice=True
if WHICH_RUN == 'run1':
    
    #loop over blocks [first time letters, second operations, third/fourth/fifth both]
    for c_blocks,n_block in enumerate(practicephases):
        
        if c_blocks<len(instructionspractice):
            expyriment.stimuli.TextScreen("", instructionspractice[c_blocks], 
                                      text_colour=[0,0,0],
                                      text_size=font_size).present()
            task.keyboard.wait(experimenterkey)

        #pauze
        fixcross.present()
        wait(2000)
        
        #loop over trials
        resp_correct=[]
        collectletter=[]
        for c_trials in range(blockspractice[c_blocks]):
            
            #operation
            if n_block == 'operations' or n_block == 'both':
                expyriment.stimuli.TextScreen("",text=operationspractice[0]+"\n \n <Incorrect>                       <Correct>",
                                                           text_colour=[0,0,0],text_size=font_size,position=(0,text_pos)).present()
                btn, rt = task.keyboard.wait(responsekeys,duration=o_dur)
                
                #check is operation is correct
                spltoperation=operationspractice[0].split("=")
                correctanswer=int(int(eval(spltoperation[0]))==int(spltoperation[1]))
                if btn:
                    whichbtn=[c for c,val in enumerate(responsekeys) if btn==val]          
                    resp_correct.append(int(correctanswer==int(whichbtn[0])))
                else:
                    whichbtn=[999]
                    resp_correct.append(0)
                operationspractice.pop(0)
            
            #fixation    
            fixcross.present()
            wait(d_dur)
            
            #letter
            if n_block == 'letters' or n_block == 'both':
                expyriment.stimuli.TextLine(text=str(letterspractice[0]),
                                            text_colour=[0,0,0],text_size=font_size).present()
                wait(d_dur)
                collectletter.append(letterspractice[0])
                letterspractice.pop(0)
            
            #fixation
            fixcross.present()
            wait(d_dur)
        
        #letter response
        if n_block == 'letters' or n_block == 'both':
            letterresp = expyriment.io.TextInput("Which letters did you see:",
                                                   message_colour=(0,0,0),
                                                   frame_colour=(0,0,0),
                                                   user_text_colour=(0,0,0),
                                                   message_text_size=font_size,
                                                   user_text_size=font_size)
            letterresp_out = letterresp.get() 
        
        #check answers
        if n_block == 'both':
            
            #check if answer is correct Letters
            letterresp_out=re.sub("[^a-zA-Z]+", "",letterresp_out) #get only letters
            letterresp_out=letterresp_out.upper()
            letterresp_out=list([i for i in str(letterresp_out)]) #seperate them
        
            tot_recalled=[]
            for c_ans in letterresp_out:
                tot_recalled.append(sum([int(c_ans==val) for c,val in enumerate(collectletter)]))
            tot_recalled=(sum(tot_recalled)/blockspractice[c_blocks])*100
            
            #check if answer is correct Operations
            tot_correct=(sum(resp_correct)/blockspractice[c_blocks])*100
            
            #Feedback
            expyriment.stimuli.TextScreen("", text="\n \
                                          You recalled: " + str(int(tot_recalled)) + "% of the letters. \n \
                                          You had: " + str(int(tot_correct)) + "% of the operations correct.",
                                            text_colour=[0,0,0],text_size=font_size,position=(0,text_pos)).present()
            task.keyboard.wait(experimenterkey)
            
            #end practice
            if int(tot_recalled)>=int((blockspractice[0]-1)/blockspractice[0]*100):
                dopractice=False
            if int(tot_correct)>=int((blockspractice[0]-1)/blockspractice[0]*100):
                dopractice=False
    
        if dopractice==False:
            break

    # INSTRUCTIONS FOR THE REAL TASK
    #-----------------------------------------------------------------------------
    for i in instructions:
        expyriment.stimuli.TextScreen("", i, 
                                      text_colour=[0,0,0],
                                      text_size=font_size).present()
        task.keyboard.wait(experimenterkey)
    
    #starttime
    task.data.add(["starttime",task.clock.time]) 


# RUN THE TASK
#-----------------------------------------------------------------------------

#preperation screen
fixcross.present()
wait(5000)

o_collect_cor=[]
d_collect_cor=[]
# Loop over trials/blocks
for block in task.blocks: 
    
    collectletters=[]
    
    for trial in block.trials:
    
        #operation
        trial.stimuli[0].present()
        btn, rt = task.keyboard.wait(responsekeys,duration=o_dur)
        
        #check if answer is correct
        if btn:
            whichbtn=[c for c,val in enumerate(responsekeys) if btn==val]          
            resp_correct=int(trial.get_factor("solution")==int(whichbtn[0]))
        else:
            whichbtn=[999]
            resp_correct=0

        
        #log
        o_collect_cor.append(resp_correct)
        task.data.add([WHICH_RUN,
                       "operation",
                       task.clock.time,
                       trial.get_factor("operation"),
                       trial.get_factor("solution"),                   
                       whichbtn[0],
                       resp_correct,
                       rt])
    
        
        #letter
        fixcross.present()
        wait(d_dur)
        
        trial.stimuli[1].present()
        collectletters.append(trial.get_factor("letters"))
        task.data.add([WHICH_RUN,"letters",task.clock.time,trial.get_factor("letters")]) 
        wait(d_dur)
        
        fixcross.present()
        wait(d_dur)
        
    #letter response
    letterresp = expyriment.io.TextInput("Which letters did you see:",
                                           message_colour=(0,0,0),
                                           frame_colour=(0,0,0),
                                           user_text_colour=(0,0,0),
                                           message_text_size=font_size,
                                           user_text_size=font_size)
    letterresp_out = letterresp.get()
    
    #check if answer is correct
    letterresp_out=re.sub("[^a-zA-Z]+", "",letterresp_out) #get only letters
    letterresp_out=letterresp_out.upper()
    letterresp_out=list([i for i in str(letterresp_out)]) #seperate them
    
    tot_recalled=[]
    for c_ans in letterresp_out:
        tot_recalled.append(sum([int(c_ans==val) for c,val in enumerate(collectletters)]))
    tot_recalled=sum(tot_recalled)

    #log    
    task.data.add([WHICH_RUN,"sum correct",collectletters,letterresp_out,len(collectletters)==tot_recalled]) 
    if len(collectletters)==tot_recalled:
        d_collect_cor.append(len(collectletters))
    else:
        d_collect_cor.append(0)        
    
    #fix
    fixcross.present()
    wait(2000)
    
 #end   
task.data.add(["% correct operations",sum(o_collect_cor)/sum(nblocks)*100]) 
task.data.add(["WM span score",sum(d_collect_cor)]) 

#endtime
task.data.add(["endtime",task.clock.time]) 
expyriment.control.end()
