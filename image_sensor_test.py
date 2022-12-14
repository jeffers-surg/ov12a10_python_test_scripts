import os
import time


exp_reg_array = [0x3500,0x3501,0x3502]
group_hold_reg = 0x3208
group_hold_manual_launch_reg = 0x320D
i2c_device=2
i2c_address='0x42'

group_hold_group=0
group_hold_start_flag = 0x0
group_hold_end_flag = 0x1
group_hold_delay_launch_flag = 0x2
group_hold_quick_launch_flag = 0x3

standby_reg=0x100

image_flip_reg=0x3820

binning_enable_reg=0x3820

hbin_ctrl_reg = 0x4501



def write_i2c(register, value):
	cmd_str="sudo i2cset -y -f {} {} {} {} {} i".format(i2c_device, i2c_address, hex((register >> 8) & 0xff), hex(register & 0xff), hex(value))
	#print(cmd_str)
	os.system(cmd_str)

def read_i2c(register):
	cmd_str="sudo i2cset -y -f {} {} {} {} && sudo i2cget -y -f {} {}".format(i2c_device, i2c_address, hex((register >> 8) & 0xff), hex(register & 0xff), i2c_device, i2c_address)
	#print(cmd_str)
	ret_str=os.system(cmd_str)
	#ret_str=0x0
	#print(ret_str)
	return ret_str

def get_exposure():
	print("Get exposure")
	exposure_val=0
	for i in range(len(exp_reg_array)):
		exposure_val = exposure_val + (int(read_i2c(exp_reg_array[i])) << 8*i)
	#print(exposure_val)

def set_exposure(exp_input):

	print("Set exposure")
	exp_val=[0x0, 0x0, 0x0]
	exp_val[0] = ((exp_input >> 16) & 0x3)
	exp_val[1] = ((exp_input >> 8) & 0xff)
	exp_val[2] = (exp_input & 0xff)

	for i in range(len(exp_reg_array)):
		write_i2c(exp_reg_array[i], exp_val[i])

def exposure_test():
	for i in range(0,0xA000,0x1000):
		#set the group hold id
		#group_hold_set_id(group_hold_group)

		#Group hold start
		#group_hold_start()

		#Try to set the exposure settings
		print("Setting exposure to ", i)
		set_exposure(i)

		#End the group hold
		#group_hold_end()

		#Launch mode 1:  Quick manual launch
		#group_hold_manual_launch()

		#group_hold_quick_launch()

		time.sleep(2)

		get_exposure()

def group_hold_set_id(group_num):
	reg_val = read_i2c(group_hold_reg)
	reg_val = (reg_val & 0xff00)
	reg_val = reg_val | (group_num & 0xff)
	write_i2c(group_hold_reg, reg_val)

def group_hold_start():
	print("Group hold start")
	reg_val = read_i2c(group_hold_reg)
	reg_val = (reg_val & 0x00ff)
	reg_val = reg_val | (group_hold_start_flag << 4)
	write_i2c(group_hold_reg, reg_val)
	print(read_i2c(group_hold_reg))

def group_hold_end():
	print("Group hold end")
	reg_val = read_i2c(group_hold_reg)
	reg_val = (reg_val & 0x00ff)
	reg_val = reg_val | (group_hold_end_flag << 4)
	write_i2c(group_hold_reg, reg_val)
	print(read_i2c(group_hold_reg))

def group_hold_delay_launch():
	print("Group hold delay launch")
	reg_val = read_i2c(group_hold_reg)
	reg_val = (reg_val & 0x00ff)
	reg_val = reg_val | (group_hold_delay_launch_flag << 4)
	write_i2c(group_hold_reg, reg_val)
	print(read_i2c(group_hold_reg))

def group_hold_quick_launch():
	print("Group hold quick launch")
	reg_val = read_i2c(group_hold_reg)
	reg_val = (reg_val & 0x00ff)
	reg_val = reg_val | (group_hold_quick_launch_flag << 4)
	write_i2c(group_hold_reg, reg_val)
	print(read_i2c(group_hold_reg))

def group_hold_manual_launch():
	print("Group hold manual launch")
	write_i2c(group_hold_manual_launch_reg, 0x00)
	print(read_i2c(group_hold_manual_launch_reg))


def flip_image(flip_horizontal, flip_vertical):
	reg_val = 0x0

	if flip_horizontal == True:
		reg_val = reg_val | (0x1 << 3)
	if flip_vertical == True:
		reg_val = reg_val | (0x1 << 4)

	write_i2c(image_flip_reg, reg_val)

def flipping_test():
	#Demonstrate flipping the image
	standby_enter()
	flip_image(True, True)
	standby_exit()

	time.sleep(4)

	standby_enter()
	flip_image(True, False)
	standby_exit()

	time.sleep(4)

	standby_enter()
	flip_image(False, False)
	standby_exit()

	time.sleep(4)

	standby_enter()
	flip_image(True, True)
	standby_exit()


def standby_enter():
	write_i2c(standby_reg, 0x00)

def standby_exit():
	write_i2c(standby_reg, 0x01)


def enable_binning(hbin,vbin):
	reg_val = 0x0

	if hbin == True:
		reg_val = reg_val | (0x1 << 1)
	if vbin == True:
		reg_val = reg_val | (0x1)

	write_i2c(binning_enable_reg, reg_val)
	
def hbin_ctrl_set(r_hbin4_opt, r_hbin2_opt):
	#[5:4] r_hbin4_opt
	r_hbin4_opt_str = ["00: Average of 4 pixels",
						"01: Debug",
						"10: Select first bin2 pixel",
						"11: Select last bin2 pixel"]
	#[3:2] r_hbin2_opt
	r_hbin2_opt_str = ["00: Average",
						"01: Debug",
						"10: Select the first pixel",
						"11: Select the last pixel"]



	if (r_hbin4_opt > 0x3) or (r_hbin4_opt < 0x0):
		print("Error:  r_hbin4_opt out of range")
		return

	if (r_hbin2_opt > 0x3) or (r_hbin2_opt < 0x0):
		print("Error:  r_hbin2_opt out of range")
		return

	print("r_hbin4_opt", r_hbin4_opt_str[r_hbin4_opt])
	print("r_hbin2_opt", r_hbin2_opt_str[r_hbin2_opt])
	
	reg_val = 0x0

	reg_val = reg_val | (r_hbin4_opt << 4)
	reg_val = reg_val | (r_hbin2_opt << 2)

	write_i2c(hbin_ctrl_reg, reg_val)

def test_binning():
	enable_binning(False, False)

	for i in range(0,4):
		for j in range(0,4):
			standby_enter()

			print("#######MODE#######")
			hbin_ctrl_set(i, j)
			standby_exit()
			time.sleep(5)
