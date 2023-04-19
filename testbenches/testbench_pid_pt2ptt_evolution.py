# Any copyright is dedicated to the Public Domain.
# https://creativecommons.org/publicdomain/zero/1.0/

#imports
from pyconsys.Control import Control
from pyconsys.PIDControl import PIDControl
from pyconsys.PT2 import PT2
from pyconsys.DelayControl import DelayControl
from pyconsys.Rating import Rating
from pyconsys.Evopid import Evopid
import matplotlib.pyplot as plt
import time

#parameter used for the pt2 and the ptt
pt2_a2 = 0.2
pt2_a1 = 0.1
pt2_a0 = 1
pt2_b0 = 1
delaytime = 15
delay_control = DelayControl(delaytime)

pid_control = PIDControl(0, 0, 0)
pt2 = PT2(pt2_a2, pt2_a1, pt2_a0, pt2_b0)
rating = Rating()

# define a function to get the fitness score of a pid triple

def calculate(pid_lst):
    p = pid_lst[0]
    i = pid_lst[1]
    d = pid_lst[2]

    time_steps = [x * Control.DELTA_T for x in range(0, 3000)]
    w_lst = [1 for x in time_steps]
    x_lst = []
    v_lst = []
    e_lst = []
    y_lst = []
    x = 0

    pid_control.update_params(p, i, d)
    pt2.reset()                         #reset pt2
    delay_control.reset(delaytime)      #reset ptt with delaytime

    for w in w_lst:
        e = w - x
        y = pid_control.get_xa(e)
        v = delay_control.get_xa(y)     #v is the output of the delay from the ptt
        x = pt2.get_xa(v)               #v is used for the calculation of x in pt2 --> ptt and pt2 in series
        e_lst.append(e)
        v_lst.append(v)
        y_lst.append(y)
        x_lst.append(x)

    r = rating.get_update_rating(x_lst, w)
    return r

#####################################################
# start the evolution


time_stamp = time.time()
print("Evolution is running. Please wait...")
# The constructor needs the fitness function as a callback
evo = Evopid(calculate)
# start the evolution
best_pid, best_score, plot_score_mean = evo.run()

tm = time.time() - time_stamp

#plot and show of the evolving process
plt.title("evolution score")
plt.plot(plot_score_mean, label="mean score (generation)")
plt.show()
####################################################
# plot the fittest control loop
time_steps_fin = [x * Control.DELTA_T for x in range(0, 3000)]
w_lst_fin = [1 for x in time_steps_fin]
x_lst_fin = []
v_lst_fin = []
e_lst_fin = []
y_lst_fin = []
x = 0
best_pid_p = best_pid[0]
best_pid_i = best_pid[1]
best_pid_d = best_pid[2]

pid_control.update_params(best_pid_p, best_pid_i, best_pid_d)
pt2.reset()                         #reset pt2
delay_control.reset(delaytime)      #reset ptt with delaytime

for w in w_lst_fin:
    e = w - x
    y = pid_control.get_xa(e)
    v = delay_control.get_xa(y)     #v is the output of the delay from the ptt
    x = pt2.get_xa(v)               #v is used for the calculation of x in pt2 --> ptt and pt2 in series
    x_lst_fin.append(x)
    e_lst_fin.append(e)
    y_lst_fin.append(y)
    v_lst_fin.append(v)

#print of the best score and the used time
print("##### best score: {:7.2f}".format(best_score))
print("##### evolution time: {:7.2f}".format(tm))

#plot of the best evolution
txt_pid = "PID with P = {}, I = {}, D = {}".format(best_pid_p, best_pid_i, best_pid_d)
txt_pt2 = "PT2 with a2 = {}, a1 = {}, a0 = {}, b0 = {}".format(pt2_a2, pt2_a1, pt2_a0, pt2_b0)
txt_ptt = "PTt with Delay = {}".format(delaytime)
plt.plot(time_steps_fin, w_lst_fin, label="w")
plt.plot(time_steps_fin, x_lst_fin, label="x")
#plt.plot(time_steps_fin, y_lst_fin, label="y")
#plt.plot(time_steps_fin, e_lst_fin, label="e")
#plt.plot(time_steps_fin, v_lst_fin, label="v")
plt.grid()
plt.minorticks_on()
plt.grid(which='major', linestyle='-', linewidth='0.5')
plt.grid(which='minor', linestyle=':', linewidth='0.3')

plt.xlabel('k in hundreds')
plt.title("PT2 + PTt control loop with evolution PID")
plt.text(1.5, 0.3, txt_pid, bbox=dict(facecolor='white', alpha=0.5))
plt.text(1.5, 0.0, txt_pt2, bbox=dict(facecolor='white', alpha=0.5))
plt.text(1.5, -0.3, txt_ptt, bbox=dict(facecolor='white', alpha=0.5))
plt.legend()
plt.ylim(top=2, bottom=-1)
plt.show()
