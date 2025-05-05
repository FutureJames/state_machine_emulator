import csv
import sys

# Usage: python digital_to_pin_program.py digital.csv pin_program_out
# each cycle of the pio for rp2040 is -0.000000008 seconds (8 nanoseconds)
# this is based on the clockspeed of the rp2040 which is 125 MHz (1 / 125,000,000 Hz = 8 ns)

def convert_digital_to_pin_program(input_csv, output_file, pico_version):
    if pico_version == '1':
        # For Pico 1, the clock speed is 125 MHz
        clock_speed = 125
    elif pico_version == '2':
        # For Pico 2, the clock speed is 250 MHz
        clock_speed = 150
    elif pico_version > '10':
        # Otherwise just use the input as the given clockspeed
        clock_speed = int(pico_version)

    cycle_duration = 1 / (clock_speed*1000000)  # 8 nanoseconds per cycle

    with open(input_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        pins = [col for col in reader.fieldnames if col != 'Time [s]']
        
        # Write header
        with open(output_file, 'w') as out:
            out.write('# timestamp, pinnumber, state\n')
            out.write('# timestamp 0 is the first clock\n')
            out.write('# pinnumber = all means all GPIOs\n')
            out.write('# pinnumber = GPIOx means pin x\n')
            out.write('# state = -1 means not driven externally\n')
            out.write('# state = 0 means driven low externally\n')
            out.write('# state = 1 means driven high externally\n')
            out.write(f'# clockspeed = {clock_speed} MHz\n')
            out.write('0, all, -1\n')

            prev = {pin: None for pin in pins}
            time0 = None
            for row in reader:
                t = float(row['Time [s]'])
                if time0 is None:
                    time0 = t
                # Each timestamp in pin_program represents 8 nanoseconds (0.000000008 seconds)
                # Calculate the number of cycles since the first clock

                cycle = int(round((t - time0) / cycle_duration))
                for pin in pins:
                    state = int(row[pin])
                    if prev[pin] is None or state != prev[pin]:
                        out.write(f'{cycle}, {pin}, {state}\n')
                        prev[pin] = state

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python digital_to_pin_program.py digital.csv pin_program_out pico_version')
        sys.exit(1)
    convert_digital_to_pin_program(sys.argv[1], sys.argv[2], sys.argv[3])
