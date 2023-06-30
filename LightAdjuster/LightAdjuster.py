import argparse

def adjust_value(line, value_name, percentage, log_changes, i):
    if f'float {value_name} =' in line:
        parts = line.split('=')
        old_value = float(parts[1].strip())
        new_value = old_value * percentage
        new_line = f'{parts[0]}= {new_value}\n'
        if log_changes:
            log_line = f'Line {i + 1}: {line.strip()} -> {new_line.strip()}'
            print(log_line)
            with open('changes.log', 'a') as log:
                log.write(log_line + '\n')
        line = new_line
        return line, True
    return line, False

def adjust_file(file_path, start_line=1, log_changes=False, adjust_intensity=False, adjust_color_temperature=False, percentage=None):
    with open(file_path, 'r') as file:
        data = file.readlines()
    lines_changed = 0
    with open(file_path, 'w') as file:
        for i, line in enumerate(data):
            if i + 1 >= start_line:
                if adjust_intensity:
                    line, changed = adjust_value(line, 'intensity', percentage, log_changes, i)
                    if changed:
                        lines_changed += 1
                if adjust_color_temperature:
                    line, changed = adjust_value(line, 'colorTemperature', percentage, log_changes, i)
                    if changed:
                        lines_changed += 1
            file.write(line)
    print(f'Completed! {lines_changed} lines changed.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Adjust the intensity and/or color temperature values in a file.')
    parser.add_argument('file_path', type=str, help='The path to the file to modify.')
    parser.add_argument('-s', '--start-line', type=int, default=1, help='The line number to start modifying at.')
    parser.add_argument('-l', '--log', action='store_true', help='Whether to print a log of the changed lines.')
    parser.add_argument('-ai', '--adjust-intensity', action='store_true', help='Whether to adjust the intensity value.')
    parser.add_argument('-act', '--adjust-color-temperature', action='store_true', help='Whether to adjust the color temperature value.')
    parser.add_argument('-p', '--percentage', type=float, required=True, help='The percentage to adjust the value by.')
    args = parser.parse_args()
    adjust_file(args.file_path, args.start_line, args.log, args.adjust_intensity, args.adjust_color_temperature, args.percentage)
