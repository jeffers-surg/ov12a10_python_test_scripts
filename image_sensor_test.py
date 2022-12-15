import os
import time
import sys
import subprocess

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

ref_clock = 24E6


def write_i2c(register, value):
	cmd_str="sudo i2cset -y -f {} {} {} {} {} i".format(i2c_device, i2c_address, hex((register >> 8) & 0xff), hex(register & 0xff), hex(value))
	#print(cmd_str)
	os.system(cmd_str)

def read_i2c(register):
	cmd_str="sudo i2cset -y -f {} {} {} {} && sudo i2cget -y -f {} {}".format(i2c_device, i2c_address, hex((register >> 8) & 0xff), hex(register & 0xff), i2c_device, i2c_address)
	#print(cmd_str)
	#ret_str=os.system(cmd_str)
	ret_str = subprocess.check_output(cmd_str, shell=True)
	ret_str = ret_str.decode("utf-8")
	return int(ret_str.replace("\n",""), 16)

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

pll1_reg_array = [0x0307, 0x0300, 0x0301, 0x0302, 0x0303, 0x0304, 0x0305, 0x3020, 0x3106]
prediv0_0307 = {"0x0": 1, "0x1": 2}
prediv_0300 = {"0x0": 1, "0x1": 1.5,"0x2": 2,"0x3": 2.5,"0x4": 3,"0x5": 4,"0x6": 6,"0x7": 8}
mipi_div_0303 = {"0x0": 1, "0x1": 2, "0x2": 3, "0x3": 4}
pix_bit_div_0304 = {"0x0": 4, "0x1": 5}
sys_bit_div_0305 = {"0x0": 4, "0x1": 5}
pll_pclk_div_3020 = {"0x0": 1, "0x1": 2}
sys_clk_div_3106 = {"0x0": 1, "0x1": 2, "0x2": 4, "0x3": 8}

def calculate_clock_values():


	#reg_vals = [0x00, 0x01, 0x00, 0x32, 0x00, 0x00, 0x01, 0x9b, 0x15]

	reg_vals = []
	for i in range(len(pll1_reg_array)):
		reg_vals.append(read_i2c(pll1_reg_array[i]))
		print("{}: {}".format(hex(pll1_reg_array[i]), hex(reg_vals[i])))

	prediv0_div = prediv0_0307[hex(reg_vals[0] & 0x1)]

	prediv_div = prediv_0300[hex(reg_vals[1] & 0x7)]

	multiplier = ((reg_vals[2] & 0x3) << 8) + (reg_vals[3] & 0xff)

	mipi_div = mipi_div_0303[hex(reg_vals[4] & 0x3)]

	pix_bit_div = pix_bit_div_0304[hex(reg_vals[5] & 0x1)]

	sys_bit_div = sys_bit_div_0305[hex(reg_vals[6] & 0x1)]

	pll_pclk_div = pll_pclk_div_3020[hex((reg_vals[7] >> 3) & 0x1)]

	sys_clk_div = sys_clk_div_3106[hex((reg_vals[8] >> 2) & 0x3)]

	mipi_phy_clock = (ref_clock * multiplier ) / (prediv0_div * prediv_div * mipi_div)
	mipi_pclk = (ref_clock * multiplier) / (prediv0_div * prediv_div * mipi_div * pix_bit_div * pll_pclk_div)
	sclk = (ref_clock * multiplier) / (prediv0_div * prediv_div * mipi_div * sys_bit_div* sys_clk_div)

	print("MIPI PHY CLOCK: ", mipi_phy_clock)
	print("MIPI PIXEL CLOCK: ", mipi_pclk)
	print("SCLK: ", sclk)
	
	return 

_fns = globals().copy()
for k, v in list(_fns.items()):
	if k.startswith("_") or not hasattr(v, "__call__") or getattr(v, " __doc__", None) is not None:
		_fns.pop(k)

if __name__ == "__main__":
	if len(sys.argv) > 1:
		for arg in sys.argv[1:]:
			args = []
			name, _colon, args_str = arg.partition(":")
			if args_str:
				args = args_str.split(',')
			if name not in _fns:
				print("Error: unknown function '{}'".format(name))
				help()
				break
			print("Running", name, "with args", args)
			_fns[name](*args)
	else:
		help()


